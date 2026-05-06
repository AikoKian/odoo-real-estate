from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare

class EstateProperty(models.Model):
    # _name es el identificador único del modelo en Odoo
    _name = "estate.property"
    _description = "Real Estate Property"
    _inherit = "estate.property"

    # Campos de la base de datos
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date()
    
    # Campo Active
    active = fields.Boolean(default=True)

    expected_price = fields.Float(required=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ]
    )

    # Campos Relacionales
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one("res.users", string="Salesperson")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    # Campo calculado
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area")
    # Funcion para el campo calculado
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    # Funcion Onchange (SE ejecuta en vivo al hacer click)
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False # Vacia los campos de seleccion

    # Nueva relacion hacia Ofertas
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    # Nuevo campo calculado para el mejor precio
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")
    # Funcion para calcular el mejor precio
    def _compute_best_price(self):
        for record in self:
            # Si hay ofertas, sacamos el precio maximo. Si no, es 0.
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0
    
    # Nuevo campor para manejar el estado
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted','Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        required=True,
        copy=False,
        default='new',
        string="Status"
    )
    # Logica para los botones de la propiedad
    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("A canceled property cannot be sold.")
            record.state = 'sold'
        return True
    
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be canceled.")
            record.state='canceled'
        return True
    
    # Restriccion SQL, precio esperado > 0, precio de venta puede ser 0 hasta que se acepte una oferta.
    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)', 'The selling price must be positive.')
    ]

    # Funcion para Logica de Negocio
    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            # Solo validamos si hay un precio de venta mayor a 0
            if record.selling_price > 0:
                # Calculamos el 90% del precio esperado
                minimun_price = record.expected_price * 0.90

                # Comparamos si el precio de veneta es menor al minimo aceptable
                if float_compare(record.selling_price, minimun_price, precision_digits=2) < 0:
                    raise ValidationError("The selling price cannot be lower tha 90'%' of the expected price.")
                
    @api.model
    def get_dashboard_stats(self):
        """
        Calcula las métricas principales en una sola consulta al servidor.
        Retorna un diccionario con los conteos por estado.
        """
        return {
            'sold': self.search_count([('state', '=', 'sold')]),
            'new': self.search_count([('state', '=', 'new')]),
            'canceled': self.search_count([('state', '=', 'canceled')]),
        }
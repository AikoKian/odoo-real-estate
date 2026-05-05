from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    # ID unico del modelo en Odoo:
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc" # Ordena por precio descendente

    # Campos de la base de datos
    # Campo many2one, ofertas para propiedad
    price = fields.Float(string="Price")
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False,
        string="Status"
    )
    partner_id = fields.Many2one("res.partner", required=True, string="Partner")
    property_id = fields.Many2one("estate.property", required=True, string="Property")

    # Campos Calculados con Inverse
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(
        compute="_compute_date_deadline", 
        inverse="_inverse_date_deadline", 
        string="Deadline"
    )

    # Funcion para calcular Fecha Limite. Fecha de Creacion + Validez (dias) -> Inverse
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            # Si la oferta es nueva y aún no tiene fecha de creación, usamos hoy
            date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            date = record.create_date.date() if record.create_date else fields.Date.today()
            # Si el usuario cambia la fecha, recalculamos los días de validez
            record.validity = (record.date_deadline - date).days

    # Funcion aceptar o rechazar
    def action_accept(self):
        for record in self:
            # Validamos si hay una oferta aceptada en esta propiedad
            if 'accepted' in record.property_id.offer_ids.mapped('status'):
                raise UserError("AN offer has already been accepted.")
            
            # Actualizamos la oferta y la propieda al mismo tiempo
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
        return True
    
    def action_refuse(self):
        for record in self:
            record.status = 'refused'
        return True
    
    # Restriccion a nivel SQL
    _sql_constraints = [
        ('check_price_positive', 'CHECK(price > 0)', 'The offer price must be strictly positive!')
    ]

    
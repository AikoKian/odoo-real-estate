from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    name = fields.Char(required=True)
    color = fields.Integer()

    # Restriccion SQL para nombres unicos
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)', 'The tag name must be unique!')
    ]
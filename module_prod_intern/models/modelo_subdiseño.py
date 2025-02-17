
from odoo import api,models,fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subdesign_prod = fields.Float(
        string='Subdiseño',
        help = "Subdiseño del producto"
    )
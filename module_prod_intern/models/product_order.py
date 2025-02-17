
from odoo import api , models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    net_weight = fields.Float(
        string="Peso Neto",
        help="Peso neto del producto en kg"
    )


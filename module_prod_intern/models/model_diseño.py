
from odoo import api,models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    design_prod = fields.Float(
        string="Diseño",
        help="Peso neto del producto en kg"
    )


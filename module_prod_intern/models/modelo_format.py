from odoo import api,models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    format_prod = fields.Float(
        string="Formato",
        help="Formato del producto"
    )
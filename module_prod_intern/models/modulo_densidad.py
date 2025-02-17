from odoo import api,models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    densidad_prod = fields.Float(
        string="Densidad",
        help="Densidad del producto"
    )
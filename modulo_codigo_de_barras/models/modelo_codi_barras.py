
from odoo import api , models , fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cod_barcode_prod = fields.Char(
        string="Codigo de barras",
        compute="_compute_barcode_prod",
        help = "Concatenacion diseño-subdiseño-formato-densidad"
    )

    @api.depends('design_prod', 'subdesign_prod', 'format_prod', 'densidad_prod')
    def _compute_barcode_prod(self):

        cod_barcode_prod = (f"{self.design_prod}-{self.subdesign_prod}-{self.format_prod}-{self.densidad_prod}")
        self.cod_barcode_prod = cod_barcode_prod

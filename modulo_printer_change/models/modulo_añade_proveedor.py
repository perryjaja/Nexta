from odoo import api, models, fields

class StokePicking(models.Model):
    _inherit = 'stock.picking'

    prov_albaran = fields.Integer(
        string="Albarán proveedor nº",
        help="Numero de albaran"
    )

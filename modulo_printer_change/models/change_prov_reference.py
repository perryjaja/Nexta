from odoo import api, models, fields

class PurchaseTemplate(models.Model):
    _inherit = 'purchase.order'

    prov_purchase = fields.Integer(
        string="Oferta proveedor nº",
        help="Oferta de proveedor"
    )
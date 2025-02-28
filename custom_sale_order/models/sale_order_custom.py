
from odoo import api , models , fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    transporter_num= fields.Char(string='Numero de Transporte')


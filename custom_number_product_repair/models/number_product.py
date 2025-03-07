
from odoo import api , models , fields

class NumberProd (models.Model):
    _inherit = 'repair.order'

    num_prod = fields.Char(String='Numero del pedido')
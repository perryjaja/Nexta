
from odoo import api , models , fields

class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'

    transporter_num_sale= fields.Char(string='Numero de Transporte')

class SaleOrderLineCustom(models.Model):
    _inherit = 'sale.order.line'

    transporter_num_sale_line= fields.Char(string='Numero de Transporte' , related='order_id.transporter_num_sale')


class BillOrderCustom(models.Model):
    _inherit = 'account.move.line'

    transporter_num_bill= fields.Char(string='Numero de Transporte' , related='sale_line_ids.transporter_num_sale_line')



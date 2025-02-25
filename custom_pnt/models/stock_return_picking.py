# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        res = super().create_returns()
        picking_id= res['res_id']
        partner=self.picking_id.partner_id
        if picking_id and partner:
            picking = self.env['stock.picking'].browse(picking_id)
            picking.write({'partner_id': partner.id})
        return res


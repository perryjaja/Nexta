# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp


class ResPartner(models.Model):
    _inherit = "res.partner"

    pnt_payment_day_client = fields.Char(
        string="Payment day client"
    )
    pnt_payment_day_supplier = fields.Char(
        string="Payment day supplier"
    )

    def muestra_ranking_proveedores(self):
        action = self.env.ref("custom_pnt.pnt_partner_product_ranking_wizard_action")
        action = action.read()[0]
        action["context"] = {"active_id": self.id}
        return action

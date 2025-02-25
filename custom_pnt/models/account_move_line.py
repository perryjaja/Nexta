# -*- coding:utf-8 -*-
from odoo import models, api, fields, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pnt_punteo = fields.Boolean(
        string="Punteo",
        readonly=True,
    )

    def button_pnt_punteo(self):
        for record in self:
            record.pnt_punteo = not record.pnt_punteo

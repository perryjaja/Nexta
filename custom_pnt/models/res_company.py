# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _


class ResCompany(models.Model):
    _inherit = "res.company"

    pnt_base_metal_market_ids = fields.One2many(
        string=" Base Metal Market",
        comodel_name='pnt.base.metal',
        inverse_name='pnt_company_id'
    )


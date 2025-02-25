# -*- coding: utf-8 -*-
from odoo import models, fields, api


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     net_weight = fields.Integer(string='Net weight')
#     lst_price_lorente = fields.Float(string='Lst price Lorente')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    net_weight = fields.Integer(string='Net weight')
    lst_price_lorente = fields.Float(string='Lst price Lorente')


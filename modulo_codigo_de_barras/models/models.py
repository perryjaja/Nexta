# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class modulo_codigo_de_barras(models.Model):
#     _name = 'modulo_codigo_de_barras.modulo_codigo_de_barras'
#     _description = 'modulo_codigo_de_barras.modulo_codigo_de_barras'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


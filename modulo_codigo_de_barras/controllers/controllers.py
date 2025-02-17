# -*- coding: utf-8 -*-
# from odoo import http


# class ModuloCodigoDeBarras(http.Controller):
#     @http.route('/modulo_codigo_de_barras/modulo_codigo_de_barras', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo_codigo_de_barras/modulo_codigo_de_barras/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo_codigo_de_barras.listing', {
#             'root': '/modulo_codigo_de_barras/modulo_codigo_de_barras',
#             'objects': http.request.env['modulo_codigo_de_barras.modulo_codigo_de_barras'].search([]),
#         })

#     @http.route('/modulo_codigo_de_barras/modulo_codigo_de_barras/objects/<model("modulo_codigo_de_barras.modulo_codigo_de_barras"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo_codigo_de_barras.object', {
#             'object': obj
#         })


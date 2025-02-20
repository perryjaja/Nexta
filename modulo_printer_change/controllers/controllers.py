# -*- coding: utf-8 -*-
# from odoo import http


# class ModuloPrinterChange(http.Controller):
#     @http.route('/modulo_printer_change/modulo_printer_change', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo_printer_change/modulo_printer_change/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo_printer_change.listing', {
#             'root': '/modulo_printer_change/modulo_printer_change',
#             'objects': http.request.env['modulo_printer_change.modulo_printer_change'].search([]),
#         })

#     @http.route('/modulo_printer_change/modulo_printer_change/objects/<model("modulo_printer_change.modulo_printer_change"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo_printer_change.object', {
#             'object': obj
#         })


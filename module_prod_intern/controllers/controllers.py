# -*- coding: utf-8 -*-
# from odoo import http


# class ModuleTest(http.Controller):
#     @http.route('/module_test/module_test', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_test/module_test/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_test.listing', {
#             'root': '/module_test/module_test',
#             'objects': http.request.env['module_test.module_test'].search([]),
#         })

#     @http.route('/module_test/module_test/objects/<model("module_test.module_test"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_test.object', {
#             'object': obj
#         })


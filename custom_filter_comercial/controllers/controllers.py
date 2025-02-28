# -*- coding: utf-8 -*-
# from odoo import http


# class CustomFilterComercial(http.Controller):
#     @http.route('/custom_filter_comercial/custom_filter_comercial', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_filter_comercial/custom_filter_comercial/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_filter_comercial.listing', {
#             'root': '/custom_filter_comercial/custom_filter_comercial',
#             'objects': http.request.env['custom_filter_comercial.custom_filter_comercial'].search([]),
#         })

#     @http.route('/custom_filter_comercial/custom_filter_comercial/objects/<model("custom_filter_comercial.custom_filter_comercial"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_filter_comercial.object', {
#             'object': obj
#         })


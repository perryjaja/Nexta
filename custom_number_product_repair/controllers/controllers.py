# -*- coding: utf-8 -*-
# from odoo import http


# class CustomNumberProductRepair(http.Controller):
#     @http.route('/custom_number_product_repair/custom_number_product_repair', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_number_product_repair/custom_number_product_repair/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_number_product_repair.listing', {
#             'root': '/custom_number_product_repair/custom_number_product_repair',
#             'objects': http.request.env['custom_number_product_repair.custom_number_product_repair'].search([]),
#         })

#     @http.route('/custom_number_product_repair/custom_number_product_repair/objects/<model("custom_number_product_repair.custom_number_product_repair"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_number_product_repair.object', {
#             'object': obj
#         })


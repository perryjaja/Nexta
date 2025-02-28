# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPurchaseOrder(http.Controller):
#     @http.route('/custom_purchase_order/custom_purchase_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_purchase_order/custom_purchase_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_purchase_order.listing', {
#             'root': '/custom_purchase_order/custom_purchase_order',
#             'objects': http.request.env['custom_purchase_order.custom_purchase_order'].search([]),
#         })

#     @http.route('/custom_purchase_order/custom_purchase_order/objects/<model("custom_purchase_order.custom_purchase_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_purchase_order.object', {
#             'object': obj
#         })


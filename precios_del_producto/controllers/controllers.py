# -*- coding: utf-8 -*-
# from odoo import http


# class PreciosDelProducto(http.Controller):
#     @http.route('/precios_del_producto/precios_del_producto', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/precios_del_producto/precios_del_producto/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('precios_del_producto.listing', {
#             'root': '/precios_del_producto/precios_del_producto',
#             'objects': http.request.env['precios_del_producto.precios_del_producto'].search([]),
#         })

#     @http.route('/precios_del_producto/precios_del_producto/objects/<model("precios_del_producto.precios_del_producto"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('precios_del_producto.object', {
#             'object': obj
#         })


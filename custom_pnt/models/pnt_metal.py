# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _


class PntTypeMetal(models.Model):
    _name = "pnt.type.metal"
    _description = "pnt_type_metal"

    name = fields.Char(
        string="Type Metal"
    )


class PntBaseMetal(models.Model):
    _name = "pnt.base.metal"
    _description = "pnt_base_metal"

    pnt_company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company'
    )
    pnt_metal_id = fields.Many2one(
        string="Metal",
        comodel_name='pnt.type.metal'
    )
    pnt_base_metal = fields.Float(
        string='Base Metal'
    )

    def btn_update_price(self):
        product_tmpl_ids = self.env['product.template'].search([])
        product_ids = self.env['product.product'].search([])
        product_supplier_ids = self.env['product.supplierinfo'].search([])

        for product_supplier in product_supplier_ids:
            product_supplier.pnt_compute_price()

        for product in product_ids:
            product._compute_pnt_hechura_venta()
            product.btn_seller_price()
            product.pnt_compute_list_price()

        for template in product_tmpl_ids:
            template._compute_pnt_hechura_venta()
            template.btn_seller_price()
            template.pnt_compute_list_price()


class PntMetal(models.Model):
    _name = "pnt.metal"
    _description = "pnt_metal"

    name = fields.Char(
        string="Metal"
    )

class PntDesign(models.Model):
    _name = "pnt.design"
    _description = "pnt_design"

    name = fields.Char(
        string="Design"
    )
    pnt_product_category_id = fields.Many2one(
        string='Category',
        comodel_name='product.category'
    )


class PntSubdesign(models.Model):
    _name = "pnt.subdesign"
    _description = "pnt_subdesign"

    name = fields.Char(
        string="Subdesign"
    )
    pnt_product_category_id = fields.Many2one(
        string='Category',
        comodel_name='product.category'
    )


class PntFormat(models.Model):
    _name = "pnt.format"
    _description = "pnt_format"

    name = fields.Char(
        string="Format"
    )
    pnt_product_category_id = fields.Many2one(
        string='Category',
        comodel_name='product.category'
    )

class PntStones(models.Model):
    _name = "pnt.stones"
    _description = "pnt_stones"

    name = fields.Char(
        string="Stones"
    )

class PntDensity(models.Model):
    _name = "pnt.density"
    _description = "pnt_density"

    name = fields.Char(
        string="Density"
    )
    pnt_product_category_id = fields.Many2one(
        string='Category',
        comodel_name='product.category'
    )

# class PntSaleUnit(models.Model):
#     _name = "pnt.sale.unit"
#     _description = "pnt_sale_unit"
#
#     name = fields.Char(
#         string="Density"
#     )


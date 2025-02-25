# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('categ_id',
                 'categ_id.pnt_no_compute_sale_price')
    def _compute_obligatoriedad_precio(self):
        for record in self:
            if record.categ_id and record.categ_id.pnt_no_compute_sale_price:
                record.pnt_precio_obligatorio = True
            else:
                record.pnt_precio_obligatorio = False

    @api.depends('categ_id',
                 'categ_id.pnt_peso_neto_obligatorio')
    def _compute_obligatoriedad_peso(self):
        for record in self:
            if record.categ_id and record.categ_id.pnt_peso_neto_obligatorio:
                record.pnt_peso_obligatorio = True
            else:
                record.pnt_peso_obligatorio = False

    pnt_description_intern = fields.Char(
        string="Intern Descripcion",
        compute="_compute_pnt_description_intern",
        store=True
    )
    pnt_peso_neto = fields.Float(
        string='Net Weight'
    )
    pnt_quilataje = fields.Float(
        string='Quilataje',
        digits=(12, 2)
    )
    pnt_tipo_metal = fields.Many2one(
        string='Metal Type',
        comodel_name='pnt.type.metal'
    )
    pnt_metal = fields.Many2one(
        string='Metal',
        comodel_name='pnt.metal'
    )
    pnt_design = fields.Many2one(
        string='Design',
        comodel_name='pnt.design'
    )
    pnt_subdesign = fields.Many2one(
        string='Subdesign',
        comodel_name='pnt.subdesign'
    )
    pnt_format = fields.Many2one(
        string='Format',
        comodel_name='pnt.format'
    )
    pnt_stones = fields.Many2one(
        string='Stones',
        comodel_name='pnt.stones'
    )
    pnt_density = fields.Many2one(
        string='Density',
        comodel_name='pnt.density'
    )
    pnt_sale_unit = fields.Selection(
        string='Sale Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )
    pnt_escandallo = fields.Float(
        string='Escandallo'
    )
    pnt_hechura_venta = fields.Float(
        string='Hechura Venta',
        compute='_compute_pnt_hechura_venta',
        store=True
    )
    pnt_hechura_compra = fields.Float(
        string='Hechura Compra'
    )
    pnt_merma = fields.Float(
        string='Merma'
    )
    pnt_purchase_unit = fields.Selection(
        string='Purchase Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )
    pnt_categ_parent_id = fields.Many2one(
        string='Categ_parent',
        comodel_name='product.category',
        compute='_compute_categ_id'
    )
    list_price = fields.Float(
        string='List Price',
        compute='pnt_compute_list_price',
        store=True
    )
    pnt_list_price = fields.Float(
        string='List Price Lorente',
    )
    pnt_escandallo_manual = fields.Boolean(
        string='Escandallo Manual'
    )
    pnt_detail = fields.Char(
        string="Details"
    )
    pnt_ubicacion = fields.Char(
        string="Ubicacion"
    )
    pnt_precio_obligatorio = fields.Boolean(
        compute='_compute_obligatoriedad_precio',
        string='Precio obligatorio',
        store=True, readonly=True
    )

    pnt_peso_obligatorio = fields.Boolean(
        compute='_compute_obligatoriedad_peso',
        string='Peso obligatorio',
        store=True, readonly=True
    )

    pnt_medidas = fields.Char('Medidas')

    _sql_constraints = [
        (
            'product_default_code_uniq',
            'unique(default_code)',
            'This default code already exist!'
        ),
    ]

    def _compute_categ_id(self):
        for record in self:
            record.pnt_categ_parent_id = record.categ_id.parent_id if record.categ_id.parent_id else record.id

    @api.onchange('categ_id')
    def pnt_onchange_categ_id(self):
        self.pnt_sale_unit = self.categ_id.pnt_sale_unit
        if not self.pnt_escandallo_manual:
            self.pnt_escandallo = self.categ_id.pnt_escandallo
        self.pnt_precio_obligatorio = self.pnt_precio_obligatorio

    @api.depends('pnt_merma', 'pnt_peso_neto', 'pnt_tipo_metal',
                 'pnt_hechura_compra', 'pnt_escandallo', 'pnt_purchase_unit', 'categ_id')
    def _compute_pnt_hechura_venta(self):
        for record in self:
            # if not record.categ_id.pnt_no_compute_sale_price:
            if record.categ_id.name == '2' or record.categ_id.parent_id.name == '2':
                base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
                base_metal = base_metal[0].pnt_base_metal if base_metal else 0

                if record.pnt_peso_neto != 0 and record.pnt_purchase_unit == 'piece':
                    hechura = (((((base_metal + base_metal * (
                            record.pnt_merma / 100)) * record.pnt_peso_neto)
                                                  + record.pnt_hechura_compra) / record.pnt_peso_neto)
                                                * record.pnt_escandallo) - base_metal
                    record.pnt_hechura_venta = self.compute_redondeo(hechura)

                if record.pnt_purchase_unit == 'weight':
                    hechura = ((base_metal + (base_metal *
                                                               record.pnt_merma / 100) + record.pnt_hechura_compra)
                                                * record.pnt_escandallo) - base_metal
                    record.pnt_hechura_venta = self.compute_redondeo(hechura)

    def get_categ_parent(self, categ):
        categ_object = self.env['product.category']
        pnt_parent_categ = categ.parent_path.split('/')[0] \
            if categ.parent_path.split('/')[0] \
            else categ.id
        parent_categ_id = categ_object.browse(int(pnt_parent_categ)).name

        return parent_categ_id if parent_categ_id else '0'

    @api.depends('pnt_merma', 'pnt_peso_neto', 'pnt_tipo_metal',
                 'pnt_hechura_compra', 'pnt_escandallo', 'pnt_purchase_unit', 'categ_id',
                 'pnt_list_price', 'pnt_sale_unit')
    def pnt_compute_list_price(self):
        for record in self:
            parent_categ_id = self.get_categ_parent(record.categ_id)

            if parent_categ_id == '1':
                record.list_price = self.compute_list_price_1(record)
            if parent_categ_id == '2':
                record.list_price = self.compute_list_price_2(record)
            if parent_categ_id == '3':
                record.list_price = self.compute_manual_price(record)
            if parent_categ_id == '4':
                record.list_price = self.compute_list_price_4(record)


    def compute_list_price_1(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        if record.pnt_purchase_unit == 'piece':
            precio_venta = (((base_metal + base_metal * (record.pnt_merma / 100)) * record.pnt_peso_neto)
                            + record.pnt_hechura_compra) * record.pnt_escandallo

        if record.pnt_purchase_unit == 'weight':
            precio_venta = (((base_metal + (base_metal * record.pnt_merma) / 100) + record.pnt_hechura_compra) *
                            record.pnt_peso_neto) * record.pnt_escandallo

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_list_price_2(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        if record.pnt_purchase_unit == 'weight':
            precio_venta = record.pnt_hechura_venta + base_metal

        if record.pnt_purchase_unit == 'piece':
            precio_venta = record.pnt_hechura_venta + base_metal

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_list_price_4(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        if record.pnt_purchase_unit == 'piece':
            precio_venta = (((base_metal + base_metal * (
                    record.pnt_merma / 100)) * record.pnt_peso_neto) + record.pnt_hechura_compra) * record.pnt_escandallo

        if record.pnt_purchase_unit == 'weight':
            precio_venta = ((base_metal + base_metal * (
                    record.pnt_merma / 100) + record.pnt_hechura_compra) * record.pnt_peso_neto) * record.pnt_escandallo

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_manual_price(self, record):
        if not record.pnt_list_price:
            precio_venta = record.standard_price * record.pnt_escandallo
        else:
            precio_venta = record.pnt_list_price

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_redondeo(self, price):
        if price != 0:
            precio_venta = str(round(price, 2)).split('.')
            entero = precio_venta[0]
            decimal = precio_venta[1]

            if len(decimal) == 2:
                if int(decimal[1]) == 0 or int(decimal[1]) == 5:
                    precio_venta = float(entero + "." + decimal)
                if int(decimal[1]) >= 1 and int(decimal[1]) <= 4:
                    decimal = decimal[0] + '5'
                    precio_venta = float(entero + "." + decimal)
                if int(decimal[1]) >= 6:
                    decimal = decimal[0] + '0'
                    precio_venta = float(entero + "." + decimal)
                    precio_venta += 0.10
                return precio_venta
        return price

    @api.depends('pnt_design', 'pnt_subdesign', 'pnt_format', 'pnt_metal', 'pnt_stones')
    def _compute_pnt_description_intern(self):
        pnt_description_intern = ''
        for record in self:
            pnt_description_intern += record.pnt_design.name + " " if record.pnt_design else ''
            pnt_description_intern += record.pnt_subdesign.name + " " if record.pnt_subdesign else ''
            pnt_description_intern += record.pnt_format.name + " " if record.pnt_format else ''
            pnt_description_intern += record.pnt_metal.name + " " if record.pnt_metal else ''
            pnt_description_intern += record.pnt_stones.name + " " if record.pnt_stones else ''
            record.pnt_description_intern = pnt_description_intern

    @api.onchange('seller_ids')
    def _pnt_onchange_seller_ids(self):
        pnt_proveedor_activo = self.mapped('seller_ids').filtered(lambda x: x.pnt_activo)
        if pnt_proveedor_activo:
            self.pnt_merma = pnt_proveedor_activo[0].pnt_merma
            self.pnt_hechura_compra = pnt_proveedor_activo[0].pnt_hechura_compra
            self.pnt_purchase_unit = pnt_proveedor_activo[0].pnt_purchase_unit
            self.standard_price = pnt_proveedor_activo[0].price

    def btn_seller_price(self):
        pnt_proveedor_activo = self.mapped('seller_ids').filtered(lambda x: x.pnt_activo)
        if pnt_proveedor_activo:
            self.standard_price = pnt_proveedor_activo[0].price

    def pnt_action_product_replenish(self):
        action = self.env.ref("stock.action_product_replenish")
        action = action.read()[0]

        if self.purchase_line_warn != 'no-message':
            message = self.purchase_line_warn_msg
            bloqueo = False
            if self.purchase_line_warn == 'block':
                bloqueo = True

            action["context"] = {
                "default_product_id": self.id,
                "block_message": message,
                "message_bool": True,
                "block_message_bool": bloqueo,
            }
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends('categ_id',
                 'categ_id.pnt_no_compute_sale_price')
    def _compute_obligatoriedad_precio(self):
        for record in self:
            if record.categ_id and record.categ_id.pnt_no_compute_sale_price:
                record.pnt_precio_obligatorio = True
            else:
                record.pnt_precio_obligatorio = False

    @api.depends('categ_id',
                 'categ_id.pnt_peso_neto_obligatorio')
    def _compute_obligatoriedad_peso(self):
        for record in self:
            if record.categ_id and record.categ_id.pnt_peso_neto_obligatorio:
                record.pnt_peso_obligatorio = True
            else:
                record.pnt_peso_obligatorio = False

    pnt_description_intern = fields.Char(
        string="Intern Descripcion",
        compute="_compute_pnt_description_intern",
        store=True
    )
    pnt_peso_neto = fields.Float(
        string='Net Weight'
    )
    pnt_quilataje = fields.Float(
        string='Quilataje',
        digits=(12, 2)
    )
    pnt_tipo_metal = fields.Many2one(
        string='Metal Type',
        comodel_name='pnt.type.metal'
    )
    pnt_metal = fields.Many2one(
        string='Metal',
        comodel_name='pnt.metal'
    )
    pnt_design = fields.Many2one(
        string='Design',
        comodel_name='pnt.design'
    )
    pnt_subdesign = fields.Many2one(
        string='Subdesign',
        comodel_name='pnt.subdesign'
    )
    pnt_format = fields.Many2one(
        string='Format',
        comodel_name='pnt.format'
    )
    pnt_stones = fields.Many2one(
        string='Stones',
        comodel_name='pnt.stones'
    )
    pnt_density = fields.Many2one(
        string='Density',
        comodel_name='pnt.density'
    )
    pnt_sale_unit = fields.Selection(
        string='Sale Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )
    pnt_escandallo = fields.Float(
        string='Escandallo'
    )
    pnt_hechura_venta = fields.Float(
        string='Hechura Venta',
        compute='_compute_pnt_hechura_venta',
        store=True
    )
    pnt_hechura_compra = fields.Float(
        string='Hechura Compra'
    )
    pnt_merma = fields.Float(
        string='Merma'
    )
    pnt_purchase_unit = fields.Selection(
        string='Purchase Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )
    pnt_categ_parent_id = fields.Many2one(
        string='Categ_parent',
        comodel_name='product.category',
        compute='_compute_categ_id'
    )
    lst_price = fields.Float(
        string='List Price',
        compute='pnt_compute_list_price',
        store=True
    )
    pnt_list_price = fields.Float(
        string='List Price Lorente',
    )
    pnt_escandallo_manual = fields.Boolean(
        string='Escandallo Manual'
    )
    pnt_detail = fields.Char(
        string="Details"
    )
    pnt_ubicacion = fields.Char(
        string="Ubicacion"
    )
    default_code = fields.Char('Internal Reference', index=True, copy=False)

    pnt_precio_obligatorio = fields.Boolean(
        compute='_compute_obligatoriedad_precio',
        string='Precio obligatorio',
        store=True, readonly=True
    )

    pnt_peso_obligatorio = fields.Boolean(
        compute='_compute_obligatoriedad_peso',
        string='Peso obligatorio',
        store=True, readonly=True
    )

    pnt_medidas = fields.Char(
        related='product_tmpl_id.pnt_medidas',
        string='Medidas',
        readonly=False
    )

    _sql_constraints = [
        (
            'product_default_code_uniq',
            'unique(default_code)',
            'This default code already exist!'
        ),
    ]

    
    def write(self, vals):
        if vals.get('categ_id', False):
            familia = self.env['product.category'].browse(vals['categ_id'])
            manual = self.pnt_escandallo_manual
            if 'pnt_escandallo_manual' in vals:
                manual = vals['pnt_escandallo_manual']
            if not manual:
                vals['pnt_escandallo'] = self.get_categ_parent_id(familia).pnt_escandallo
        return super(ProductProduct, self).write(vals)

    def _compute_categ_id(self):
        for record in self:
            record.pnt_categ_parent_id = record.categ_id.parent_id if record.categ_id.parent_id else record.id

    def get_categ_parent_id(self, categ):
        value = parent_id = categ
        while parent_id:
            value = parent_id.parent_id or parent_id
            parent_id = parent_id.parent_id

        return value

    @api.onchange('categ_id')
    def pnt_onchange_categ_id(self):
        if self.categ_id:
            self.pnt_sale_unit = self.categ_id.pnt_sale_unit
            if not self.pnt_escandallo_manual:
                self.pnt_escandallo = self.get_categ_parent_id(self.categ_id).pnt_escandallo
            self.pnt_precio_obligatorio = self.pnt_precio_obligatorio

    @api.depends('pnt_merma', 'pnt_peso_neto', 'pnt_tipo_metal',
                 'pnt_peso_neto', 'pnt_hechura_compra', 'pnt_escandallo', 'pnt_purchase_unit', 'categ_id')
    def _compute_pnt_hechura_venta(self):
        for record in self:
            parent_categ_id = self.get_categ_parent(record.categ_id)

            if parent_categ_id == '2':
                base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
                base_metal = base_metal[0].pnt_base_metal if base_metal else 0

                purchase_unit = record.seller_ids.filtered(lambda x: x.pnt_activo == True)

                if record.pnt_peso_neto != 0 and purchase_unit.pnt_purchase_unit == 'piece':
                    hechura = (((((base_metal + base_metal * (
                            purchase_unit.pnt_merma / 100)) * record.pnt_peso_neto)
                                                  + purchase_unit.pnt_hechura_compra) / record.pnt_peso_neto)
                                                * record.pnt_escandallo) - base_metal

                    record.pnt_hechura_venta = self.compute_redondeo(hechura)

                if purchase_unit.pnt_purchase_unit == 'weight':
                    hechura = ((base_metal + base_metal * (
                            purchase_unit.pnt_merma / 100) + purchase_unit.pnt_hechura_compra)
                                                * record.pnt_escandallo) - base_metal

                    record.pnt_hechura_venta = self.compute_redondeo(hechura)

    def get_categ_parent(self, categ):
        categ_object = self.env['product.category']
        pnt_parent_categ = categ.parent_path.split('/')[0] \
            if categ.parent_path.split('/')[0] \
            else categ.id
        parent_categ_id = categ_object.browse(int(pnt_parent_categ)).name

        return parent_categ_id if parent_categ_id else '0'

    @api.depends('pnt_merma', 'pnt_peso_neto', 'pnt_tipo_metal',
                 'pnt_hechura_compra', 'pnt_escandallo', 'pnt_purchase_unit', 'categ_id',
                 'pnt_list_price', 'pnt_sale_unit')
    def pnt_compute_list_price(self):
        for record in self:
            parent_categ_id = self.get_categ_parent(record.categ_id)

            if parent_categ_id == '1':
                record.lst_price = self.compute_list_price_1(record)
            if parent_categ_id == '2':
                record.lst_price = self.compute_list_price_2(record)
            if parent_categ_id == '3':
                record.lst_price = self.compute_manual_price(record)
            if parent_categ_id == '4':
                record.lst_price = self.compute_list_price_4(record)

    def compute_list_price_1(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0
        purchase_unit = record.seller_ids.filtered(lambda x: x.pnt_activo == True)
        if purchase_unit.pnt_purchase_unit == 'piece':
            precio_venta = (((base_metal + base_metal * (purchase_unit.pnt_merma / 100)) * record.pnt_peso_neto)
                            + purchase_unit.pnt_hechura_compra) * record.pnt_escandallo

        if purchase_unit.pnt_purchase_unit == 'weight':
            precio_venta = (((base_metal + (base_metal * purchase_unit.pnt_merma) / 100) +
                             purchase_unit.pnt_hechura_compra) * record.pnt_peso_neto) * record.pnt_escandallo

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_list_price_2(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        purchase_unit = record.seller_ids.filtered(lambda x: x.pnt_activo == True)
        if purchase_unit.pnt_purchase_unit == 'weight':
            precio_venta = record.pnt_hechura_venta + base_metal

        if purchase_unit.pnt_purchase_unit == 'piece':
            precio_venta = record.pnt_hechura_venta + base_metal

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_list_price_4(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0
        purchase_unit = record.seller_ids.filtered(lambda x: x.pnt_activo == True)

        if purchase_unit.pnt_purchase_unit == 'piece':
            precio_venta = (((base_metal + (base_metal * purchase_unit.pnt_merma) / 100) *
                             record.pnt_peso_neto) + purchase_unit.pnt_hechura_compra) * record.pnt_escandallo

        if purchase_unit.pnt_purchase_unit == 'weight':
            precio_venta = (((base_metal + (base_metal * purchase_unit.pnt_merma) / 100) + purchase_unit.pnt_hechura_compra) *
                            record.pnt_peso_neto) * record.pnt_escandallo

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_manual_price(self, record):
        if not record.pnt_list_price:
            precio_venta = record.standard_price * record.pnt_escandallo
        else:
            precio_venta = record.pnt_list_price

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_redondeo(self, price):
        if price != 0:
            precio_venta = str(round(price, 2)).split('.')
            entero = precio_venta[0]
            decimal = precio_venta[1]

            if len(decimal) == 2:
                if int(decimal[1]) == 0 or int(decimal[1]) == 5:
                    precio_venta = float(entero + "." + decimal)
                if int(decimal[1]) >= 1 and int(decimal[1]) <= 4:
                    decimal = decimal[0] + '5'
                    precio_venta = float(entero + "." + decimal)
                if int(decimal[1]) >= 6:
                    decimal = decimal[0] + '0'
                    precio_venta = float(entero + "." + decimal)
                    precio_venta += 0.10
                return precio_venta
        return price

    def btn_seller_price(self):
        pnt_proveedor_activo = self.mapped('seller_ids').filtered(lambda x: x.pnt_activo)
        if pnt_proveedor_activo:
            self.standard_price = pnt_proveedor_activo[0].price

    @api.depends('pnt_design', 'pnt_subdesign', 'pnt_format', 'pnt_metal', 'pnt_stones')
    def _compute_pnt_description_intern(self):
        pnt_description_intern = ''
        for record in self:
            pnt_description_intern += record.pnt_design.name + " " if record.pnt_design else ''
            pnt_description_intern += record.pnt_subdesign.name + " " if record.pnt_subdesign else ''
            pnt_description_intern += record.pnt_format.name + " " if record.pnt_format else ''
            pnt_description_intern += record.pnt_metal.name + " " if record.pnt_metal else ''
            pnt_description_intern += record.pnt_stones.name + " " if record.pnt_stones else ''
            record.pnt_description_intern = pnt_description_intern

    @api.onchange('seller_ids')
    def _pnt_onchange_seller_ids(self):
        pnt_proveedor_activo = self.mapped('seller_ids').filtered(lambda x: x.pnt_activo)
        if pnt_proveedor_activo:
            self.pnt_merma = pnt_proveedor_activo[0].pnt_merma
            self.pnt_hechura_compra = pnt_proveedor_activo[0].pnt_hechura_compra
            self.pnt_purchase_unit = pnt_proveedor_activo[0].pnt_purchase_unit
            self.standard_price = pnt_proveedor_activo[0].price

    def btn_regularize_category(self):
        products = self.env['product.product'].search([])
        for product in products:
            if not self.pnt_escandallo_manual:
                product.update({
                    'pnt_sale_unit': product.categ_id.pnt_sale_unit,
                    'pnt_escandallo': self.get_categ_parent_id(product.categ_id).pnt_escandallo
                })
            else:
                product.update({
                    'pnt_sale_unit': product.categ_id.pnt_sale_unit,
                })

    @api.model
    def create(self, vals):
        if 'categ_id' in vals:
            pc_obj = self.env['product.category']
            pc_ids = pc_obj.browse(vals['categ_id'])
            if pc_ids and 'pnt_escandallo_manual' in vals:
                if not vals['pnt_escandallo_manual']:
                    vals['pnt_escandallo'] = self.get_categ_parent_id(pc_ids).pnt_escandallo

        return super(ProductProduct, self).create(vals)

    
    def price_compute(self, price_type, uom=False, currency=False, company=False, precio_gramo=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            parent_categ_id = \
                product.get_categ_parent(product.categ_id)

            if parent_categ_id == '2':
                prices[product.id] = precio_gramo
            else:
                prices[product.id] = product[price_type] or 0.0

            if price_type == 'list_price' or price_type == 'lst_price':
                prices[product.id] += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id._convert(
                    prices[product.id], currency, product.company_id, fields.Date.today())

        return prices

    def pnt_action_product_replenish(self):
        action = self.env.ref("stock.action_product_replenish")
        action = action.read()[0]

        if self.purchase_line_warn != 'no-message':
            message = self.purchase_line_warn_msg
            bloqueo = False
            if self.purchase_line_warn == 'block':
                bloqueo = True

            action["context"] = {
                "default_product_id": self.id,
                "block_message": message,
                "message_bool": True,
                "block_message_bool": bloqueo,
            }
        return action


class ProductCategory(models.Model):
    _inherit = "product.category"

    pnt_sale_unit = fields.Selection(
        string='Sale Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )
    pnt_no_compute_sale_price = fields.Boolean(
        string='No Compute Sale Price'
    )
    pnt_escandallo = fields.Float(
        string='Escandallo'
    )
    pnt_hechura_compra = fields.Float(
        string='Hechura Compra'
    )
    pnt_merma = fields.Float(
        string='Merma'
    )
    pnt_purchase_unit = fields.Selection(
        string='Purchase Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )

    pnt_peso_neto_obligatorio = fields.Boolean(
        string='Peso Neto Obligatorio en Productos')

    pnt_cambio_escandallo = fields.Boolean(default=False)

    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        category_ids = self.env['product.category'].search([('parent_id', '=', self.id)])

        if 'pnt_peso_neto_obligatorio' in vals:
            peso_obligatorio = vals['pnt_peso_neto_obligatorio']

            for category in category_ids:
                category.write({
                    'pnt_peso_neto_obligatorio': peso_obligatorio
                })

        if 'pnt_no_compute_sale_price' in vals:
            precio_obligatorio = vals['pnt_no_compute_sale_price']

            for category in category_ids:
                category.write({
                    'pnt_no_compute_sale_price': precio_obligatorio
                })

        for category in category_ids:
            category.write({
                'pnt_sale_unit': self.pnt_sale_unit,})

        return res

    @api.onchange('parent_id')
    def _pnt_onchange_parent_id(self):
        self.pnt_sale_unit = self.parent_id.pnt_sale_unit
        if not self.pnt_escandallo_manual:
            self.pnt_escandallo = self.parent_id.pnt_escandallo

    @api.onchange('pnt_escandallo')
    def _pnt_onchange_pnt_escandallo(self):
        if self.pnt_escandallo:
            self.pnt_cambio_escandallo = True

    
    def open_escandallo_wizard(self):
       return {
       'view_type': 'form',
       'view_mode': 'form',
       'res_model': 'pnt.category.escandallo.wizard',
       'target': 'new',
       'type': 'ir.actions.act_window',
       'context': {'current_id': self.id, 'escandallo': self.pnt_escandallo}
       }


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    pnt_hechura_compra = fields.Float(
        string='Hechura Compra'
    )
    pnt_discount_hechura_compra = fields.Float(
        string='Discount Hechura Compra(%)'
    )
    pnt_merma = fields.Float(
        string='Merma'
    )
    pnt_purchase_unit = fields.Selection(
        string='Purchase Unit',
        selection=[
            ("piece", "Piece"),
            ("weight", "Weight(g)")
        ]
    )
    pnt_activo = fields.Boolean(
        string='Active'
    )
    pnt_manual_price = fields.Float(
        string='Manual Price'
    )
    price = fields.Float(
        string='Price',
        compute='pnt_compute_price',
        store=True
    )

    @api.model
    def create(self, vals):
        if not 'pnt_purchase_unit' in vals:
            vals['pnt_purchase_unit'] = 'piece'
        result = super(ProductSupplierinfo, self).create(vals)
        return result

    
    def write(self, vals):
        result = super(ProductSupplierinfo, self).write(vals)
        return result

    @api.onchange('pnt_activo')
    def _pnt_onchange_activo(self):
        if self.pnt_activo:
            proveedores = self.env['product.supplierinfo'].search([
                ('product_id', '=', self.product_id.id),
                ('pnt_activo', '=', True),
                ('name', '!=', self.name.id)
            ])
            if proveedores:
                raise ValidationError(_("Is not possible have more one supplier active in one product"))
        else:
            self.env['product.supplierinfo'].search([
                ('product_id', '=', self.product_id.id),
                ('name', '=', self.name.id)
            ]).write({'pnt_activo': self.pnt_activo})


    def get_categ_parent(self, categ):
        categ_object = self.env['product.category']
        parent_categ_id = '0'
        if categ:
            pnt_parent_categ = categ.parent_path.split('/')[0] \
                if categ.parent_path.split('/')[0] \
                else categ.id
            parent_categ_id = categ_object.browse(int(pnt_parent_categ)).name

        return parent_categ_id

    @api.depends('pnt_merma', 'product_id', 'pnt_hechura_compra', 'pnt_manual_price',
                 'product_id.pnt_peso_neto',
                 'product_id.categ_id',
                 'product_id.pnt_tipo_metal')
    def pnt_compute_price(self):
        for record in self:
            parent_categ_id = self.get_categ_parent(record.product_id.categ_id)

            if parent_categ_id == '1':
                record.price = self.compute_list_price_1(record)
            if parent_categ_id == '2':
                record.price = self.compute_list_price_2(record)
            if parent_categ_id == '3':
                record.price = self.compute_manual_price(record)
            if parent_categ_id == '4':
                record.price = self.compute_list_price_4(record)

    def compute_list_price_1(self, record):
        precio = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.product_id.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        if record.pnt_purchase_unit == 'weight':
            precio = (record.pnt_hechura_compra + base_metal + base_metal * (
                    record.pnt_merma / 100)) * record.product_id.pnt_peso_neto

        else:
            record.pnt_purchase_unit = 'piece'
            precio = (base_metal + base_metal * (
                    record.pnt_merma / 100)) * record.product_id.pnt_peso_neto + record.pnt_hechura_compra

        precio = self.compute_redondeo(precio)

        return precio

    def compute_list_price_2(self, record):
        precio = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.product_id.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        if record.pnt_purchase_unit == 'weight':
            precio = (base_metal + base_metal * (
                    record.pnt_merma / 100) + record.pnt_hechura_compra) * record.product_id.pnt_peso_neto

        else:
            record.pnt_purchase_unit = 'piece'
            precio = (base_metal + base_metal * (
                    record.pnt_merma / 100)) * record.product_id.pnt_peso_neto + record.pnt_hechura_compra

        precio = self.compute_redondeo(precio)

        return precio

    def compute_list_price_4(self, record):
        precio = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.product_id.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0

        if record.pnt_purchase_unit == 'weight':
            precio = ((base_metal + base_metal * (
                    record.pnt_merma / 100) + record.pnt_hechura_compra) * record.product_id.pnt_peso_neto)

        else:
            record.pnt_purchase_unit = 'piece'
            precio = ((base_metal + base_metal * (
                    record.pnt_merma / 100)) * record.product_id.pnt_peso_neto) + record.pnt_hechura_compra

        precio = self.compute_redondeo(precio)

        return precio

    def compute_manual_price(self, record):
        precio = self.compute_redondeo(record.pnt_manual_price)

        return precio

    def compute_redondeo(self, price):
        if price != 0:
            precio_venta = str(round(price, 2)).split('.')
            entero = precio_venta[0]
            decimal = precio_venta[1]

            if len(decimal) == 2:
                if int(decimal[1]) == 0 or int(decimal[1]) == 5:
                    precio_venta = float(entero + "." + decimal)
                if int(decimal[1]) >= 1 and int(decimal[1]) <= 4:
                    decimal = decimal[0] + '5'
                    precio_venta = float(entero + "." + decimal)
                if int(decimal[1]) >= 6:
                    decimal = decimal[0] + '0'
                    precio_venta = float(entero + "." + decimal)
                    precio_venta += 0.10
                return precio_venta
        return price

    @api.constrains('price')
    def _update_standard_price(self):
        if self.price:
            self.product_id.standard_price = self.price

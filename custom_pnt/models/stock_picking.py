import math

from odoo.addons.stock.models.stock_picking import Picking
from odoo.addons.stock.models.stock_move import StockMove
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    
    @api.depends('move_lines.pnt_cantidad_recibida')
    def _compute_texto_trazabilidad(self):
        texto = ''
        if len(self) == 1:
            for line in self.move_lines:
                texto += line.name + ' uds. ' + \
                         str(int(line.pnt_cantidad_recibida)) + '  '

            self.pnt_texto_trazabilidad = texto

    pnt_check_deposito = fields.Boolean(
        string="Gender Delivered in Deposit"
    )

    pnt_todo_plata = fields.Boolean(
        string="PLATA",
        default=False
    )

    pnt_texto_trazabilidad = fields.Text(
        compute='_compute_texto_trazabilidad',
        track_visibility='onchange',
        string='Trazabilidad',
        store=True
    )

    pnt_tipo_interno = fields.Boolean(
        string="Operación interna",
        related='picking_type_id.pnt_tipo_interno',
        store=True
    )

    line_total_qty = fields.Float('Total Quantity', compute='_compute_line_total_qty')

    
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.move_lines:
                line.sequence = current_sequence
                current_sequence += 1

    @api.depends('move_lines.product_uom_qty')
    def _compute_line_total_qty(self):
        self.line_total_qty = \
            sum(self.mapped('move_lines').mapped('product_uom_qty'))

    def pnt_update_product(self):
        for record in self.move_ids_without_package:
            if record.pnt_update:
                vals = {
                    'pnt_quilataje': record.pnt_quilates,
                    'pnt_peso_neto': record.pnt_peso_neto,
                }
                record.product_id.update(vals)

                supplierLine = self.env['product.supplierinfo'].search(
                    [('product_id', '=', record.product_id.id),
                     ('name', '=', record.picking_id.partner_id.id)])
                valsLine = {
                    'pnt_merma': record.pnt_merma,
                    'pnt_hechura_compra': record.pnt_hechura_compra,
                    'pnt_discount_hechura_compra': record.pnt_discount,
                    'pnt_purchase_unit': record.pnt_purchase_unit or 'piece',
                    'pnt_activo': True
                }

                # Eliminamos el activo anterior
                suppliers = self.env['product.supplierinfo'].search(
                    [('product_id', '=', record.product_id.id), ('pnt_activo', '=', True)])
                for s in suppliers:
                    s.pnt_activo = False

                supplierLine.update(valsLine)
                record.product_id.btn_seller_price()
                record.product_id._compute_pnt_hechura_venta()
                record.product_id.pnt_compute_list_price()

    def action_done(self):
        res = super(StockPicking, self).action_done()
        self.pnt_update_product()
        return res

    
    def onchange_internal_product_read_from_js(self, product_read, cantidad):
        if self and product_read:

            if not cantidad:
                cantidad = 1
            else:
                cantidad = float(cantidad)

            spm_obj = self.env['stock.move']
            pp_obj = self.env['product.product']
            pp_ids = pp_obj.search([
                '|', ('default_code', '=', product_read),
                ('barcode', '=', product_read)
            ])

            if pp_ids and len(pp_ids) == 1:
                existe = False
                for linea in self.move_lines.filtered(lambda l: l.product_id == pp_ids):
                    # Si el producto existe, aumentamos la cantidad
                    existe = True

                    linea.product_uom_qty += cantidad
                    linea.sequence = 0
                    continue

                if not existe:
                    vals = {
                        'sequence': 0,
                        'picking_id': self.id,
                        'location_id': self.location_id and
                                       self.location_id.id or False,
                        'location_dest_id': self.location_dest_id and
                                       self.location_dest_id.id or False,
                        'company_id': self.env.user.company_id.id,
                        'product_id': pp_ids.id,
                        'name': pp_ids.display_name,
                        'product_uom_qty': cantidad,
                        'quantity_done': 0,
                        'product_uom': pp_ids.uom_id and pp_ids.uom_id.id or False,
                    }

                    self.move_lines = [(0, 0, vals)]
                    #linea = self.move_lines.create(vals)
                    return True

            else:
                return False

        return True

    
    def onchange_internal_product_lot_read_from_js(self, product_read, lot_name, cantidad):
        if self and product_read and lot_name:

            if cantidad:
                cantidad = float(cantidad)
            else:
                cantidad = 1

            pp_obj = self.env['product.product']
            pp_ids = pp_obj.search([
                '|', ('default_code', '=', product_read),
                ('barcode', '=', product_read)
            ])

            if len(lot_name) == 12:
                lot_name = lot_name[:2] + '00000' + lot_name[7:12]
            if pp_ids and len(pp_ids) == 1:
                spl_obj = self.env['stock.production.lot']
                spl_id = spl_obj.search([
                    ('product_id', '=', pp_ids.id),
                    ('name', '=', lot_name)
                ])
                if spl_id:
                    # Existe el lote
                    peso_neto = 0.0
                    hechura_venta = 0.0
                    parent_categ_id = pp_ids.get_categ_parent(pp_ids.categ_id)

                    if parent_categ_id == '2':
                        if lot_name:
                            peso = lot_name[-5:]
                            if peso.isdigit():
                                peso_neto = int(peso) / 100
                            else:
                                peso_neto = 0.0

                            hechura_venta = pp_ids.pnt_hechura_venta

                        else:
                            peso_neto = 0.0
                            hechura_venta = 0.0

                        vals = {
                            'sequence': 0,
                            'picking_id': self.id,
                            'location_id': self.location_id and
                                           self.location_id.id or False,
                            'location_dest_id': self.location_dest_id and
                                                self.location_dest_id.id or False,
                            'company_id': self.env.user.company_id.id,
                            'product_id': pp_ids.id,
                            'name': pp_ids.display_name,
                            'product_uom_qty': cantidad,
                            'product_uom': pp_ids.uom_id and pp_ids.uom_id.id or False,
                        }

                        linea = self.move_lines.create(vals)

                        # Si el producto está disponible, añadimos la linea de lote
                        quants = self.env['stock.quant'].search([
                            ('product_id', '=', pp_ids.id),
                            ('lot_id', '=', spl_id.id)]).filtered(
                            lambda q: q.location_id.usage == 'internal')

                        if quants and  quants.filtered(
                                lambda q: q.location_id == self.location_id):
                            disponible = quants.filtered(
                                lambda q: q.location_id == self.location_id)[
                                0].unreserved_quantity
                            if disponible >= 1:
                                linea._update_reserved_quantity(
                                    1, disponible, self.location_id, lot_id=spl_id,
                                    package_id=False, strict=False)

                            if linea.move_line_ids:
                                linea.move_line_ids.write({
                                'pnt_sale_price': hechura_venta,
                                'pnt_peso_neto': peso_neto,
                                'lot_id': spl_id and spl_id.id or False,
                                'lot_name': lot_name,
                                })

                        return True

                else:
                    return False

            else:
                return False

        return True

    
    def action_assign(self):
        res = super(StockPicking, self).action_assign()
        for line in self.move_line_ids:
            if line.lot_id:
                peso = line.lot_id.name[-5:]
                if peso.isdigit():
                    peso_neto = int(peso) / 100
                else:
                    peso_neto = 0.0
                line.pnt_peso_neto = peso_neto
        return res

    
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        if self.picking_type_code == 'incoming':
            for line in self.move_lines:
                if line.quantity_done > 0 and line.pnt_cantidad_recibida != line.quantity_done:
                    raise UserError(_('No coincide la cantidad recibida con la hecha.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        no_line_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_lines.mapped('move_line_ids').filtered(lambda m: m.state not in ('done', 'cancel')))
        if no_reserved_quantities and no_quantities_done and no_line_quantities_done:
            raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            for x in self.move_lines.mapped('move_line_ids'):
                if x.id not in lines_to_check.ids:
                    lines_to_check += x

            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none' and line.qty_done > 0:
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        if picking_type.code == 'internal':
            if no_quantities_done:
                view = self.env.ref('stock.view_immediate_transfer')
                wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
                return {
                    'name': _('Immediate Transfer?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.immediate.transfer',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return

    Picking.button_validate = button_validate


class StockMove(models.Model):
    _inherit = ['stock.move', 'mail.thread', 'mail.activity.mixin']
    _name = 'stock.move'

    pnt_quilates = fields.Float(
        string="Quilates",
        digits=(12, 2),
        default=lambda self: self.product_id.pnt_quilataje

    )
    pnt_peso_neto = fields.Float(
        string="Net Weight",
        compute="_compute_net_weight"
    )
    pnt_peso_neto_global = fields.Float(
        string="Net Weight global"
    )
    pnt_peso_neto_global_compute = fields.Float(
        string="Net Weight global compute",
        compute="_compute_net_weight_global",
        store=True
    )
    pnt_merma = fields.Float(
        string="Merma",

    )
    pnt_discount = fields.Float(
        string='Discount',
    )
    pnt_update = fields.Boolean(
        string='Update',
        default=False
    )
    pnt_hechura_compra = fields.Float(
        string='Hechura Compra',
    )
    pnt_purchase_unit = fields.Selection([
        ('piece', 'Piece'),
        ('weight', 'Weight(g)'),
    ],
        string='Unidad de compra'
    )

    pnt_sale_price = fields.Float(
        string='Sale Price',
        compute='pnt_compute_list_price'
    )
    pnt_lot = fields.Char(
        string='Lot'
    )

    pnt_primera_vez = fields.Boolean(default=False)

    pnt_cantidad_recibida = fields.Float(
        string='Cantidad recibida',
        copy=False,
    )
    sequence = fields.Integer(string='Sequence', default=0)

    impresora = fields.Selection(
        [('imp01', 'Impresora TSC'),
         ('imp02', 'Impresora Toshiba'),
        ], string='Impresora', default='imp01'
    )

    @api.depends('move_line_ids')
    def _compute_net_weight_global(self):
        for record in self:
            move_line = self.env['stock.move.line'].search([
                ('move_id', '=', record.id)
            ])
            if move_line:
                record.pnt_peso_neto_global_compute = \
                    round_half_up(sum(move_line.filtered(
                        lambda l: l.qty_done > 0).mapped("pnt_peso_neto")), 2)

    @api.depends('quantity_done','pnt_peso_neto_global', 'pnt_peso_neto_global_compute')
    def _compute_net_weight(self):
        for record in self:
            if record.state == 'done':
                if record.quantity_done:
                    record.pnt_peso_neto = \
                        round_half_up(record.pnt_peso_neto_global_compute /
                                      record.quantity_done, 2)
                else:
                    record.pnt_peso_neto = \
                        round_half_up(record.pnt_peso_neto_global_compute /
                                      record.product_uom_qty if
                                      record.product_uom_qty != 0 else 0, 2)

            else:
                if record.pnt_cantidad_recibida:
                    if record.quantity_done:
                        record.pnt_peso_neto = round_half_up(
                            record.pnt_peso_neto_global_compute / record.pnt_cantidad_recibida if
                            record.pnt_cantidad_recibida != 0 else 0, 2)
                    else:
                        record.pnt_peso_neto = round_half_up(
                            record.pnt_peso_neto_global / record.product_uom_qty if
                            record.product_uom_qty != 0 else 0, 2)
                else:
                    record.pnt_peso_neto = round_half_up(
                        record.pnt_peso_neto_global / record.product_uom_qty if
                        record.product_uom_qty != 0 else 0, 2)


            # quantity = record.quantity_done if record.quantity_done > 0 else record.product_uom_qty
            # if record.pnt_peso_neto_global_compute < record.pnt_peso_neto_global:
            #     record.pnt_peso_neto = record.pnt_peso_neto_global / quantity \
            #         if quantity != 0 else 0
            # else:
            #     record.pnt_peso_neto = record.pnt_peso_neto_global_compute / quantity \
            #         if quantity != 0 else 0

    def get_product_supplier_info(self):
        supplier_info = self.env['product.supplierinfo'].search([
            ('product_id', '=', self.product_id.id),
            ('name', '=', self.picking_id.partner_id.id)
        ])

        if supplier_info:
            self.update({
                'pnt_merma': supplier_info[0].pnt_merma,
                'pnt_discount': supplier_info[0].pnt_discount_hechura_compra,
                'pnt_hechura_compra': supplier_info[0].pnt_hechura_compra,
                'pnt_purchase_unit': supplier_info[0].pnt_purchase_unit
            })
        else:
            raise UserError(
                _(
                    "Supplier " + self.picking_id.partner_id.name + " is not assigned in article !" + self.product_id.name))

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockMove, self).onchange_product_id()
        if self.picking_type_id.id == 1 and self.product_id:
            self.pnt_quilates = self.product_id.pnt_quilataje
            self.get_product_supplier_info()
        return res

    @api.onchange('impresora')
    def onchange_impresora(self):
        if self.impresora:
            for sml in self.move_line_ids:
                sml.write({'impresora': self.impresora})

    @api.depends('pnt_merma', 'pnt_peso_neto',
                 'pnt_hechura_compra',
                 'product_id', 'pnt_purchase_unit', 'product_uom_qty')
    def pnt_compute_list_price(self):
        for record in self:
            if record.product_id:
                parent_categ_id = record.product_id.get_categ_parent(record.product_id.categ_id)

                if parent_categ_id == '1':
                    record.pnt_sale_price = self.compute_list_price_1(record)
                if parent_categ_id == '2':
                    record.pnt_sale_price = self.compute_list_price_2(record)
                if parent_categ_id == '3':
                    record.pnt_sale_price = self.compute_manual_price(record)
                if parent_categ_id == '4':
                    record.pnt_sale_price = self.compute_list_price_4(record)

    def compute_list_price_1(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.product_id.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0
        if record.pnt_purchase_unit:
            purchase_unit = record.pnt_purchase_unit
        else:
            purchase_unit = self.env['product.supplierinfo'].search(
                [('product_id', '=', record.product_id.id),
                 ('name', '=', record.picking_id.partner_id.id)]).pnt_purchase_unit

        if purchase_unit == 'piece':
            precio_venta = (((base_metal + (base_metal * record.pnt_merma) / 100) *
                            record.pnt_peso_neto) + record.pnt_hechura_compra) * record.product_id.pnt_escandallo

        if purchase_unit == 'weight':
            precio_venta = (((base_metal + (base_metal * record.pnt_merma) / 100) + record.pnt_hechura_compra) *
                            record.pnt_peso_neto) * record.product_id.pnt_escandallo

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_list_price_2(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.product_id.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0
        if record.pnt_purchase_unit:
            purchase_unit = record.pnt_purchase_unit
        else:
            purchase_unit = self.env['product.supplierinfo'].search(
                [('product_id', '=', record.product_id.id),
                 ('name', '=', record.picking_id.partner_id.id)]).pnt_purchase_unit

        if purchase_unit == 'piece':
            precio_venta = ((((((base_metal + (base_metal * record.pnt_merma) / 100) * record.pnt_peso_neto) +
                               record.pnt_hechura_compra) / record.pnt_peso_neto) * record.product_id.pnt_escandallo) -
                            base_metal) if record.pnt_peso_neto != 0 else 0

        if purchase_unit == 'weight':
            precio_venta = (((base_metal + (base_metal * record.pnt_merma) / 100) + record.pnt_hechura_compra) *
                            record.product_id.pnt_escandallo) - base_metal

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_list_price_4(self, record):
        precio_venta = 0
        base_metal = self.env['pnt.base.metal'].search([('pnt_metal_id', '=', record.product_id.pnt_tipo_metal.id)])
        base_metal = base_metal[0].pnt_base_metal if base_metal else 0
        if record.pnt_purchase_unit:
            purchase_unit = record.pnt_purchase_unit
        else:
            purchase_unit = self.env['product.supplierinfo'].search(
                [('product_id', '=', record.product_id.id),
                 ('name', '=', record.picking_id.partner_id.id)]).pnt_purchase_unit

        if purchase_unit == 'piece':
            precio_venta = (((base_metal + (base_metal * record.pnt_merma) / 100) *
                             record.pnt_peso_neto) + record.pnt_hechura_compra) * record.product_id.pnt_escandallo

        if purchase_unit == 'weight':
            precio_venta = (((base_metal + (base_metal * record.pnt_merma) / 100) + record.pnt_hechura_compra) *
                            record.pnt_peso_neto) * record.product_id.pnt_escandallo

        precio_venta = self.compute_redondeo(precio_venta)

        return precio_venta

    def compute_manual_price(self, record):
        precio_venta = self.compute_redondeo(record.product_id.pnt_list_price)

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
        return round_half_up(price, 2)

    def action_show_details(self):
        if self.origin_returned_move_id or self.picking_code == 'internal':
            return super(StockMove, self).action_show_details()

        if self.state not in ['cancel', 'done'] and self.picking_type_id.id != 5:
            parent_categ_id = self.product_id.get_categ_parent(self.product_id.categ_id)
            lot = ''
            if parent_categ_id == '2':
                if not self.pnt_primera_vez:
                    self.pnt_primera_vez = True
                    self._do_unreserve()
                    self.move_line_ids.unlink()

                peso_linea = str(int(round_half_up(self.pnt_peso_neto * 100, 0))).zfill(5)
                lot = "99" + '00000' + peso_linea
            else:
                precio_venta = str(int(round(self.pnt_sale_price * 100, 2)))
                # lot = precio_venta.zfill(7) + "0"
                #lot = precio_venta.zfill(7)

            if lot:
                n_lot = self.env['stock.production.lot'].search(
                    [('name', '=', lot), ('product_id', '=', self.product_id.id)])
                if not n_lot:
                    n_lot = self.env['stock.production.lot'].create({
                        'product_id': self.product_id.id,
                        'name': lot
                    })

                if parent_categ_id == "2":
                    self.mapped('move_line_ids').filtered(lambda x : not x.lot_id).write({
                        'lot_id': n_lot.id,
                        'pnt_peso_neto_global_compute':self.pnt_peso_neto_global_compute,
                        'pnt_sale_price': self.pnt_sale_price,
                        'product_uom_qty': 1,
                        'pnt_peso_neto': self.pnt_peso_neto
                    })

                    rango = int(self.product_uom_qty - len(self.move_line_ids))
                    # Evitamos que la unidad se quede vacia si no viene de compras.
                    uom_id = self.purchase_line_id and \
                             self.purchase_line_id.product_uom and \
                             self.purchase_line_id.product_uom.id or \
                             self.product_id.uom_id.id

                    vals = {
                        'move_id': self.id,
                        'product_id': self.product_id.id,
                        'pnt_sale_price': self.pnt_sale_price,
                        'pnt_peso_neto_global_compute': self.pnt_peso_neto_global_compute,
                        'pnt_peso_neto': self.pnt_peso_neto,
                        'lot_id': n_lot.id,
                        'date': self.date,
                        'location_dest_id': self.location_dest_id.id,
                        'location_id': self.location_id.id,
                        'product_uom_id': uom_id,
                        'product_uom_qty': 1,
                    }
                    i = 0
                    while i < rango:
                        self.env['stock.move.line'].create(vals)
                        i += 1
            else:
                move_line = self.env['stock.move.line'].search([
                    ('move_id', '=', self.id),
                ])
                for line in move_line:
                    line.write({
                        'pnt_sale_price': self.pnt_sale_price,
                        'pnt_peso_neto': self.pnt_peso_neto_global,
                    })
        return super(StockMove, self).action_show_details()

    @api.model
    def create(self, vals):
        if 'origin_returned_move_id' in vals:
            sm_obj = self.env['stock.move']
            sm_id = sm_obj.search([('id', '=', vals['origin_returned_move_id'])])
            if sm_id:
                vals['pnt_sale_price'] = sm_id.pnt_sale_price

        vals['pnt_primera_vez'] = False
        res = super(StockMove, self).create(vals)

        spt_id = False
        if 'picking_type_id' in vals:
            spt_obj = self.env['stock.picking.type']
            spt_id = spt_obj.search([('id', '=', vals['picking_type_id'])])

        pp_obj = self.env['product.product']
        pp_ids = pp_obj.browse(vals['product_id'])

        if spt_id and spt_id.code == 'outgoing':
            pass
            # if res and 'desde_venta' in self.env.context:
            #     if not res.origin_returned_move_id:
            #         res.picking_id.action_assign()

        elif spt_id and spt_id.code == 'incoming':
            if pp_ids:
                supplier_info = self.env['product.supplierinfo'].search(
                    [('product_id', '=', pp_ids.id),
                     ('name', '=', res.picking_id.partner_id.id)])
                if supplier_info:
                    res.pnt_purchase_unit = supplier_info.pnt_purchase_unit

                if 'pnt_peso_neto' in vals:
                    res.pnt_merma = pp_ids.pnt_merma
                    res.pnt_peso_neto_global = \
                        vals['product_uom_qty'] * vals['pnt_peso_neto']
                else:
                    res.pnt_merma = pp_ids.pnt_merma
                    res.pnt_peso_neto = pp_ids.pnt_peso_neto
                    res.pnt_peso_neto_global = \
                        vals['product_uom_qty'] * pp_ids.pnt_peso_neto

                if not res.pnt_sale_price:
                    res.pnt_sale_price = pp_ids.pnt_hechura_venta
        else:
            pass
        if vals.get('picking_id', False):
            res.picking_id._reset_sequence()

        #SI ES UN PRODUCTO CONSUMIBLE, LO RESERVAMOS
        if vals.get('product_id', False):
            pp_ids = self.env['product.product'].browse(vals['product_id'])
            if pp_ids and pp_ids.type == 'consu':
                res._action_confirm()
                res._action_assign()

        return res

    def _action_confirm(self, merge=False, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id, move.rule_id and move.rule_id.name or "/", origin,
                                              values)

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply()
        if merge:
            return self._merge_moves(merge_into=merge_into)
        return self

    StockMove._action_confirm = _action_confirm


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pnt_peso_neto = fields.Float(
        string="Net Weight"
    )
    pnt_peso_neto_global_compute = fields.Float(
        string="Net Weight global compute",
        readonly=True,
    )
    pnt_sale_price = fields.Float(
        string='Sale Price',
        readonly=True,
    )

    picking_type_code = fields.Selection(
        string='Picking code',
        related='picking_id.picking_type_code',
        store=True,
        copy=False,
    )

    pnt_partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='picking_id.partner_id',
        string='Cliente',
    )
    impresora = fields.Selection(
        selection=[('imp01', 'Impresora TSC'),
         ('imp02', 'Impresora Toshiba'),
        ], string='Impresora', default='imp01'
    )

    # @api.onchange('pnt_peso_neto')
    # def onchange_pnt_peso_neto(self):
    #     if self.move_id.product_id.categ_id.parent_id.name == "2":
    #         hechura_venta = str(int(round(self.pnt_sale_price * 100, 2))).zfill(5)
    #         peso_linea = str(int(round(self.pnt_peso_neto * 100, 2))).zfill(5)
    #         lot = "99" + hechura_venta + peso_linea
    #         if lot:
    #             n_lot = self.env['stock.production.lot'].search(
    #                 [('name', '=', lot), ('product_id', '=', self.product_id.id)])
    #         if not n_lot:
    #             n_lot = self.env['stock.production.lot'].create({
    #                 'product_id': self.product_id.id,
    #                 'name': lot
    #             })
    #         self.lot_id = n_lot

    @api.model
    def create(self, vals):
        if 'move_id' in vals:
            pp_obj = self.env['product.product']
            mv_id = self.env['stock.move'].browse(vals['move_id'])
            if mv_id and mv_id.origin_returned_move_id:
                if 'product_id' in vals:
                    pp_id = pp_obj.browse(vals['product_id'])
                    parent_categ_id = pp_id.get_categ_parent(pp_id.categ_id)

                    if parent_categ_id == '2':
                        origen = mv_id.origin_returned_move_id
                        vals['product_uom_qty'] = 1
                        vals['pnt_peso_neto'] = \
                            mv_id.pnt_peso_neto
                        if len(origen.move_line_ids) == 1:
                            vals['pnt_sale_price'] = \
                                origen.move_line_ids.pnt_sale_price
                        else:
                            vals['pnt_sale_price'] = \
                                origen.pnt_sale_price or mv_id.pnt_sale_price

                        if mv_id.pnt_lot:
                            n_lot = self.env['stock.production.lot'].search(
                                [('name', '=', mv_id.pnt_lot),
                                 ('product_id', '=', mv_id.product_id.id)])
                            if n_lot:
                                vals['lot_id'] = n_lot.id
            else:
                # En Ventas, Comprobamos que existe lote si es de familia 2
                if mv_id and  mv_id.picking_code and mv_id.picking_code not in ('internal', 'incoming'):
                    pp_id = pp_obj.browse(vals['product_id'])
                    parent_categ_id = pp_id.get_categ_parent(pp_id.categ_id)
                    if parent_categ_id == '2':
                        cantidad_lote = \
                            sum(self.env['stock.quant'].search([
                                ('product_id', '=', vals['product_id']),
                                ('lot_id', '=', vals['lot_id'])]).filtered(
                                lambda spl: spl.location_id.usage ==
                                            'internal').mapped('quantity'))
                        if not cantidad_lote:
                            raise UserError(_('No hay stock disponible del lote.'))

        res = super(StockMoveLine, self).create(vals)
        return res

    
    def write(self, vals):
        for record in self:
            if 'state' in vals or 'lot_id' in vals:
                return super(StockMoveLine, record).write(vals)

            if record.move_id.inventory_id:
                return super(StockMoveLine, record).write(vals)

            if record.state not in ['cancel', 'done'] and \
                    record.move_id[0].picking_type_id.id == 4:
                parent_categ_id = record.product_id.get_categ_parent(record.product_id.categ_id)
                lot = False
                if parent_categ_id == '2':
                    if 'pnt_peso_neto' in vals:
                        peso_linea = \
                            str(int(round_half_up(vals['pnt_peso_neto'] * 100, 0))).zfill(5)
                    else:
                        peso_linea = \
                            str(int(round_half_up(record.pnt_peso_neto * 100,
                                                  0))).zfill(5)
                    lot = "99" + '00000' + peso_linea

                if lot:
                    n_lot = self.env['stock.production.lot'].search(
                        [('name', '=', lot), ('product_id', '=', record.product_id.id)])
                    if not n_lot:
                        n_lot = self.env['stock.production.lot'].create({
                            'product_id': record.product_id.id,
                            'name': lot
                        })

                    vals['lot_id'] = n_lot.id
                    vals['pnt_sale_price'] = record.pnt_sale_price
                    vals['product_uom_qty'] = 1
                    if not 'pnt_peso_neto' in vals:
                        vals['pnt_peso_neto'] = record.pnt_peso_neto

            return super(StockMoveLine, record).write(vals)

        return super(StockMoveLine, self).write(vals)

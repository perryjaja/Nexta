# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError, ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pnt_aleacion = fields.Char(
        string="Alloy"
    )
    pnt_observations = fields.Char(
        string="Observations"
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine,self).onchange_product_id()
        self.pnt_aleacion = self.product_id.pnt_tipo_metal.name
        # supplierInfo = self.env['product.supplierinfo'].search([('product_id', '=', self.product_id.id),
        #                                                         ('name', '=', self.partner_id.id)])
        # if not supplierInfo and self.product_id:
        #     raise ValidationError(_("This supplier (%s) is not assigned to the product %s!"% \
        #                            (self.partner_id.name, self.partner_id.name)))
        return res

    
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for record in res:
            partner = self.env['stock.picking'].browse(record['picking_id'])
            supplierInfo = self.env['product.supplierinfo'].search([('product_id', '=', record['product_id']),
                                                                 ('name', '=', partner.partner_id.id)])
            record['pnt_quilates'] = self.env['product.product'].search([('id','=',record['product_id'])]).pnt_quilataje
            record['pnt_merma'] = supplierInfo.pnt_merma
            record['pnt_hechura_compra'] = supplierInfo.pnt_hechura_compra
            record['pnt_discount'] = supplierInfo.pnt_discount_hechura_compra
            record['pnt_peso_neto_global'] = self.env['product.product'].search(
                [('id', '=', record['product_id'])
                 ]).pnt_peso_neto * self.product_uom_qty
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
                # Convert the price in the right currency.
                currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
                price = self.currency_id._convert(line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                    default_uom = line.product_id.product_tmpl_id.uom_po_id
                    price = line.product_uom._compute_price(price, default_uom)

                supplierinfo = {
                    'name': partner.id,
                    'product_id': line.product_id.id,
                    'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                    'min_qty': 0.0,
                    'price': price,
                    'currency_id': currency.id,
                    'delay': 0,
                }
                # In case the order partner is a contact address, a new supplierinfo is created on
                # the parent company. In this case, we keep the product name and code.
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom)
                if seller:
                    supplierinfo['product_name'] = seller.product_name
                    supplierinfo['product_code'] = seller.product_code
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break

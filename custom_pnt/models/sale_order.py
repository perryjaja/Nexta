# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('state',
                 'order_line.invoice_status',
                 'order_line.qty_delivered',
                 'order_line.qty_invoiced')
    def _get_pnt_pending_invoiced_amount(self):
        for order in self.filtered(
                lambda l: l.company_id == self.env.user.company_id):
            facturado = 0.0
            pendiente = 0.0
            for line in order.order_line:
                facturado += line.untaxed_amount_invoiced
                pendiente += line.untaxed_amount_to_invoice

            order.pnt_invoice_amount_untaxed = facturado
            order.pnt_invoice_pending_amount = pendiente

    @api.depends('state', 'order_line.invoice_status', 'order_line.invoice_lines')
    def _get_invoiced(self):
        """
        Compute the invoice status of a SO. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - to invoice: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - invoiced: if all SO lines are invoiced, the SO is invoiced.
        - upselling: if all SO lines are invoiced or upselling, the status is upselling.

        The invoice_ids are obtained thanks to the invoice lines of the SO lines, and we also search
        for possible refunds created directly from existing invoices. This is necessary since such a
        refund is not directly linked to the SO.
        """
        # Ignore the status of the deposit product
        deposit_product_id = self.env['sale.advance.payment.inv']._default_product_id()
        line_invoice_status_all = [(d['order_id'][0], d['invoice_status']) for d in self.env['sale.order.line'].read_group([('order_id', 'in', self.ids), ('product_id', '!=', deposit_product_id.id)], ['order_id', 'invoice_status'], ['order_id', 'invoice_status'], lazy=False)]
        for order in self:
            invoice_ids = \
                order.order_line.mapped('invoice_lines').mapped(
                    'invoice_id').sudo().filtered(
                    lambda r: r.type in ['out_invoice', 'out_refund'])
            # Search for invoices which have been 'cancelled' (filter_refund = 'modify' in
            # 'account.invoice.refund')
            # use like as origin may contains multiple references (e.g. 'SO01, SO02')
            refunds = invoice_ids.search([('origin', 'like', order.name), ('company_id', '=', order.company_id.id), ('type', 'in', ('out_invoice', 'out_refund'))])
            invoice_ids |= refunds.filtered(lambda r: order.name in [origin.strip() for origin in r.origin.split(',')])

            # Search for refunds as well
            domain_inv = expression.OR([
                ['&', ('origin', '=', inv.number), ('journal_id', '=', inv.journal_id.id)]
                for inv in invoice_ids if inv.number
            ])
            if domain_inv:
                refund_ids = self.env['account.move'].search(expression.AND([
                    ['&', ('type', '=', 'out_refund'), ('origin', '!=', False)],
                    domain_inv
                ]))
            else:
                refund_ids = self.env['account.move'].browse()

            line_invoice_status = [d[1] for d in line_invoice_status_all if d[0] == order.id]

            if order.state not in ('sale', 'done'):
                invoice_status = 'no'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
            elif line_invoice_status and all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
            elif line_invoice_status and all(invoice_status in ['invoiced', 'upselling'] for invoice_status in line_invoice_status):
                invoice_status = 'upselling'
            else:
                invoice_status = 'no'

            order.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
                'invoice_status': invoice_status
            })


    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_get_invoiced',
        readonly=True
    )
    invoice_ids = fields.Many2many(
        comodel_name="account.move",
        string='Invoices',
        compute="_get_invoiced",
        readonly=True,
        copy=False
    )
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_get_invoiced', store=True,
        readonly=True
    )

    pnt_invoice_amount_untaxed = fields.Float(
        string='Invoices amount untaxed',
        compute='_get_pnt_pending_invoiced_amount',
        store=False,
    )
    pnt_invoice_pending_amount = fields.Float(
        string='Pending to invoice',
        compute='_get_pnt_pending_invoiced_amount',
        store=False,
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pnt_detalle = fields.Char(string='Details')
    pnt_ubicacion = fields.Char(string='Ubicacion')
    pnt_peso = fields.Float(string='Weight')
    pnt_quilates = fields.Float(
        related='product_id.pnt_quilataje',
        string='Quilates', store=True)
    pnt_precio_gramo = fields.Float(
        string='Precio gramo',
        digits=dp.get_precision('Product Price'),
        default=0.0
    )

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if not self.product_id:
            return result

        if self.product_id:
            vals = {}

            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id
            )

            parent_categ_id = \
                product.get_categ_parent(product.categ_id)

            if parent_categ_id == '2':
                vals['pnt_peso'] = product.pnt_peso_neto or 0.0
            else:
                vals['pnt_peso'] = 0.0

            vals['pnt_detalle'] = product.pnt_detail or ''
            vals['pnt_ubicacion'] = product.pnt_ubicacion or ''
            vals['pnt_quilates'] = product.pnt_quilataje or 0.0

            self.update(vals)
        return result

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            pp_obj = self.env['product.product']
            pp_ids = pp_obj.search([('id', '=', vals['product_id'])])
            if pp_ids:
                vals['pnt_detalle'] = pp_ids.pnt_detail or ''
                vals['pnt_ubicacion'] = pp_ids.pnt_ubicacion or ''
                vals['pnt_quilates'] = pp_ids.pnt_quilataje or 0.0
                familia2_ids = pp_obj.search([
                    ('id', '=', vals['product_id']),
                    ('categ_id', 'child_of', 5)])
                if familia2_ids:
                    vals['pnt_peso'] = familia2_ids.pnt_peso_neto or 0.0
        return super(SaleOrderLine, self).create(vals)

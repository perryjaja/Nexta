# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    pnt_payment_day = fields.Char(
        string="Payment day",
        compute="_compute_payment_day"
    )

    @api.depends('partner_id')
    def _compute_payment_day(self): 
        for record in self:
            if record.type in ('out_invoice', 'out_refund'):
                record.pnt_payment_day = record.partner_id.pnt_payment_day_client
            if record.type in ('in_invoice', 'in_refund'):
                record.pnt_payment_day = record.partner_id.pnt_payment_day_supplier

    def action_invoice_open(self):
        if any(abs(line.price_subtotal) < 0.01 and line.discount < 100 for line in self.mapped('invoice_line_ids')):
            raise ValidationError(_('No pueden haber lineas a precio 0 sin descuento.'))

        return super(AccountInvoice, self).action_invoice_open()

    @api.model
    def create(self, vals):
        if vals.get('origin', False) and vals.get('sale_type_id', False):
            vals['comment'] = ''

        return super(AccountInvoice, self).create(vals)


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    condicional = fields.Boolean(
        string='Condicional',
        compute='compute_condicional',
        store=True,
    )

    @api.depends('move_line_ids')
    def compute_condicional(self):
        for record in self:
            res = False
            if any(record.mapped('move_line_ids').mapped('picking_id').mapped('pnt_check_deposito')):
                res = True

            record.condicional = res

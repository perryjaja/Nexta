from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    condicional = fields.Boolean(
        string='Condicional',
        readonly=True
    )

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + \
            ", sub.condicional as condicional"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + \
            ", ail.condicional as condicional"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + \
            ", ail.condicional"

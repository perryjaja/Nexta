from odoo import api, fields, models


class ProductReplenish(models.TransientModel):
    _inherit = 'product.replenish'

    block_message_bool = fields.Boolean(string='Bloqueo')
    message_bool = fields.Boolean(string='Aviso')
    block_message = fields.Text(string='Mensaje')

    @api.model
    def default_get(self, fields):
        res = super(ProductReplenish, self).default_get(fields)
        if self.env.context.get('block_message', False):
            res['block_message_bool'] = self.env.context.get('block_message_bool', False)
            res['message_bool'] = self.env.context.get('message_bool', False)
            res['block_message'] = self.env.context.get('block_message', False)

        return res

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerProductRankingWizard(models.TransientModel):
    _name = 'pnt.partner.product.ranking.wizard'
    _description = 'Ranking de ventas de productos'

    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor'
    )

    @api.model
    def default_get(self, fields):
        result = super(PartnerProductRankingWizard, self).default_get(fields)
        result['partner_id'] = self._context.get('active_id', False)
        result['fecha_inicio'] = date(date.today().year, 1, 1)
        result['fecha_fin'] = date.today()
        return result

    def calcula_ranking(self):
        action = self.env.ref("custom_pnt.pnt_action_server_partner_product_ranking_wizard")
        action = action.read()[0]
        action["context"] = {
            "proveedor": self.partner_id.id,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
        }
        return action

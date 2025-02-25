import math

from odoo.addons.stock.models.stock_picking import Picking
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    pnt_tipo_interno = fields.Boolean(
        string="Operación interna",
        default=False
    )

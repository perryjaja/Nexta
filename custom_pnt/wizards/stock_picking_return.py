from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    location_id = fields.Many2one(
        'stock.location', 'Return Location',
        domain="['|', ('usage', '=', 'internal'), ('return_location', '=', True)]")

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)
        if not 'product_return_moves' in res:
            return res
        sp_obj = self.env['stock.picking']
        if 'picking_id' in res:
            sp_ids = sp_obj.search([('id', '=', res['picking_id'])])
            if sp_ids and sp_ids.picking_type_code == 'incoming':
                devolver_f2 = []
                for rm in res['product_return_moves']:
                    mv_obj = self.env['stock.move']
                    mv_ids = mv_obj.browse(rm[2]['move_id'])
                    if mv_ids:
                        parent_categ_id = mv_ids.product_id.get_categ_parent(
                            mv_ids.product_id.categ_id)
                        if parent_categ_id == '2':
                            del rm
                            for sml in mv_ids.move_line_ids:
                                devolver_f2.append((0, 0, {
                                    'product_id': mv_ids.product_id.id,
                                    'move_id': mv_ids.id,
                                    'quantity': 1,
                                    'uom_id': mv_ids.product_id.uom_id.id,
                                    'pnt_peso_neto': sml.pnt_peso_neto,
                                    'pnt_lot_id':
                                        sml.lot_id and
                                        sml.lot_id.id or False,
                                    'pnt_sale_price':
                                        sml.pnt_sale_price or
                                        sml.pnt_hechura_venta,
                                    'to_refund': True
                                              }))
                        else:
                            rm[2].update({'to_refund': True})

                if devolver_f2:
                    productos = []
                    for l in devolver_f2:
                        if l[2]['product_id'] not in productos:
                            productos.append(l[2]['product_id'])

                    i = 0
                    for l in res['product_return_moves']:
                        if l[2]['product_id'] in productos:
                            del res['product_return_moves'][i]
                        i += 1

                    res['product_return_moves'] += devolver_f2
                return res
            else:
                if sp_ids:
                    for rm in res['product_return_moves']:
                        mv_obj = self.env['stock.move']
                        mv_ids = mv_obj.browse(rm[2]['move_id'])
                        if mv_ids:
                            parent_categ_id = mv_ids.product_id.get_categ_parent(
                                mv_ids.product_id.categ_id)
                            if parent_categ_id == '2':
                                rm[2].update({
                                    'pnt_peso_neto':
                                        mv_ids.move_line_ids.pnt_peso_neto,
                                    'pnt_lot_id':
                                        mv_ids.move_line_ids.lot_id and
                                        mv_ids.move_line_ids.lot_id.id or False,
                                    'pnt_sale_price':
                                        mv_ids.move_line_ids.pnt_sale_price or
                                        mv_ids.product_id.pnt_hechura_venta,
                                    'to_refund': True})
                            else:
                                rm[2].update({'to_refund': True})
        else:
            return res

        for rm in res['product_return_moves']:
            mv_obj = self.env['stock.move']
            mv_ids = mv_obj.browse(rm[2]['move_id'])
            if mv_ids:
                parent_categ_id = mv_ids.product_id.get_categ_parent(
                    mv_ids.product_id.categ_id)
                if parent_categ_id == '2':
                    rm[2].update({'pnt_peso_neto':
                                      mv_ids.move_line_ids.pnt_peso_neto,
                                  'pnt_lot_id':
                                      mv_ids.move_line_ids.lot_id and
                                      mv_ids.move_line_ids.lot_id.id or False,
                                  'pnt_sale_price':
                                      mv_ids.move_line_ids.pnt_sale_price or
                                      mv_ids.product_id.pnt_hechura_venta,
                                  })
                rm[2].update({'to_refund': True})

        return res

    def _create_returns(self):
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id
        new_picking = self.picking_id.create({
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': _("Return of %s") % self.picking_id.name,
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(return_line, new_picking)
                vals['to_refund'] = True
                r = return_line.move_id.copy(vals)
                vals = {}

                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]

                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking.id, picking_type_id.id

    def _prepare_move_default_values(self, return_line, new_picking):
        result = \
            super(ReturnPicking, self)._prepare_move_default_values(
                return_line, new_picking)

        result['pnt_peso_neto'] = return_line.pnt_peso_neto or \
                                  return_line.product_id.pnt_peso_neto
        result['pnt_sale_price'] = return_line.pnt_sale_price

        if return_line and return_line.pnt_lot_id:
            result['pnt_lot'] = return_line.pnt_lot_id.name

        return result


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    pnt_peso_neto = fields.Float(
        string="Net Weight",
    )
    pnt_sale_price = fields.Float(
        string='Sale Price',
        readonly=True,
    )
    pnt_lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial Number',
        domain="[('product_id', '=', product_id)]")

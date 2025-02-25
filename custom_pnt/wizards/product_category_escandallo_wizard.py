from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductSupplierinfo(models.TransientModel):
    _name = 'pnt.category.escandallo.wizard'
    _description = 'Categorias de escandallos'

    
    def actualiza_escandallo(self):
        if 'current_id' in self.env.context and \
                'escandallo' in self.env.context:
            escandallo = self.env.context['escandallo']
            pp_obj = self.env['product.product']
            productos = pp_obj.search([
                ('categ_id', 'child_of', self.env.context['active_ids'])])
            for p in productos:
                if not p.pnt_escandallo_manual:
                    p.pnt_escandallo = escandallo

        else:
            raise UserError(_('Error desconocido.'))

        # Ocultamos el botón
        categ = self.env['product.category'].search([
            ('id', '=', self.env.context['current_id'])])
        if categ:
            categ.pnt_cambio_escandallo = False

        return {'type': 'ir.actions.act_window_close'}

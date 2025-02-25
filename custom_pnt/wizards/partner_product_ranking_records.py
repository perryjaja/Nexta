from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PartnerProductRankingWizard(models.TransientModel):
    _name = 'pnt.partner.product.ranking.records'
    _description = 'Registros del Ranking de ventas de productos'

    ref_interna = fields.Char()
    producto = fields.Many2one(
        comodel_name='product.product',
        string='Producto'
    )
    familia = fields.Many2one(
        comodel_name='product.category',
        string='Familia'
    )
    cantidades = fields.Float()
    importe = fields.Float()
    pnt_detalle = fields.Char(
        string='Detalle',
    )
    pnt_design = fields.Many2one(
        comodel_name='pnt.design',
        string='Design'
    )
    pnt_subdesign = fields.Many2one(
        comodel_name='pnt.subdesign',
        string='Design'
    )
    pnt_format = fields.Many2one(
        comodel_name='pnt.format',
        string='Formato'
    )
    pnt_metal = fields.Many2one(
        comodel_name='pnt.metal',
        string='Metal'
    )
    pnt_stones = fields.Many2one(
        comodel_name='pnt.stones',
        string='Piedras'
    )
    pnt_density = fields.Many2one(
        comodel_name='pnt.density',
        string='Densidad'
    )
    pnt_tipo_metal = fields.Many2one(
        comodel_name='pnt.type.metal',
        string='Tipo Metal'
    )

    def action_create_view_info(self):
        pp_obj = self.env['product.product']
        proveedor = self.env.context.get('proveedor', False)
        fecha_inicial = self.env.context.get('fecha_inicio', False)
        fecha_final = self.env.context.get('fecha_fin', False)
        productos_proveedor = \
            self.env['product.supplierinfo'].search(
                [('name', '=', proveedor),
                 ('pnt_activo', '=', True)]).mapped('product_id')

        sql = """
            SELECT ail.product_id AS Producto, sum(ail.quantity) AS Cantidad, 
            sum(ail.quantity * (ail.price_unit * (1 - (ail.discount/100)))) AS Importe
            FROM account_invoice_line ail
            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN product_product pp ON pp.id = ail.product_id
            WHERE ai.state in ('open','paid') AND ail.product_id in %s AND
            ai.date_invoice between %s and %s AND ai.type = 'out_invoice'
            GROUP BY ail.product_id
        """
        self._cr.execute(sql, (tuple(productos_proveedor.ids), fecha_inicial, fecha_final))
        registros = self._cr.dictfetchall()

        objetos = self.env["pnt.partner.product.ranking.records"]
        for line in registros:
            product = pp_obj.browse(line['producto'])
            objetos |= objetos.create({
                "ref_interna": product.default_code,
                "producto": product.id,
                "familia": product.categ_id.id,
                "cantidades": line['cantidad'],
                "importe": line['importe'],
                "pnt_detalle": product.pnt_detail,
                "pnt_design": product.pnt_design.id or False,
                "pnt_subdesign": product.pnt_subdesign.id or False,
                "pnt_format": product.pnt_format.id or False,
                "pnt_metal": product.pnt_metal.id or False,
                "pnt_stones": product.pnt_stones.id or False,
                "pnt_density": product.pnt_density.id or False,
                "pnt_tipo_metal": product.pnt_tipo_metal.id or False,
            })

        action = self.env.ref("custom_pnt.action_partner_product_ranking_wizard")
        action = action.read()[0]
        action["domain"] = [("id", "in", objetos.ids)]
        return action

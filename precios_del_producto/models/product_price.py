
from odoo import api ,models, fields

class ProductPrice(models.Model):
    _name = 'product.price'

    product_id = fields.Many2one('product.product', string='Producto')

    base_price=fields.Float(string='Base')
    merma=fields.Float(string='Merma')
    peso=fields.Float(string='Peso', related='product_id.weight',default=1.0)
    hechura=fields.Float(string='Hechura')
    escandallo=fields.Float(string='Escandallo')
    prec_vent_unitario=fields.Float(string='Precio venta unitario', compute='_compute_prec_vent_unitario')
    prec_vent_gramo=fields.Float(string='Precio venta gramo',compute='_compute_prec_vent_gramo')
    vent_pieza=fields.Float(string='Venta pieza',compute='_compute_vent_pieza')
    vent_peso=fields.Float(string='Venta peso',compute='_compute_vent_peso')
    sin_merma=fields.Boolean(string='Sin Merma',default=False)
    type_venta=fields.Selection(selection=[
        ('weight', 'Peso'),
        ('pieza', 'Pieza'),
        ('all', 'Todo')
    ],
    String='Tipo de Venta',
    default='weight'
    )


    @api.depends('base_price', 'merma', 'peso', 'hechura')
    def _compute_prec_vent_unitario(self):
        for product_id in self:
            product_id.prec_vent_unitario = ((product_id.base_price + product_id.merma) * product_id.peso) + product_id.hechura

    @api.depends('base_price', 'merma', 'peso', 'hechura', 'escandallo')
    def _compute_prec_vent_gramo(self):
        for product_id in self:
            product_id.prec_vent_gramo = (((product_id.base_price + product_id.merma) * product_id.peso) + product_id.hechura) * product_id.escandallo

    @api.depends('merma', 'hechura', 'escandallo', 'peso')
    def _compute_vent_pieza(self):
        for product_id in self:
            product_id.vent_pieza = (((product_id.base_price+product_id.merma)*product_id.hechura)*product_id.peso)*product_id.escandallo

    @api.depends('merma', 'hechura', 'escandallo', 'peso')
    def _compute_vent_peso(self):
        for product_id in self:
            product_id.vent_peso = ((((product_id.base_price+product_id.merma)/product_id.peso)+product_id.hechura)/product_id.peso)*product_id.escandallo



    @api.onchange('sin_merma')
    def _onchange_type_venta(self):
        if self.sin_merma == True:
            self.prec_vent_gramo = (((self.base_price)*self.peso)+self.hechura)*self.escandallo
            self.prec_vent_unitario = ((self.base_price)*self.peso)+self.hechura
            self.vent_pieza = (((self.base_price) * self.hechura) * self.peso) * self.escandallo
            self.vent_peso = ((((self.base_price) / self.peso) + self.hechura) / self.peso) * self.escandallo

        else:
            self.prec_vent_gramo = (((self.base_price+self.merma) * self.peso) + self.hechura) * self.escandallo
            self.prec_vent_unitario = ((self.base_price+self.merma) * self.peso) + self.hechura
            self.vent_pieza = (((self.base_price+self.merma) * self.hechura) * self.peso) * self.escandallo
            self.vent_peso = ((((self.base_price+self.merma) / self.peso) + self.hechura) / self.peso) * self.escandallo


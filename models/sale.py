from odoo import models, fields, api
from odoo.exceptions import UserError

class EasySalesSale(models.Model):
    _name = 'easy.sales.sale'
    _description = 'Venta'

    customer_id = fields.Many2one('easy.sales.customer', string='Cliente', required=True)
    product_id = fields.Many2one('easy.sales.product', string='Producto', required=True)
    size = fields.Selection([('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], string='Talla', required=True)
    quantity = fields.Integer(string='Cantidad', required=True, default=1)
    price = fields.Float(string='Precio', compute='_compute_price')
    total = fields.Float(string='Total', compute='_compute_total')
    type = fields.Selection([('cash', 'Al Contado'), ('credit', 'Fiada')], string='Tipo', required=True)
    state = fields.Selection([('draft', 'Borrador'), ('confirmed', 'Confirmada')], default='draft')

    @api.depends('product_id')
    def _compute_price(self):
        for sale in self:
            sale.price = sale.product_id.price if sale.product_id else 0

    @api.depends('price', 'quantity')
    def _compute_total(self):
        for sale in self:
            sale.total = sale.price * sale.quantity

    def action_confirm_cash(self):
        self._confirm_sale('cash')

    def action_confirm_credit(self):
        self._confirm_sale('credit')

    def _confirm_sale(self, sale_type):
        self.ensure_one()
        if self.state == 'confirmed':
            raise UserError('Venta ya confirmada.')
        size_line = self.product_id.size_lines.filtered(lambda l: l.size == self.size)
        if not size_line or size_line.stock < self.quantity:
            raise UserError('No hay stock suficiente para esta talla.')
        if sale_type == 'cash':
            size_line.stock -= self.quantity
        else:  # Fiada
            debt = self.env['easy.sales.debt'].create({
                'customer_id': self.customer_id.id,
                'amount': self.total,
                'sale_id': self.id,
            })
        self.state = 'confirmed'
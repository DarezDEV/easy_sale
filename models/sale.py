from odoo import models, fields, api
from odoo.exceptions import UserError

class EasySalesSale(models.Model):
    _name = 'easy.sales.sale'
    _description = 'Venta'

    customer_id = fields.Many2one('easy.sales.customer', string='Cliente', required=True, ondelete='cascade')
    product_id = fields.Many2one('easy.sales.product', string='Producto', required=True, ondelete='cascade')
    size = fields.Selection([('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], string='Talla', required=True)
    quantity = fields.Integer(string='Cantidad', required=True, default=1)
    price = fields.Float(string='Precio', compute='_compute_price')
    total = fields.Float(string='Total', compute='_compute_total')
    type = fields.Selection([('cash', 'Al Contado'), ('credit', 'Fiada')], string='Tipo', required=False)
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
        
        # Actualizar el tipo y estado de venta
        self.write({
            'type': sale_type,
            'state': 'confirmed'
        })
        
        # Reducir el stock en ambos tipos de venta
        size_line.stock -= self.quantity
        
        # Si es fiada, crear la deuda
        if sale_type == 'credit':
            debt = self.env['easy.sales.debt'].create({
                'customer_id': self.customer_id.id,
                'amount': self.total,
                'sale_id': self.id,
            })

    def unlink(self):
        for sale in self:
            # Si la venta está confirmada, devolver el stock
            if sale.state == 'confirmed' and sale.product_id:
                size_line = sale.product_id.size_lines.filtered(lambda l: l.size == sale.size)
                if size_line:
                    size_line.stock += sale.quantity
            
            # Eliminar la deuda asociada si existe
            debt = self.env['easy.sales.debt'].search([('sale_id', '=', sale.id)])
            if debt:
                debt.unlink()
        
        return super().unlink()
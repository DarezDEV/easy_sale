# product.py
from odoo import models, fields, api

class EasySalesProduct(models.Model):
    _name = 'easy.sales.product'
    _description = 'Producto'

    name = fields.Char(string='Nombre', required=True)
    price = fields.Float(string='Precio', required=True)
    category_id = fields.Many2one('easy.sales.category', string='Categoría', ondelete='set null')
    size_lines = fields.One2many('easy.sales.product.size', 'product_id', string='Tallas y Stock')

    @api.depends('size_lines.stock')
    def _compute_total_stock(self):
        for product in self:
            product.total_stock = sum(line.stock for line in product.size_lines)

    total_stock = fields.Integer(string='Stock Total', compute='_compute_total_stock', store=True)

    def unlink(self):
        # Verificar si hay ventas asociadas a este producto
        sales = self.env['easy.sales.sale'].search([('product_id', 'in', self.ids)])
        if sales:
            # Si hay ventas, no permitir eliminar
            from odoo.exceptions import UserError
            raise UserError(f'No se puede eliminar el producto porque tiene {len(sales)} venta(s) asociada(s). Considere archivar el producto en su lugar.')
        
        # Eliminar primero las tallas relacionadas
        for product in self:
            product.size_lines.unlink()
        return super().unlink()

class EasySalesProductSize(models.Model):
    _name = 'easy.sales.product.size'
    _description = 'Talla de Producto'

    product_id = fields.Many2one('easy.sales.product', required=True, ondelete='cascade')
    size = fields.Selection([('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], string='Talla', required=True)
    stock = fields.Integer(string='Stock', default=0)

    @api.onchange('stock')
    def _onchange_stock(self):
        if self.stock < 5:
            return {'warning': {'title': 'Alerta', 'message': 'El stock de esta talla está por agotarse.'}}

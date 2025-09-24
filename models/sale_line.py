# sale_line.py
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class EasySalesSaleLine(models.Model):
    _name = 'easy.sales.sale.line'
    _description = 'Línea de Venta'

    sale_id = fields.Many2one('easy.sales.sale', string='Venta', required=True, ondelete='cascade')
    product_id = fields.Many2one('easy.sales.product', string='Producto', required=True, ondelete='cascade')
    size = fields.Selection([('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], string='Talla', required=True)
    quantity = fields.Integer(string='Cantidad', required=True, default=1)
    unit_price = fields.Float(string='Precio Unitario', compute='_compute_unit_price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('product_id')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = line.product_id.price if line.product_id else 0

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.unit_price * line.quantity

    @api.onchange('product_id', 'size', 'quantity')
    def _onchange_product_size_quantity(self):
        if self.product_id and self.size:
            # Verificar stock disponible
            size_line = self.product_id.size_lines.filtered(lambda l: l.size == self.size)
            if not size_line:
                return {
                    'warning': {
                        'title': 'Talla no configurada',
                        'message': f'El producto {self.product_id.name} no tiene configurada la talla {self.size.upper()}'
                    }
                }
            if size_line.stock < self.quantity:
                return {
                    'warning': {
                        'title': 'Stock Insuficiente',
                        'message': f'Solo hay {size_line.stock} unidades disponibles en talla {self.size.upper()}. Cantidad solicitada: {self.quantity}'
                    }
                }
            elif size_line.stock == 0:
                return {
                    'warning': {
                        'title': 'Sin Stock',
                        'message': f'El producto {self.product_id.name} en talla {self.size.upper()} está agotado'
                    }
                }

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError('La cantidad debe ser mayor a cero.')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create para validar stock al crear líneas"""
        lines = super().create(vals_list)
        for line in lines:
            # Solo validar si la venta no está confirmada aún
            if line.sale_id.state == 'draft':
                try:
                    line._check_stock_availability()
                except UserError:
                    # Si no hay stock pero la venta está en borrador, solo mostrar warning
                    pass
        return lines

    def write(self, vals):
        """Override write para validar stock al modificar líneas"""
        result = super().write(vals)
        if any(key in vals for key in ['product_id', 'size', 'quantity']):
            for line in self:
                # Solo validar si la venta no está confirmada aún
                if line.sale_id.state == 'draft':
                    try:
                        line._check_stock_availability()
                    except UserError:
                        # Si no hay stock pero la venta está en borrador, solo mostrar warning
                        pass
        return result

    def _check_stock_availability(self):
        """Verifica si hay stock suficiente para esta línea"""
        if not self.product_id or not self.size:
            raise UserError('Debe seleccionar un producto y una talla.')
            
        size_line = self.product_id.size_lines.filtered(lambda l: l.size == self.size)
        if not size_line:
            raise UserError(f'El producto "{self.product_id.name}" no tiene configurada la talla {self.size.upper()}. Configure el stock primero.')
            
        if size_line.stock <= 0:
            raise UserError(f'El producto "{self.product_id.name}" en talla {self.size.upper()} está AGOTADO (Stock actual: 0)')
            
        if size_line.stock < self.quantity:
            raise UserError(f'Stock insuficiente para "{self.product_id.name}" talla {self.size.upper()}.\nStock disponible: {size_line.stock}\nCantidad solicitada: {self.quantity}')
            
        return size_line

    def _reduce_stock(self):
        """Reduce el stock del producto en la talla especificada"""
        size_line = self._check_stock_availability()
        size_line.stock -= self.quantity

    def _restore_stock(self):
        """Restaura el stock cuando se cancela una venta"""
        size_line = self.product_id.size_lines.filtered(lambda l: l.size == self.size)
        if size_line:
            size_line.stock += self.quantity
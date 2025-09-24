from odoo import models, fields, api
from odoo.exceptions import UserError

class EasySalesSale(models.Model):
    _name = 'easy.sales.sale'
    _description = 'Venta'

    customer_id = fields.Many2one('easy.sales.customer', string='Cliente', required=True, ondelete='cascade')
    line_ids = fields.One2many('easy.sales.sale.line', 'sale_id', string='Productos')
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    type = fields.Selection([('cash', 'Al Contado'), ('credit', 'Fiada')], string='Tipo', required=False)
    state = fields.Selection([('draft', 'Borrador'), ('confirmed', 'Confirmada')], default='draft')
    date = fields.Date(string='Fecha', default=fields.Date.today)

    # Campos heredados que ya no se usan directamente pero mantenemos para compatibilidad
    product_id = fields.Many2one('easy.sales.product', string='Producto (Obsoleto)', help='Campo mantenido por compatibilidad')
    size = fields.Selection([('s', 'S'), ('m', 'M'), ('l', 'L'), ('xl', 'XL')], string='Talla (Obsoleto)')
    quantity = fields.Integer(string='Cantidad (Obsoleto)', default=1)
    price = fields.Float(string='Precio (Obsoleto)')

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for sale in self:
            sale.total = sum(line.subtotal for line in sale.line_ids)

    @api.model
    def create(self, vals):
        # Si se está creando desde la interfaz antigua (con product_id), crear la línea automáticamente
        if vals.get('product_id') and not vals.get('line_ids'):
            line_vals = {
                'product_id': vals['product_id'],
                'size': vals.get('size'),
                'quantity': vals.get('quantity', 1),
            }
            vals['line_ids'] = [(0, 0, line_vals)]
        return super().create(vals)

    def action_confirm_cash(self):
        self._confirm_sale('cash')

    def action_confirm_credit(self):
        self._confirm_sale('credit')

    def _confirm_sale(self, sale_type):
        self.ensure_one()
        if self.state == 'confirmed':
            raise UserError('Venta ya confirmada.')
        
        if not self.line_ids:
            raise UserError('No se puede confirmar una venta sin productos.')
        
        # Verificar stock para todas las líneas antes de procesar
        stock_errors = []
        for line in self.line_ids:
            try:
                line._check_stock_availability()
            except UserError as e:
                stock_errors.append(str(e))
        
        # Si hay errores de stock, mostrarlos todos
        if stock_errors:
            error_message = "No se puede confirmar la venta por problemas de stock:\n\n" + "\n".join([f"• {error}" for error in stock_errors])
            raise UserError(error_message)
        
        # Si todo está bien, procesar la venta
        self.write({
            'type': sale_type,
            'state': 'confirmed'
        })
        
        # Reducir stock para todas las líneas
        for line in self.line_ids:
            line._reduce_stock()
        
        # Si es fiada, crear la deuda
        if sale_type == 'credit':
            self.env['easy.sales.debt'].create({
                'customer_id': self.customer_id.id,
                'amount': self.total,
                'sale_id': self.id,
            })

    def action_add_product(self):
        """Acción para agregar un nuevo producto a la venta"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Agregar Producto',
            'res_model': 'easy.sales.sale.line',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_id': self.id,
            },
        }

    def unlink(self):
        for sale in self:
            # Si la venta está confirmada, devolver el stock
            if sale.state == 'confirmed':
                for line in sale.line_ids:
                    line._restore_stock()
            
            # Eliminar la deuda asociada si existe
            debt = self.env['easy.sales.debt'].search([('sale_id', '=', sale.id)])
            if debt:
                debt.unlink()
        
        return super().unlink()

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        """Actualiza campos de compatibilidad cuando cambian las líneas"""
        if self.line_ids:
            first_line = self.line_ids[0]
            self.product_id = first_line.product_id
            self.size = first_line.size
            self.quantity = first_line.quantity
            self.price = first_line.unit_price
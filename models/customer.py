# customer.py
from odoo import models, fields
from odoo.exceptions import UserError

class EasySalesCustomer(models.Model):
    _name = 'easy.sales.customer'
    _description = 'Cliente'

    name = fields.Char(string='Nombre', required=True)
    phone = fields.Char(string='Teléfono')
    sale_ids = fields.One2many('easy.sales.sale', 'customer_id', string='Ventas')
    debt_ids = fields.One2many('easy.sales.debt', 'customer_id', string='Deudas')

    def action_view_history(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Historial de Compras',
            'res_model': 'easy.sales.sale',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
        }

    def unlink(self):
        for customer in self:
            # Verificar si hay ventas
            if customer.sale_ids:
                raise UserError(f'No se puede eliminar el cliente "{customer.name}" porque tiene {len(customer.sale_ids)} venta(s) registrada(s).')
            
            # Verificar si hay deudas
            if customer.debt_ids:
                raise UserError(f'No se puede eliminar el cliente "{customer.name}" porque tiene {len(customer.debt_ids)} deuda(s) pendiente(s).')
        
        return super().unlink()
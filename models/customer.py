from odoo import models, fields

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
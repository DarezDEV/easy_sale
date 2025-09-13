from odoo import models, fields, api

class EasySalesDebt(models.Model):
    _name = 'easy.sales.debt'
    _description = 'Deuda'

    customer_id = fields.Many2one('easy.sales.customer', string='Cliente', required=True)
    sale_id = fields.Many2one('easy.sales.sale', string='Venta Asociada')
    amount = fields.Float(string='Monto Pendiente', required=True)
    payment_ids = fields.One2many('easy.sales.payment', 'debt_id', string='Pagos')

    def action_register_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar Pago',
            'res_model': 'easy.sales.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_debt_id': self.id},
        }

class EasySalesPayment(models.Model):
    _name = 'easy.sales.payment'
    _description = 'Pago'

    debt_id = fields.Many2one('easy.sales.debt', required=True)
    amount = fields.Float(string='Monto Pagado', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.today)

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec.debt_id.amount -= vals['amount']
        return rec
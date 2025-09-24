from odoo import models, fields
from odoo.exceptions import UserError

class EasySalesCategory(models.Model):
    _name = 'easy.sales.category'
    _description = 'Categoría de Producto'

    name = fields.Char(string='Nombre', required=True)

    def unlink(self):
        for category in self:
            # Verificar si hay productos usando esta categoría
            products = self.env['easy.sales.product'].search([('category_id', '=', category.id)])
            if products:
                raise UserError(f'No se puede eliminar la categoría "{category.name}" porque tiene {len(products)} producto(s) asociado(s). '
                               f'Elimine o reasigne los productos primero.')
        return super().unlink()
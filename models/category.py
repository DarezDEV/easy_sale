from odoo import models, fields

class EasySalesCategory(models.Model):
    _name = 'easy.sales.category'
    _description = 'Categoría de Producto'

    name = fields.Char(string='Nombre', required=True)
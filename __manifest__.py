{
    'name': 'Easy Sales V',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Módulo simple para gestión de ventas en tienda física',
    'description': 'Resuelve problemas de stock, ventas y deudas para tiendas pequeñas.',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/customer_views.xml',
        'views/sale_views.xml',
        'views/debt_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
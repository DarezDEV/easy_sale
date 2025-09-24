{
    'name': 'Solución de Ventas',
    'version': '1.1',
    'category': 'Sales',
    'summary': 'Módulo simple para gestión de ventas en tienda física con múltiples productos por venta',
    'description': 'Módulo profesional para la gestión integral de ventas en tiendas físicas. Permite controlar el inventario en tiempo real, administrar clientes, registrar ventas y gestionar deudas de manera eficiente. Ideal para pequeños comercios que buscan optimizar sus procesos comerciales y mejorar la toma de decisiones.',
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
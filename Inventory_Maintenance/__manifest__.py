{
    'name': 'Product Maintenance',
    'version': '1.0',  # Update this line
    'sequence': 1,
    'category': 'Inventory',
    'summary': 'Add maintenance capability to products',
    'description': """
        This module allows you to mark products as subject to maintenance and manage their associated equipment.
    """,
    'author': 'Doodex',
    'depends': ['product', 'maintenance', 'mrp', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_template_search_views.xml',
        'views/maintenance_equipment_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'Inventory_Maintenance/static/src/js/product_template.js',
        ],
    },
    'installable': True,
    'application': True,
}



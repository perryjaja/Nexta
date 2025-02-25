# -*- coding: utf-8 -*-
# (c) 2025 Nexta - Jaume Basiero <jbasiero@nextads.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/a
{
    'name': "Variantes de producto",

    'summary': """
        Este módulo añade personalizaciones a los productos y las variantes de los productos
                
    """,

    'description': """
        Este módulo añade personalizaciones a los productos y las variantes de los productos

    """,

    'author': "NextaDS",
    'website': "http://www.nextads.es",
    'license': "LGPL-3",

    'category': 'Product',
    'version': '17.0.0.1',

    'depends': ['stock',
                'product',
                ],

    'data': [
        'views/product_template.xml',
        'views/product_product.xml',
    ],
}

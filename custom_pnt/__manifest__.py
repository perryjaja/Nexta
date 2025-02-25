# -*- coding: utf-8 -*-
{
    'name': "Custom Pnt",
    'version': '17.0.0.1',
    'author': 'Carlos Ramos Hernández (Punt Sistemes)',
    'website': '',
    'sequence': 1,
    'category': 'Specific Modules',
    'summary': 'Personalizaciones Cliente',
    'depends': [
        'sales_team',
        'account',
        'account_due_list',
        'account_financial_report',
        'product',
        'stock',
        'account_payment_partner',
        'account_payment_order',
        'account_payment_return',
        'sale_stock',
        'sale_management',
        'purchase_discount',
        'purchase_last_price_info',
        # 'stock_available_unreserved', Sin migrar
        'stock_picking_invoice_link',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/lorente_security_pnt.xml',
        'views/templates.xml',
        'views/stock_picking_type_views.xml',
        'views/res_company.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'views/product_category.xml',
        'views/pnt_product_configuration.xml',
        'views/res_partner.xml',
        'views/account_invoice.xml',
        'views/purchase_order.xml',
        'views/stock_picking.xml',
        'views/sale_order_views.xml',
        'views/account_security_views.xml',
        'views/account_move_line_view.xml',
        'views/product_supplierinfo_view.xml',
        'wizards/product_category_escandallo_wizard.xml',
        'wizards/open_items_wizard_view.xml',
        'wizards/partner_product_ranking_wizard.xml',
        'wizards/partner_product_ranking_records.xml',
        'wizards/product_replenish_views.xml',
    ],
    'qweb': ['static/src/xml/template.xml'],
    'css': ['static/src/css/style.css'],

    'installable': True,
    'application': False,
    'auto_install': False,
    'description': """
Descripción
===========

Personalizaciones cliente

Configuración
=============


Limitaciones/Problemas
======================
No se conocen.

Registro de cambios
===================
12.0.1.0.0:

Desarrollo inicial.

"""
}

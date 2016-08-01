# -*- coding: utf-8 -*-
{
    'name': "nantian_erp",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Nantian",
    'website': "http://www.nantian.com.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'nantianerp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr','project','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/server_desk_security.xml',
        'views/nantian_erp_view.xml',
        'views/nantian_erp_menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'application': True,
}

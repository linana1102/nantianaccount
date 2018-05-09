# -*- coding: utf-8 -*-
{
    'name': "nantian_account",

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
    'category': 'nantianaccount',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr','project','resource','base_action_rule','hr_attendance'],

    # always loaded
    'data': [
        # 'security/account.xml',
        'security/ir.model.access.csv',
        'views/sign.xml',
        # 'views/export_resume.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'application': True,
}

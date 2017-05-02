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
    'depends': ['base','mail','hr','project','resource','base_action_rule','hr_attendance'],

    # always loaded
    'data': [
        'security/nantian_erp_security.xml',
        'security/ir.model.access.csv',
        'views/nantian_erp_hr_view.xml',
        'views/nantian_erp_contract_view.xml',
        'views/nantian_erp_work_team_view.xml',
        'views/nantian_erp_view.xml',
        'views/nantian_erp_menu.xml',
        'views/dimission_workflow.xml',
        'views/leave_workflow.xml',
        'views/nantian_erp_cron.xml',
        'views/nantian_erp_auto_action.xml',
        'views/nantian_erp_link.xml',
        'views/nantian_erp_project_view.xml',
        'views/nantian_erp_ip_data_menu.xml',
        'views/sale.xml',
        'views/job.xml',
        'views/human_cost.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'application': True,
    'qweb':[
        'static/xml/nantian_view.xml',
    ],
}

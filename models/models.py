# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api
from email.utils import formataddr
import email,math
from email.header import Header
from datetime import datetime,timedelta

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    project_id = fields.Many2one('project.project',ondelete='set null',)
    analytic_line_id = fields.Many2one('account.analytic.line',ondelete='set null',)
    project_parent_id = fields.Many2one('account.analytic.account',compute='_compute_parent_project',store=True)
    certificate_ids = fields.One2many('nantian_erp.certificate','employee_ids',ondelete = 'set null',string="证书")
    graduation = fields.Char(string="毕业学校")    
    major = fields.Char(string='专业')
    work_time = fields.Date()
    entry_time = fields.Date()
    contract_starttime = fields.Date()
    contract_endtime = fields.Date(store=True,compute='_get_end_date')
    contract_len = fields.Integer()
    education = fields.Selection(
        [
            (u'专科', u"专科"),
            (u'本科', u"本科"),
            (u'硕士', u"硕士"),
            (u'博士', u"博士"),
            (u'专升本', u"专升本"),
            (u'高级技工', u"高级技工"),
            (u'高中', u"高中"),
        ]

    )
    level = fields.Selection(
        [
            (u'1',1),
            (u'2',2),
            (u'3',3),
            (u'4',4),
            (u'5',5),
            (u'6',6),
            (u'7',7),
            (u'8',8),
            (u'9',9),
        ]
    )
    category = fields.Selection(
        [
            (u'在公司', u"在公司"),
            (u'在合同中', u"在合同中"),
            (u'赠送', u"赠送"),
            (u'开发', u"开发"),
            (u'其他', u"其他"),
        ],
    default = u'在公司', string = "人员所属"
    )
    specialty = fields.Text(string="特长")
    certificate_direction_id = fields.Many2one(related='certificate_ids.certificate_direction_id', string='证书方向')
    certificate_category_id = fields.Many2one(related='certificate_ids.certificate_category_id', string='证书认证类型')
    certificate_institutions_id = fields.Many2one(related='certificate_ids.certificate_institutions_id', string='证书颁发机构或行业')
    certificate_level_id = fields.Many2one(related='certificate_ids.certificate_level_id', string='证书级别')
    dimission_why=fields.Selection(
        [
            (u'薪资待遇不满意', u"薪资待遇不满意"),
            (u'工作环境不满意', u"工作环境不满意"),
            (u'工作发展方向不满意', u"工作发展方向不满意"),
            (u'有更好的公司选择', u"有更好的公司选择"),
            (u'家庭原因', u"家庭原因"),
            (u'身体原因',u'身体原因'),
            (u'其他',u'其他'),
        ],
        string="离职原因")
    dimission_goto = fields.Text(string="离职去向")
    dimission_why_add = fields.Text(string="其他原因")

    @api.depends('project_id')
    def _compute_parent_project(self):
        for record in self:
            record.project_parent_id = record.project_id.parent_id
    #@api.multi
    #@api.onchange('project_id')
    #def _onchange_analytic_line_id(self):
        #self.analytic_line_id.name_get(self.project_id.analytic_account_id)
       
    @api.one
    @api.depends('contract_starttime', 'contract_len')
    def _get_end_date(self):
        if not (self.contract_starttime and self.contract_len):
            self.contract_endtime = self.contract_starttime
            return
        start=fields.Datetime.from_string(self.contract_starttime)
        self.contract_endtime =datetime(start.year+self.contract_len,start.month,start.day)
    
class project_project(models.Model):
    _inherit = 'project.project'

    employee_ids = fields.One2many('hr.employee','project_id','Employee')
    need_employee_count = fields.Integer()
    employee_count = fields.Integer(compute='_count_employees', store=True)

    @api.depends('employee_ids')
    def _count_employees(self):
        for employee in self.employee_ids:
            self.message_subscribe([employee.user_id.partner_id.id])
        for record in self:
            record.employee_count = len(record.employee_ids)

    @api.multi
    @api.depends('name', 'need_employee_count')
    def name_get(self):
        return [(r.id, (r.name + '-' + u'所需人数' + (str(r.need_employee_count)) + u'人')) for r in self]

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    employee_ids = fields.One2many('hr.employee','analytic_line_id',"Employees")
    employee_count = fields.Integer(compute='_count_employees',store=True)

    @api.depends('employee_ids')
    def _count_employees(self):
        for record in self:
            record.employee_count = len(record.employee_ids) 

    @api.multi
    @api.depends('name','product_id')
    def name_get(self):
       return [(r.id,(r.name+'('+(r.product_id.name)+')')) for r in self]

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    need_employee_count = fields.Integer(compute='_need_count_employees',store=True)

    @api.depends('line_ids')
    def _need_count_employees(self):
        for record in self:
            record.enee_mployee_count = 0
            for line in self.line_ids:
                record.need_employee_count += line.employee_count

    @api.multi
    @api.depends('name', 'employee_count')
    def name_get(self):
        return [(r.id, (r.name + '-'+u'所需人数'+  (str(r.need_employee_count)) +u'人')) for r in self]

class certificate(models.Model):
    _name = 'nantian_erp.certificate'
    _rec_name = 'name'
    name = fields.Char(related='certificate_direction_id.name', store=True)
    certificate_direction_id= fields.Many2one('nantian_erp.certificate_direction',string='方向')
    certificate_category_id = fields.Many2one('nantian_erp.certificate_category', string='认证类型')
    certificate_institutions_id = fields.Many2one('nantian_erp.certificate_institutions', string='颁发机构或行业')
    certificate_level_id = fields.Many2one('nantian_erp.certificate_level', string='级别')
    time = fields.Date(required=True,placeholder="截止日期",string="有效期")
    employee_ids = fields.Many2one('hr.employee',ondelete='set null')

class certificate_category(models.Model):
    _name = 'nantian_erp.certificate_category'
    _rec_name = 'name'
    name = fields.Char(required=True, string='认证类型')

class certificate_institutions(models.Model):
    _name = 'nantian_erp.certificate_institutions'
    _rec_name = 'name'
    name = fields.Char(string='机构')
    category_id = fields.Many2one('nantian_erp.certificate_category', ondelete='set null', select=True)

class certificate_direction(models.Model):
    _name = 'nantian_erp.certificate_direction'
    _rec_name = 'name'
    name = fields.Char(string='方向')
    institutions_id = fields.Many2one('nantian_erp.certificate_institutions', ondelete='set null', select=True)

class certificate_level(models.Model):
    _name = 'nantian_erp.certificate_level'
    _rec_name = 'name'
    name = fields.Char(string='级别')
    direction_id = fields.Many2one('nantian_erp.certificate_direction', ondelete='set null', select=True)


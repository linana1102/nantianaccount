# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions

class categroy(models.Model):
    _name = 'nantian_erp.categroy'
    name = fields.Char()

class jobs(models.Model):
    _name = 'nantian_erp.job'

    name = fields.Char(string='名称')
    categroy_id = fields.Many2one('nantian_erp.categroy',string='岗位类别')

class job_categroy(models.Model):
    _name = 'nantian_erp.job_categroy'

    name = fields.Char(string='类别')
    job_id = fields.Many2one('nantian_erp.job',string='职位')

class recruitment(models.Model):
    _name = 'nantian_erp.recruitment'

    user_id = fields.Many2one('res.users',default=lambda self: self.env.user)

    department_id = fields.Many2one('hr.department',string='部门',default=lambda self: self.compute_department(),store=True)
    working_team_id = fields.Many2one('nantian_erp.working_team',string='工作组',)
    position_categroy_1 = fields.Many2one('nantian_erp.categroy',string='岗位类别')
    job_id =fields.Many2one('nantian_erp.job',string='职位',)
    job_name = fields.Char(related='job_id.name')
    position_categroy_2 = fields.Many2one('nantian_erp.job_categroy')
    job_level = fields.Selection([(u'1',u'1'),(u'2',u'2'),(u'3',u'3')],string='职级')
    duties = fields.Text(string= '职责')
    requirements = fields.Text(string='要求')
    salary = fields.Char(string='薪资')
    current_employee_num = fields.Integer(string='现有人数')
    need_people_num = fields.Integer(string='招聘人数')
    reason = fields.Selection([('1','原有人员离职后增补人员'),('2','业务拓展后新增岗位'),('3','其他')])
    channel = fields.Selection([('1','招聘网站发布职位'),('2','伯乐奖职位'),('3','其他渠道')])
    cycle = fields.Char(string='招聘周期')
    state = fields.Selection([(u'审批中', u'审批中'), (u'已发布',u'已发布'),(u'被退回',u'被退回') ,(u'已取消',u'已取消')],default=u'审批中')
    examine_user = fields.Many2one('res.users',string='审批人',default=lambda self: self.compute_working_team())

    @api.multi
    @api.depends('user_id')
    def compute_department(self):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        return employee.department_id

    @api.multi
    @api.depends('user_id')
    def compute_working_team(self):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        return employee.working_team_id

    @api.multi
    def compute_examine_user(self):
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')],limit=1)
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        department =employee.department_id
        if self.env.user in customer_manager_group.users:
            if department.level == 2:
                return department.manager_id.user_id
            else:
                return department.parent_id.manager_id.user_id
        else:
            return employee.working_team_id.partner_id.customer_manager




class job_examine(models.Model):
    _name = 'nantian_erp.job_examine'

    user_id = fields.Many2one('res.users',string='审批人')
    result = fields.Selection([(u'同意',u'同意'),(u'不同意',u'不同意')])
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘需求')
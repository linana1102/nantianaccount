# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions

class jobs(models.Model):
    _name = 'nantian_erp.job'

    name = fields.Char(string='名称')
    categroy = fields.Selection([(u'系统',u'系统'),(u'网络',u'网络'),(u'开发',u'开发')],string='岗位类别')


class recruitment(models.Model):
    _name = 'nantian_erp.recruitment'

    user_id = fields.Many2one('res.users',default=lambda self: self.env.user)
    level_1_department_id = fields.Many2one('hr.department',string='一级部门')
    level_2_department_id = fields.Many2one('hr.department',string='二级部门')
    working_team = fields.Many2one('nantian_erp.working_team',string='工作组')
    position_categroy = fields.Selection([(u'系统',u'系统'),(u'网络',u'网络'),(u'开发',u'开发')],string= '岗位类别')
    job_id =fields.Many2one('nantian_erp.job',string='职位',)
    job_level = fields.Selection([(u'1',u'1'),(u'2',u'2'),(u'3',u'3')],string='职级')
    duties = fields.Text(string= '职责')
    requirements = fields.Text(string='要求')
    salary = fields.Char(string='薪资')
    current_employee_num = fields.Integer(string='现有人数')
    need_people_num = fields.Integer(string='招聘人数')
    reason = fields.Selection([('1','原有人员离职后增补人员'),('2','业务拓展后新增岗位'),('3','其他')])
    channel = fields.Selection([('1','招聘网站发布职位'),('2','伯乐奖职位'),('3','其他渠道')])
    cycle = fields.Char(string='招聘周期')
    state = fields.Selection([(u'需求方', u'需求方'), (u'行业负责人',u'行业负责人'),(u'总经理',u'总经理') ,(u'取消',u'取消'),(u'发布',u'发布')])
    examine_user = fields.Many2one('res.users',string= '审批人')


class job_examine(models.Model):
    _name = 'nantian_erp.job_examine'

    user_id = fields.Many2one('res.users',string='审批人')
    result = fields.Selection([(u'同意',u'同意'),(u'不同意',u'不同意')])
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘需求')
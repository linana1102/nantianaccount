# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
from datetime import datetime,timedelta
import time
import string
import logging
import sys




class performance_note(models.Model):
    _name = 'nantian_erp.performance_note'
    _rec_name = 'title'

    title = fields.Char(string="选项名")
    performance_month_id = fields.Many2one('nantian_erp.performance_month',string="绩效单")
    text = fields.Char(string="备注")


class performance_month(models.Model):
    _name = 'nantian_erp.performance_month'

    performance_year_id = fields.Many2one('nantian_erp.performance_year',string="员工年绩效")
    employee_id = fields.Many2one('hr.employee',string="员工姓名")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],related='employee_id.gender',string="性别")
    department_id = fields.Many2one(related='employee_id.department_id',string="一级部门（数据中心服务部）",store = True)
    department_first = fields.Char(string="一级部门",compute = 'get_department_level',store = True)
    department_second = fields.Char(string="二级部门",compute = 'get_department_level',store = True)
    department_third = fields.Many2one(related='employee_id.working_team_id',string="三级工作组",store = True)
    month_percent = fields.Float(string="本月绩效百分比" ,default = 1)
    month_performance = fields.Float(string="本月绩效")
    note_ids = fields.One2many('nantian_erp.performance_note','performance_month_id',string="备注")# 助理可以添加选项
    date = fields.Date(string="绩效日期")



    @api.multi
    @api.depends('department_id','department_third')
    def get_department_level(self):
        for record in self:
            if record.department_id.level == 1:
                pass
            elif record.department_id.level == 2:
                record.department_first = record.department_id.name
            elif record.department_id.level == 3:
                record.department_first = record.department_id.parent_id.name
                record.department_second = record.department_id.name
            else:
                pass

    # 每个月自动创建月绩效表
    @api.multi
    def create_month_performance(self):
        for record in self:
            pass


class performance_year(models.Model):
    _name = 'nantian_erp.performance_year'

    employee_id = fields.Many2one('hr.employee',string="员工姓名")
    performance_month_ids = fields.One2many('nantian_erp.performance_month','performance_year_id',string="员工姓名")
    working_team_id = fields.Many2one(related='employee_id.working_team_id',string="所在项目组")
    month_count = fields.Float(string="工作月度")
    wages = fields.Float(string="税前工资")
    base_protect = fields.Float(string="社保基数")
    pay_of_company = fields.Float(string="社保+公积金(公司缴纳部分)",compute = 'compute_kinds_cost',store = True)
    performance_month = fields.Float(string="月度绩效")
    union_funds_month = fields.Float(string="工会经费(月度)" ,compute = 'compute_kinds_cost',store = True)
    grants_year = fields.Float(string="补助(年度)")
    variable_expenses = fields.Float(string="变动费用(年度)")
    performance_year = fields.Float(string="年终绩效")
    project_human_cost = fields.Float(string="项目人力成本(年度)" ,compute = 'compute_kinds_cost',store = True)
    total_year = fields.Float(string="人力成本合计(年度)",compute = 'compute_kinds_cost',store = True)

    @api.multi
    @api.depends('month_count','wages','base_protect','pay_of_company',\
                 'performance_month','union_funds_month','grants_year',\
                 'variable_expenses','performance_year','project_human_cost')
    def compute_kinds_cost(self):
        for record in self:
            if record.base_protect > 2834:
                m1 = record.base_protect*0.19
            else:
                m1 = 2834*0.19
            if record.base_protect > 2834:
                m2 = record.base_protect * 0.008
            else:
                m2 = 2834 * 0.008
            if record.base_protect > 4252:
                m3 = record.base_protect * 0.002
            else:
                m3 = 4252 * 0.002
            if record.base_protect > 4252:
                m4 = record.base_protect * 0.1
            else:
                m4 = 4252 * 0.1
            if record.base_protect > 4252:
                m5 = record.base_protect * 0.008
            else:
                m5 = 4252 * 0.008
            record.pay_of_company = record.wages*0.12 + m1 + m2 + m3 + m4 + m5
            record.union_funds_month = record.wages*0.02
            record.project_human_cost = (record.wages + record.pay_of_company + record.performance_month\
            + record.union_funds_month) * record.month_count + record.grants_year\
            + record.variable_expenses + record.performance_year
            record.total_year = record.project_human_cost



    # 每年自动创建年绩效表
    @api.multi
    def create_year_performance(self):
        now = fields.datetime.now()
        records = self.env['hr.employnee'].search([])
        for record in records:
            for i in record.performance_year_ids:
                if i.create_date:

                    pass


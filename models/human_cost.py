# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
import datetime
import time
import string
import logging
import sys

class variable_expenses(models.Model):
    _name = 'nantian_erp.variable_expenses'


    email = fields.Char(string="员工邮箱")# 导一个即可
    # name = fields.Char(string="姓名")
    employee_id = fields.Many2one('hr.employee',compute = 'match_workingteam_and_employee',store = True)
    workteam_name = fields.Char(string="工作组名称")
    work_team_id = fields.Many2one('nantian_erp.working_team',compute = 'match_workingteam_and_employee',store = True)
    cost = fields.Float(string="变动费用")
    date = fields.Date(string="费用日期")
    project_cost_month_id = fields.Many2one('nantian_erp.project_cost_month',compute = 'match_workingteam_and_employee',store = True)
    employee_month_cost_id = fields.Many2one('nantian_erp.employee_month_cost',compute = 'match_workingteam_and_employee',store = True)

    # 触动找到人员找到工作组
    @api.multi
    @api.depends('email','workteam_name','work_team_id','employee_id',"employee_month_cost_id")
    def match_workingteam_and_employee(self):
        DATE_FORMAT = "%Y-%m-01"
        for x in self:
            employee_id = self.env['hr.employee'].search([("user_id.email", "=", x.email)])
            if x.date:
                Date = datetime.datetime.strftime(x.date, DATE_FORMAT)  # 日期转化为字符串
                if employee_id:
                    x.employee_id = employee_id[0].id
                work_team_id = self.env['nantian_erp.working_team'].search([("name", "=", x.workteam_name)])
                if work_team_id:
                    x.work_team_id = work_team_id[0].id
                if x.employee_id:
                    employee_month_cost_ids = self.env['nantian_erp.employee_month_cost'].search(
                        [("employee_id", "=", x.employee_id.id), ("create_date", ">=", Date)])
                    if employee_month_cost_ids:
                        x.employee_month_cost_id = employee_month_cost_ids[0].id
                if x.work_team_id:
                    project_cost_month_ids = self.env['nantian_erp.project_cost_month'].search(
                        [("working_team_id", "=", x.work_team_id.id), ("create_date", ">=", Date)])
                    if project_cost_month_ids:
                        x.project_cost_month_id = project_cost_month_ids[0].id




class performance_note(models.Model):
    _name = 'nantian_erp.performance_note'
    _rec_name = 'title'

    title = fields.Char(string="选项名")
    performance_month_id = fields.Many2one('nantian_erp.performance_month',string="绩效单",readonly = True)
    text = fields.Char(string="备注")


class performance_month(models.Model):
    _name = 'nantian_erp.performance_month'

    performance_year_id = fields.Many2one('nantian_erp.performance_year',string="员工年绩效")
    employee_id = fields.Many2one(related='performance_year_id.employee_id',string="员工姓名",store = True,readonly = True)
    gender = fields.Selection([('male','Male'), ('female', 'Female')],related='employee_id.gender',string="性别",readonly = True)
    department_first = fields.Char(related='performance_year_id.department_first',string="一级部门",store = True,readonly = True)
    department_second = fields.Char(related='performance_year_id.department_second',string="二级部门",store = True,readonly = True)
    department_third = fields.Many2one(related='performance_year_id.employee_id.working_team_id',string="三级工作组",store = True,readonly = True)
    department_third_name = fields.Char(string="工作组",compute='split_workteam_name',store = True)
    month_percent = fields.Float(string="本月绩效百分比" ,default = 1)
    month_performance = fields.Float(string="本月绩效")
    #note_ids = fields.One2many('nantian_erp.performance_note','performance_month_id',string="备注")# 助理可以添加选项
    date = fields.Date(string="绩效日期")
    note = fields.Char(string="备注")

    @api.depends("department_third",'month_performance',"performance_year_id")
    @api.multi
    def split_workteam_name(self):
        for x in self:
            x.department_third_name = x.department_third.name
        #根据邮箱找到这个人的绩效


class worktime_in_project(models.Model):
    _name = 'nantian_erp.worktime_in_project'

    # 用来保存每个人进入项目和出项目的时间
    # 来源有人员调动表，人员离职表
    working_team_id = fields.Many2one('nantian_erp.working_team',string="工作组(项目)名称")
    partner_id = fields.Many2one(related='working_team_id.partner_id',string="行业(客户)")
    enter_date = fields.Date(string='进入项目时间')
    exit_date = fields.Date(string='离开项目时间')
    employee_id = fields.Many2one('hr.employee',string="员工姓名")

    # 自动化给每个人一个项目开始的时间
    # 字符串转换为日期时间：datetime.datetime.strptime(sale.date, DATE_FORMAT)
    # 日期时间转换为字符串：datetime.datetime.strftime(datetime.date.today(), DATE_FORMAT)
    @api.multi
    def make_worktime_enter_date(self):
        print "开始添加++++++++++"
        YEAR_FORMAT = "%Y-01-01"
        now = fields.datetime.now()
        CreateYDate = datetime.datetime.strftime(now, YEAR_FORMAT)
        records = self.env['hr.employee'].search([])
        for record in records:
            id = self.env['nantian_erp.worktime_in_project'].search([("employee_id","=",record.id),("working_team_id","=",record.working_team_id.id)])
            if id:
                pass
            else:
                if record.entry_time and record.entry_time <= CreateYDate:
                    id = self.env['nantian_erp.worktime_in_project'].create(
                        {"employee_id": record.id, "working_team_id": record.working_team_id.id,"enter_date":CreateYDate})
                elif record.entry_time and record.entry_time > CreateYDate:
                    id = self.env['nantian_erp.worktime_in_project'].create(
                        {"employee_id": record.id, "working_team_id": record.working_team_id.id, "enter_date": record.entry_time})
                else:
                    pass

class project_cost_month(models.Model):
    _name = 'nantian_erp.project_cost_month'

    working_team_id = fields.Many2one('nantian_erp.working_team',string="工作组(项目)名称")
    workteam_name = fields.Char(string="工作组",compute='split_workteam_name',store = True)
    # 这个relate怎么写？
    # employee_ids = fields.One2many(related = 'working_team_id.employee_ids',string="工作组(人员)名称",store = True)
    partner_id = fields.Many2one("res.partner",compute = "split_workteam_name",string="行业(客户)",store=True)
    month_cost = fields.Float(compute='compute_month_workteam_cost',string = '工作组月总计',store = True)
    variable_expenses_ids = fields.One2many('nantian_erp.variable_expenses','project_cost_month_id',string="人员月变动费用")
    variable_expenses = fields.Float(compute='compute_month_workteam_cost',string="工作组变动费用(月计)",store = True)
    project_cost_year_id = fields.Many2one('nantian_erp.project_cost',string="工作组(项目)年")

    @api.depends("working_team_id","variable_expenses")
    @api.multi
    def split_workteam_name(self):
        for x in self:
            x.workteam_name = x.working_team_id.name
            x.partner_id = x.working_team_id.partner_id.id
            # 根据邮箱找到这个人的绩效


    #每个月项目要花多少钱，这个位置还没有把工作项目时长加进去
    @api.multi
    @api.depends('working_team_id','variable_expenses')
    def compute_month_workteam_cost(self):
        employees_cost = 0
        DATE_FORMAT = "%Y-%m-01"
        for x in self:
            if x.variable_expenses_ids:
                for var in x.variable_expenses_ids:
                    if var.cost:
                        x.variable_expenses = x.variable_expenses + var.cost
            if x.create_date:
                CreateDate = fields.Datetime.from_string(x.create_date)
                CreateDate = datetime.datetime.strftime(CreateDate, DATE_FORMAT)#日期转化为字符串
                if x.working_team_id:
                    records = self.env['nantian_erp.working_team'].search([("id","=",x.working_team_id.id)])
                    if records:
                        record = records[0]
                        for y in record.employee_ids:
                            if y:
                                month_ids = self.env['nantian_erp.employee_month_cost'].search([("employee_id","=", y.id),("create_date", ">=",CreateDate)])
                                # 该员工月工资表里，工作组为本工作组时，大于创建日期的第一个就是该月的成本month_ids[0]
                                if month_ids:
                                    employees_cost = employees_cost + month_ids[0].month_cost_other
                                else:
                                    print "这个月该员工这个项目没有参加"
            x.month_cost = employees_cost + x.variable_expenses


class project_cost(models.Model):
    _name = 'nantian_erp.project_cost'

    working_team_id= fields.Many2one('nantian_erp.working_team',string="工作组(项目)名称")
    workteam_name = fields.Char(string="工作组",compute='split_workteam_name',store = True)
    partner_id = fields.Many2one("res.partner",compute = "fetch_partner",string="行业(客户)",store=True)
    user_id = fields.Many2one(related='working_team_id.user_id',string="工作组负责人")
    customer_manager = fields.Many2one('res.users',ompute ="fetch_partner", string="行业负责人",store=True)
    all_employees_cost = fields.Float(string="人员总费用(年度)")
    project_variable_expenses = fields.Float(string="该项目变动费用(年度)")
    project_total = fields.Float(compute="fetch_partner",string="项目成本(年度)",store=True)

    @api.depends("working_team_id","all_employees_cost")
    @api.multi
    def split_workteam_name(self):
        for x in self:
            x.workteam_name = x.working_team_id.name
            # 根据邮箱找到这个人的绩效

    #1.自动化更新所有工作组名称
    #2.计算字段找到他的客户,创建项目年表
    @api.depends("working_team_id","all_employees_cost","project_variable_expenses")
    @api.multi
    def fetch_partner(self):
        now = fields.datetime.now()
        YEAR_FORMAT = "%Y-01-01"
        CreateDate = fields.Datetime.from_string(now)
        CreateDate = datetime.datetime.strftime(CreateDate,YEAR_FORMAT)  # 日期转化为字符串
        records = self.env['nantian_erp.working_team'].search([])
        for record in records:
            objects = self.env['nantian_erp.project_cost'].search([("working_team_id", "=", record.id),("create_date", ">=",CreateDate)])
            if objects:
                object = objects[0]
                object.partner_id = record.partner_id.id
                object.customer_manager = record.partner_id.customer_manager.id
                object.project_total = object.all_employees_cost + object.project_variable_expenses
            else:
                project_cost_id = self.env['nantian_erp.project_cost'].create(
                        {"working_team_id": record.id})

    # 创建月项目表
    @api.multi
    def create_project_cost_month(self):
        MONTH_FORMAT = "%Y-%m-01"
        YEAR_FORMAT = "%Y-01-01"
        now = fields.datetime.now()
        CreateMDate = datetime.datetime.strftime(now, MONTH_FORMAT)  #
        CreateYDate = datetime.datetime.strftime(now, YEAR_FORMAT)  #
        records = self.env['nantian_erp.working_team'].search([])
        for record in records:
            objects = self.env['nantian_erp.project_cost'].search(
                [("working_team_id", "=", record.id), ("create_date", ">=", CreateYDate)])
            if objects:
                 object = objects[0]
                 recs = self.env['nantian_erp.project_cost_month'].search(
                    [("working_team_id", "=", record.id),("project_cost_year_id", "=", object.id), ("create_date", ">=", CreateMDate)])
                 if recs:
                     print '月项目表已存在'
                 else:
                     id = self.env['nantian_erp.project_cost_month'].create(
                            {"working_team_id": record.id,"project_cost_year_id": object.id})
            else:
                print '还没有建项目年表'


    @api.multi
    @api.depends('partner_id')
    def compute_project_cost(self):
        MONTH_FORMAT = "%Y-%m-01"
        YEAR_FORMAT = "%Y-01-01"
        now = fields.datetime.now()
        CreateMDate = datetime.datetime.strftime(now, MONTH_FORMAT)  #
        CreateYDate = datetime.datetime.strftime(now, YEAR_FORMAT)  #
        records = self.env['nantian_erp.project_cost'].search(
            [("create_date", ">=", CreateYDate)])# 今年的
        for record in records:
            ids = self.env['nantian_erp.project_cost_month'].search(
                    [("project_cost_year_id", "=", record.id)])
            for id in ids:
                if id.month_cost:
                    record.project_total=+id.month_cost


# 员工每月工资表
class employee_month_cost(models.Model):
    _name = 'nantian_erp.employee_month_cost'


    email = fields.Char(related='employee_id.user_id.email',string="员工邮箱")
    wages = fields.Float(string="税前工资")
    grants_year = fields.Float(string="补助")#这个补助
    variable_expenses = fields.Float(string="变动费用")# 这个标动费用是报销只适合计算个人的，分成很多客户的，所
    base_protect = fields.Float(string="社保基数")
    pay_of_company = fields.Float(string="社保+公积金(公司缴纳部分)", compute='compute_month_cost', store=True)
    union_funds_month = fields.Float(string="工会经费(月度)",compute='compute_month_cost',store=True)
    employee_id = fields.Many2one(related='performance_year_id.employee_id', string="员工姓名")
    department_id = fields.Many2one(related='performance_year_id.department_id', string="部门", store=True)
    department_first = fields.Char(related='performance_year_id.department_first',string="一级部门",store=True)
    department_second = fields.Char(related='performance_year_id.department_second',string="二级部门",store=True)
    date = fields.Date(string='工资月份')
    month_cost = fields.Float(string="人力成本合计(月度)",compute = 'compute_month_cost',store = True)
    month_cost_other = fields.Float(string="人力成本合计(月度,不计变动费用)",compute ='compute_month_cost',store = True)
    performance_year_id = fields.Many2one('nantian_erp.performance_year',string="员工年成本")
    working_team_id = fields.Many2one(related='employee_id.working_team_id',string="所在项目组",store = True)
    # 这样的他的人员表里面relate值改变

    performance_month_id = fields.Many2one('nantian_erp.performance_month',string="员工月度绩效")
    performance_month = fields.Float(related='performance_month_id.month_performance',string="绩效")
    cost_day = fields.Float(string="人力成本(每天)",compute='compute_month_cost',store=True)


    #这个部分可以做成每月copy一份工资表然后倒入新的工资表改变话的

    # 根据邮箱找到员工录入这些基本费用
    @api.multi
    @api.depends('email')
    def search_employee(self):
        pass

    @api.multi
    @api.depends('wages','base_protect','pay_of_company','performance_month',\
                 'union_funds_month', 'grants_year','variable_expenses','month_cost','month_cost_other')
    def compute_month_cost(self):
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

            record.month_cost = record.wages + record.pay_of_company + record.performance_month\
            + record.union_funds_month + record.grants_year+ record.variable_expenses# 加上了这个人这个月的变动费用

            record.month_cost_other = record.wages + record.pay_of_company + record.performance_month\
            + record.union_funds_month+ record.grants_year
            record.cost_day = record.month_cost/21.5#（不计变动费用）
            # 暂时不管计算



#年人力成本核算
class performance_year(models.Model):
    _name = 'nantian_erp.performance_year'

    employee_id = fields.Many2one('hr.employee',string="员工姓名")
    working_team_id = fields.Many2one(related='employee_id.working_team_id',string="所在项目组")
    performance_year = fields.Float(string="年终奖")
    total_year = fields.Float(string="成本总计",compute = 'compute_year_cost',store = True)
    total_year_other = fields.Float(string="成本总计(项目)",compute = 'compute_year_cost',store = True)
    department_id = fields.Many2one(related='employee_id.department_id', string="部门", store=True)
    department_first = fields.Char(string="一级部门", compute='get_department_level', store=True)
    department_second = fields.Char(string="二级部门", compute='get_department_level', store=True)

    employee_month_cost_ids = fields.One2many('nantian_erp.employee_month_cost','performance_year_id',string="员工月度成本")
    total_month_cost = fields.Float(string="人力成本合计(年度)",compute='compute_year_cost',store = True)
    total_month_cost_other = fields.Float(string="人力成本合计(年度,不计变动费用)",compute='compute_year_cost',store = True)
    performance_month_ids = fields.One2many('nantian_erp.performance_month','performance_year_id',string="员工月度绩效")

    @api.multi
    @api.depends('department_id',"employee_month_cost_ids")
    def get_department_level(self):
        records = self.env['nantian_erp.performance_year'].search([])
        for record in records:
            if record.department_id.level == 1:
                pass
            elif record.department_id.level == 2:
                record.department_first = record.department_id.name
            elif record.department_id.level == 3:
                record.department_first = record.department_id.parent_id.name
                record.department_second = record.department_id.name
            else:
                pass

    @api.multi
    @api.depends("employee_id","working_team_id","performance_year","total_month_cost","total_month_cost_other")
    def compute_year_cost(self):
        MONTH_FORMAT = "%Y-%m-01"
        YEAR_FORMAT = "%Y-01-01"
        now = fields.datetime.now()
        CreateMDate = datetime.datetime.strftime(now, MONTH_FORMAT)  #
        CreateYDate = datetime.datetime.strftime(now, YEAR_FORMAT)  #
        records = self.env['nantian_erp.performance_year'].search([("create_date",">=",CreateYDate)])
        for record in records:
            for x in record.employee_month_cost_ids:
                worktime_id = self.env['nantian_erp.worktime_in_project'].search(
                    [("employee_id", "=",x.employee_id.id)])
                # worktime_id = self.env['nantian_erp.worktime_in_project'].search(
                #     [("employee_id", "=", x.employee_id.id), ('working_team_id', '=', x.working_team_id.id)])
                # if x.month_cost:
                #     record.total_month_cost = record.total_month_cost + x.month_cost
                pass
        record.total_year = record.total_month_cost + record.performance_year



    # 每年自动创建年绩效表
    @api.multi
    def create_year_performance(self):
        now = fields.datetime.now()
        OneyearAgo = (now - datetime.timedelta(days=365))
        records = self.env['hr.employee'].search([])
        for record in records:
            objects = self.env['nantian_erp.performance_year'].search([("employee_id", "=", record.id)])
            if objects:
                for x in objects:
                    CreateDate = fields.Date.from_string(x.create_date)
                    if CreateDate.year == now.year:
                        print record.name + '不必创建年表'
                        break
                else:
                    print record.name + '创建年表'
                    object = self.env['nantian_erp.performance_year'].create(
                    {"employee_id": record.id})
            else:
                object = self.env['nantian_erp.performance_year'].create(
                {"employee_id": record.id})
                print record.name + '没有年表'

    # 每个月自动创建月绩效表和工资表
    @api.multi
    def create_month_performance(self):
        # date = fields.Date.to_string(now)
        records = self.env['hr.employee'].search([])
        # print type(time.strftime("%Y-01-01"))
        for record in records:
            objects = self.env['nantian_erp.performance_year'].search([("employee_id", "=", record.id),('create_date', '>=',time.strftime("%Y-01-01"))])
            if objects:
                object = objects[0]
                print object.create_date
                print "对比时间"
                print (time.strftime("%Y-%m-%d"))
                if object:
                    month_id = self.env['nantian_erp.employee_month_cost'].search([("employee_id", "=", record.id),('create_date', '>=',time.strftime("%Y-%m-01"))])
                    if month_id:
                        print record.name + '月工资表和绩效表已存在'
                    else:
                        print record.name + '创建月工资表和绩效表'
                        month_cost = self.env['nantian_erp.performance_month'].create(
                        {"performance_year_id": object.id}
                    )
                        month_cost_id = self.env['nantian_erp.employee_month_cost'].create(
                        {"performance_year_id": object.id,"performance_month_id": month_cost.id})
                else:
                    #上个自动化动作已经检测他的年边是否在
                    pass
            else:
                #上个自动化动作已经检测他的年边是否存在
                pass

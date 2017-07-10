# -*- coding: utf-8 -*-
from openerp import models, fields, api,exceptions
import datetime
import time
import datetime as datetime_boss

"""
人力月成本表和年成本表有SN财务序号，项目的没有
"""

# 数据导入必须提供员工邮箱和工作组名称和日期
class variable_expenses(models.Model):
    _name = 'nantian_erp.variable_expenses'


    email = fields.Char(string="员工邮箱")# 导一个即可
    employee_id = fields.Many2one('hr.employee',compute = 'match_workingteam_and_employee',store = True)
    workteam_name = fields.Char(string="工作组名称")
    work_team_id = fields.Many2one('nantian_erp.working_team',compute = 'match_workingteam_and_employee',store = True)
    cost = fields.Float(string="变动费用")
    date = fields.Date(string="费用日期")
    project_cost_month_id = fields.Many2one('nantian_erp.project_cost_month',compute = 'match_workingteam_and_employee',store = True)
    employee_month_cost_id = fields.Many2one('nantian_erp.employee_month_cost',compute = 'match_workingteam_and_employee',store = True)
    error = fields.Char(string="数据导入时的状态")

    # 变动费用单创建时就计算出他系统里所有的关联信息
    def create(self, cr, uid, vals, context = None):
        print "开始执行创建函数"
        print "nantian_erp.variable_expenses---vals"
        # context --> {u'lang': u'zh_CN', u'params': {u'action': 1244}, u'tz': u'Asia/Shanghai', u'uid': 1}
        # context = None --> {u'lang': u'zh_CN', u'params': {u'menu_id': 921, u'view_type': u'list', u'limit': 80, u'action': 1244, u'_push_me': False, u'model': u'nantian_erp.variable_expenses', u'page': 0}, u'tz': u'Asia/Shanghai', u'uid': 1}
        return super(variable_expenses, self).create(cr, uid, vals, context=context)

    # 触动找到人员找到工作组
    @api.multi
    @api.depends('email','workteam_name','date','work_team_id','employee_id',"employee_month_cost_id")
    def match_workingteam_and_employee(self):
        DATE_FORMAT = "%Y-%m-01"
        print "开始执行自动计算函数"
        for x in self:
            employee_id = self.env['hr.employee'].search([("user_id.email", "=", x.email)])
            work_team_id = self.env['nantian_erp.working_team'].search([("name", "=", x.workteam_name)])
            if x.date:
                print x.date
                CreateDate = fields.Datetime.from_string(x.date)
                Date = datetime.datetime.strftime(CreateDate, DATE_FORMAT)  # 日期转化为字符串
                if employee_id:
                    x.employee_id = employee_id[0].id
                else:
                    x.error = "人力资源关联失败，建议检查导入的邮箱；"
                if work_team_id:
                    x.work_team_id = work_team_id[0].id
                else:
                    x.error = x.error + "工作组关联失败，建议检查导入的工作组名称；"
                if x.employee_id:
                    employee_month_cost_ids = self.env['nantian_erp.employee_month_cost'].search(
                        [("employee_id", "=", x.employee_id.id), ("create_date", ">=", Date)])
                    if employee_month_cost_ids:
                        x.employee_month_cost_id = employee_month_cost_ids[0].id
                    else:
                        x.error = "waring:员工该月工资表关联失败，建议检查日期和该月工资表情况；"
                if x.work_team_id:
                    project_cost_month_ids = self.env['nantian_erp.project_cost_month'].search(
                        [("working_team_id", "=", x.work_team_id.id), ("create_date", ">=", Date)])
                    if project_cost_month_ids:
                        x.project_cost_month_id = project_cost_month_ids[0].id
                    else:
                        x.error = "waring:工作组该月项目成本表关联失败，建议检查日期和该项目组该月成本表情况；"




class performance_note(models.Model):
    _name = 'nantian_erp.performance_note'
    _rec_name = 'title'

    title = fields.Char(string="选项名")
    performance_month_id = fields.Many2one('nantian_erp.performance_month',string="绩效单",readonly = True)
    text = fields.Char(string="备注")

# 月度绩效有财务税号，
class performance_month(models.Model):
    _name = 'nantian_erp.performance_month'

    employee_id = fields.Many2one("hr.employee", string="员工表",store=True)
    date = fields.Date(string="绩效月份")
    SN = fields.Char(string="财务序号")
    email = fields.Char(string="员工邮箱")
    name = fields.Char(string="姓名")
    gender = fields.Char(string="性别")
    department_id = fields.Many2one("hr.department", string="部门", store=True)
    department_first = fields.Char(string="一级部门",compute='get_department_level',store=True)
    department_second = fields.Char(string="二级部门",compute='get_department_level', store=True)
    department_third = fields.Many2one("nantian_erp.working_team",string="三级工作组",store = True)
    department_third_name = fields.Char(string="工作组")
    partner_id = fields.Many2one("res.partner",string="行业(客户)",store=True)
    month_percent = fields.Float(string="本月绩效百分比" ,default = 1)
    month_performance = fields.Float(string="本月绩效")
    note = fields.Char(string="备注")
    error = fields.Char(string="数据导入时的状态")
    performance_year_id = fields.Many2one('nantian_erp.performance_year',string="员工年绩效")

    @api.depends('department_id')
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

    def create(self, cr, uid, vals, context=None):
        today = fields.datetime.today()
        YEAR_FORMAT = "%Y-%m-03"
        CreateYDate = datetime.datetime.strftime(today, YEAR_FORMAT)  # 日期转化为字符串
        CreateDate = fields.Datetime.from_string(CreateYDate)  # 字符串转化为日期
        print "nantian_erp.performance_month"
        print vals
        if vals['employee_id']:
            hr_models = self.pool.get('hr.employee')
            hr_models_ids = hr_models.search(cr, uid, [('id', '=', vals['employee_id'])], limit=1, context=None)
            if hr_models_ids:
                hr_object = hr_models.browse(cr, uid, hr_models_ids, context=None)
                print hr_object.name
                vals['department_third'] = hr_object.working_team_id.id
                vals['department_third_name'] = hr_object.working_team_id.name
                vals['department_id'] = hr_object.department_id.id
                vals['SN'] = hr_object.SN
                vals['date'] = CreateDate
                vals['email'] = hr_object.user_id.email
                vals['gender'] = hr_object.gender
                vals['name'] = hr_object.name
            else:
                vals['error'] = "人力资源关联失败，建议检查员工信息；"
            return super(performance_month, self).create(cr, uid, vals, context=context)
        else:
            raise exceptions.ValidationError('您没有填写员工姓名！')
            return None

class worktime_in_project(models.Model):
    _name = 'nantian_erp.worktime_in_project'

    # 结合人员调动表，人员离职表，去确定人员在项目中的时长
    working_team_id = fields.Many2one('nantian_erp.working_team',string="工作组(项目)名称")
    partner_id = fields.Many2one("res.partner",string="行业(客户)")
    employee_ids = fields.Many2many('hr.employee',string="员工姓名")
    date = fields.Date(string='录入日期')

    # 安排的工作---每个月初记录该工作组有多少人2017.07.01
    # 应该把之前几个月的都补上
    @api.multi
    def record_workteam_employees(self):
        today = fields.datetime.today()
        YEAR_FORMAT = "%Y-%m-01"
        CreateYDate = datetime.datetime.strftime(today, YEAR_FORMAT)  # 日期转化为字符串
        work_teams = self.env['nantian_erp.working_team'].search([])
        for work_team in work_teams:
            records = self.env['nantian_erp.worktime_in_project'].search([("working_team_id", "=", work_team.id),("date",">", today)])
            if records:
                pass
            else:
                if work_team.employee_ids:
                    id = self.env['nantian_erp.worktime_in_project'].create(
                    {"working_team_id": work_team.id,"date": today,"employee_ids":[[6, 0, work_team.employee_ids.ids]]})
                else:
                    pass

    def create(self, cr, uid, vals, context=None):
        print "vals????????"
        print vals
        return super(worktime_in_project, self).create(cr, uid, vals, context=context)


# 项目月成本表
class project_cost_month(models.Model):
    _name = 'nantian_erp.project_cost_month'

    date = fields.Date(string="项目月份")
    working_team_id = fields.Many2one('nantian_erp.working_team',string="工作组(项目)名称")
    workteam_name = fields.Char(string="工作组",store = True)
    partner_id = fields.Many2one("res.partner",string="行业(客户)",store=True)
    user_id = fields.Many2one("res.users",string="工作组负责人")
    customer_manager = fields.Many2one("res.users",string="行业负责人",store=True)
    month_cost = fields.Float(compute='compute_project_cost_month',string = '工作组月总计',store = True)
    variable_expenses_ids = fields.One2many('nantian_erp.variable_expenses','project_cost_month_id',string="人员月变动费用")
    variable_expenses = fields.Float(compute='compute_project_cost_month',string="工作组变动费用(月计)",store = True)
    project_cost_year_id = fields.Many2one('nantian_erp.project_cost',string="工作组年表")
    employee_ids = fields.Many2many('hr.employee',"project_cost_month_employee_ref",store=True)
    error = fields.Char(string="数据导入时的状态")

    # 自动创建的，但是也可以手动创建
    def create(self, cr, uid, vals, context=None):
        today = fields.datetime.today()
        YEAR_FORMAT = "%Y-%m-02"
        CreateYDate = datetime.datetime.strftime(today, YEAR_FORMAT)  # 日期转化为字符串
        CreateDate = fields.Datetime.from_string(CreateYDate)  # 字符串转化为日期
        print "nantian_erp.project_cost_month------>vals"
        if vals['working_team_id']:
            work_team_models = self.pool.get('nantian_erp.working_team')
            work_team_ids = work_team_models.search(cr, uid, [('id', '=', vals['working_team_id'])], limit=1,
                                                    context=None)
            if work_team_ids:
                work_team_object = work_team_models.browse(cr, uid, work_team_ids, context=None)
                print work_team_object.name
                vals['user_id'] = work_team_object.user_id.id
                vals['partner_id'] = work_team_object.partner_id.id
                vals['customer_manager'] = work_team_object.partner_id.customer_manager.id
                vals['workteam_name'] = work_team_object.name
                vals['date'] = CreateDate
            else:
                vals['error'] = "工作组关联失败，建议检查导入的工作组名称；"
            return super(project_cost_month, self).create(cr, uid, vals, context=context)
        else:
            raise exceptions.ValidationError('您没有填写工作组！')
            return None


    #安排的动作每个月初计算上个月工作组成本2017.07.02
    #还得包括之前每一个月的支出：分开计算
    @api.multi
    def compute_workteam_cost_month(self):
        # 上个月的日期
        LastMonth = fields.datetime.now()-datetime_boss.timedelta(days=30)
        YEAR_FORMAT = "%Y-%m-01"
        LastMonthDate = datetime.datetime.strftime(LastMonth, YEAR_FORMAT)  # 日期转化为字符串
        print LastMonthDate
        # 本月的日期
        CurrentMonth = fields.datetime.now()
        CurrentMonthDate = datetime.datetime.strftime(CurrentMonth, YEAR_FORMAT)  # 日期转化为字符串
        print CurrentMonthDate
        work_teams = self.env['nantian_erp.working_team'].search([])[0:2]
        for work_team in work_teams:
            list1 = []
            list2 = []
            print "查找之前"
            print work_team.name
            print list1
            print list2
            records = self.env['nantian_erp.project_cost_month'].search([("working_team_id", "=",work_team.id),("date", ">",LastMonthDate),("date", "<",CurrentMonthDate)])
            if records:
                # 流入 inflow 流出 outflow 不变 stay
                record = records[0]
                records_last = self.env['nantian_erp.worktime_in_project'].search(
                    [("working_team_id", "=", work_team.id), ("date", ">=", LastMonthDate)])
                if records_last:
                    list1 = records_last[0].employee_ids
                    print list1
                records_current = self.env['nantian_erp.worktime_in_project'].search(
                    [("working_team_id", "=", work_team.id), ("date", ">=", CurrentMonthDate)])
                if records_current:
                    list2 = records_current[0].employee_ids
                    print list2
                # 上个月人员流出
                outflow = set(list1)-set(list2)
                print outflow
                # 上个月人员流入
                inflow = set(list2)-set(list1)
                print inflow
                # 上个月人员不变
                stay = set(list1)&set(list2)
                print stay
            else:
                #print 还没有创建本月的项目成本表
                pass



    #每个月项目要花多少钱，这个位置还没有把工作项目时长加进去
    @api.multi
    @api.depends("working_team_id",'variable_expenses_ids')
    def compute_project_cost_month(self):
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
                        """
                        这个人员是不准确的是没有变动的，解决方案每个月末，记载一下公作组里的人的ID
                        如果这个人和上个月里的人比不变的就加满整月的工资，如果是变化的就查找走的人和来的人的具体时间
                        新进入的看何时进入，离开的看何时离开"""
            x.month_cost = employees_cost + x.variable_expenses

# 项目年成本表
class project_cost(models.Model):
    _name = 'nantian_erp.project_cost'

    date = fields.Date(string="项目年份")
    working_team_id= fields.Many2one('nantian_erp.working_team',string="工作组(项目)名称")
    workteam_name = fields.Char(string="工作组",store = True)
    user_id = fields.Many2one("res.users",string="工作组负责人")
    partner_id = fields.Many2one("res.partner", string="行业(客户)", store=True)
    customer_manager = fields.Many2one('res.users',string="行业负责人",store=True)
    project_total = fields.Float(compute="compute_project_cost",string="项目成本总计(年度)",store=True)
    project_variable_expenses = fields.Float(compute="compute_project_cost",string="该工作组变动费用(年度)",store=True)
    project_cost_month_ids = fields.One2many('nantian_erp.project_cost_month','project_cost_year_id',string="人员月变动费用")
    error = fields.Char(string="数据导入时的状态")

    def create(self, cr, uid, vals, context=None):
        today = fields.datetime.today()
        YEAR_FORMAT = "%Y-%m-02"
        CreateYDate = datetime.datetime.strftime(today, YEAR_FORMAT)  # 日期转化为字符串
        CreateDate = fields.Datetime.from_string(CreateYDate)  # 字符串转化为日期
        print "nantian_erp.project_cost"
        if vals['working_team_id']:
            work_team_models = self.pool.get('nantian_erp.working_team')
            work_team_ids = work_team_models.search(cr, uid, [('id', '=',vals['working_team_id'])],limit = 1, context=None)
            if work_team_ids:
                work_team_object = work_team_models.browse(cr, uid, work_team_ids, context=None)
                print work_team_object.name
                vals['user_id'] = work_team_object.user_id.id
                vals['partner_id'] = work_team_object.partner_id.id
                vals['customer_manager'] = work_team_object.partner_id.customer_manager.id
                vals['workteam_name'] = work_team_object.name
                vals['date'] = CreateDate
            else:
                vals['error'] = "工作组关联失败，建议检查导入的工作组名称；"
            return super(project_cost, self).create(cr, uid, vals, context=context)
        else:
            raise exceptions.ValidationError('您没有填写工作组！')
            return None

    #安排动作 创建项目年表
    @api.multi
    def create_project_year(self):
        now = fields.datetime.now()
        YEAR_FORMAT = "%Y-01-01"
        CreateYDate = datetime.datetime.strftime(now,YEAR_FORMAT)  # 日期转化为字符串
        records = self.env['nantian_erp.working_team'].search([])
        for record in records:
            objects = self.env['nantian_erp.project_cost'].search([("working_team_id", "=", record.id),("create_date", ">=",CreateYDate)])
            # 如果在把年信息更新成现在最新的，如果不在就创建一个今年的
            if objects:
                pass
            else:
               self.env['nantian_erp.project_cost'].create({"working_team_id": record.id})

    # 安排的动作 创建月项目表
    @api.multi
    def create_project_cost_month(self):
        MONTH_FORMAT = "%Y-%m-01"
        YEAR_FORMAT = "%Y-01-01"
        now = fields.datetime.now()
        CreateMDate = datetime.datetime.strftime(now, MONTH_FORMAT)  #
        CreateYDate = datetime.datetime.strftime(now, YEAR_FORMAT)  #
        records = self.env['nantian_erp.working_team'].search([])
        for record in records:
            project_cost_id = self.env['nantian_erp.project_cost'].search(
                [("working_team_id", "=", record.id), ("create_date", ">=", CreateYDate)],limit = 1)
            if project_cost_id:
                 recs = self.env['nantian_erp.project_cost_month'].search(
                    [("working_team_id", "=", record.id),("create_date", ">=", CreateMDate)])
                 if recs:
                     print '月项目表已存在'
                 else:
                     id = self.env['nantian_erp.project_cost_month'].create(
                            {"working_team_id": record.id,"project_cost_year_id":project_cost_id})
            else:
                print '还没有建项目年表'

    # 每个月计算一下项目年成本()
    @api.multi
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
                    [("working_team_id","=",record.working_team_id.id),("create_date",">=",CreateYDate)])
            for id in ids:
                if id.month_cost:
                    record.project_total = record.project_total + id.month_cost
                if id.variable_expenses:
                    record.project_variable_expenses = record.project_variable_expenses + variable_expenses


# 人力月成本表
class employee_month_cost(models.Model):
    _name = 'nantian_erp.employee_month_cost'

    SN = fields.Char(string="财务序号")# 导一个即可
    date = fields.Date(string="工资月份")
    email = fields.Char(string="员工邮箱")
    employee_id = fields.Many2one('hr.employee',string="员工姓名")
    working_team_id = fields.Many2one("nantian_erp.working_team",string="所在项目组",store = True)
    department_id = fields.Many2one("hr.department", string="部门", store=True)
    department_first = fields.Char(string="一级部门",compute='get_department_level', store=True)
    department_second = fields.Char(string="二级部门",compute='get_department_level', store=True)
    wages = fields.Float(string="税前工资")
    grants_year = fields.Float(string="补助")
    variable_expenses = fields.Float(string="变动费用")# 这个标动费用是报销只适合计算个人的，分成很多客户的，所
    variable_expenses_ids = fields.One2many("nantian_erp.variable_expenses","employee_month_cost_id",store=True)
    base_protect = fields.Float(string="社保基数")
    pay_of_company = fields.Float(string="社保+公积金(公司缴纳部分)", compute='compute_month_cost', store=True)
    union_funds_month = fields.Float(string="工会经费(月度)",compute='compute_month_cost',store=True)
    month_cost = fields.Float(string="人力成本合计(月度)",compute = 'compute_month_cost',store = True)
    month_cost_other = fields.Float(string="人力成本合计(月度,不计变动费用)",compute ='compute_month_cost',store = True)
    performance_year_id = fields.Many2one('nantian_erp.performance_year',string="员工年成本表")
    performance_month_id = fields.Many2one('nantian_erp.performance_month',string="员工月度绩效")
    performance_month = fields.Float(related='performance_month_id.month_performance',string="绩效")
    cost_day = fields.Float(string="人力成本(每天)",compute='compute_month_cost',store=True)
    error = fields.Char(string="数据导入时的状态")


    #这个部分可以做成每月copy一份工资表然后倒入新的工资表改变话的
    @api.depends('department_id')
    def get_department_level(self):
        print "开始执行计算函数"
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


    @api.multi
    @api.depends('wages','base_protect','pay_of_company','performance_month',"variable_expenses_ids",\
                 'union_funds_month', 'grants_year','variable_expenses','month_cost','month_cost_other')
    def compute_month_cost(self):
        for record in self:
            if record.variable_expenses_ids:
                for var in record.variable_expenses_ids:
                    record.variable_expenses = record.variable_expenses + var.cost
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
            record.cost_day = record.month_cost/30#（不计变动费用）
            # 暂时不管计算

    def create(self, cr, uid, vals, context=None):
        print "nantian_erp.employee_month_cost"
        print vals
        print "开始执行创建函数"
        if vals['employee_id']:
            hr_models = self.pool.get('hr.employee')
            hr_models_ids = hr_models.search(cr, uid, [('id', '=', vals['employee_id'])], limit=1, context=None)
            if hr_models_ids:
                hr_object = hr_models.browse(cr, uid, hr_models_ids, context=None)
                print hr_object.name
                vals['working_team_id'] = hr_object.working_team_id.id
                vals['department_id'] = hr_object.department_id.id
                vals['email'] = hr_object.user_id.email
                vals['SN'] = hr_object.SN
                vals['workteam_name'] = hr_object.working_team_id.name
                # 手动填写的自己去找哪个项目组哪个月份下的哪个项目
                # month_cost_id = self.env['nantian_erp.employee_month_cost'].create(
                #     {"employee_id": record.id,
                #      "performance_year_id": object.id, "performance_month_id": month_cost.id,})
            else:
                vals['error'] = "人力资源关联失败，建议检查员工信息；"
            return super(employee_month_cost, self).create(cr, uid, vals, context=context)
        else:
            raise exceptions.ValidationError('您没有填写员工姓名！')
            return None



#年人力成本核算#名字一定要改成employee_year_cost
class performance_year(models.Model):
    _name = 'nantian_erp.performance_year'

    SN = fields.Char(string="财务序号")# 导一个即可
    date = fields.Date(string="工资年份")
    employee_id = fields.Many2one('hr.employee',string="员工姓名")
    working_team_id = fields.Many2one('nantian_erp.working_team',string="所在项目组",store = True)
    department_id = fields.Many2one("hr.department",string="部门", store=True)
    department_first = fields.Char(string="一级部门", compute='get_department_level', store=True)
    department_second = fields.Char(string="二级部门", compute='get_department_level', store=True)
    performance_year = fields.Float(string="年终奖")
    # 以下这两个字段便于显示
    employee_month_cost_ids = fields.One2many('nantian_erp.employee_month_cost','performance_year_id',string="员工月度成本")
    performance_month_ids = fields.One2many('nantian_erp.performance_month','performance_year_id',string="员工月度绩效")
    total_month_cost = fields.Float(string="员工月成本合计(12月)",compute='compute_year_cost',store = True)
    total_year = fields.Float(string="成本总计",compute = 'compute_year_cost',store = True)
    error = fields.Char(string="数据导入时的状态")
    # {u'employee_id': False, u'performance_month_ids': [], u'working_team_id': False,
    #  u'employee_month_cost_ids': [[6, False, []]], u'performance_year': 0, u'department_id': False}

    @api.multi
    @api.depends("employee_month_cost_ids","performance_year","total_month_cost")
    def compute_year_cost(self):
        for record in self:
            if record.employee_month_cost_ids:
                for x in record.employee_month_cost_ids:
                    print x.email
                    record.total_month_cost = record.total_month_cost + x.month_cost
            record.total_year = record.total_month_cost + record.performance_year

    # 每年自动创建年表
    @api.multi
    def create_year_performance(self):
        MONTH_FORMAT = "%Y-%m-01"
        YEAR_FORMAT = "%Y-01-01"
        now = fields.datetime.now()
        OneyearAgo = (now - datetime.timedelta(days=365))
        CreateMDate = datetime.datetime.strftime(now, MONTH_FORMAT)  #
        CreateYDate = datetime.datetime.strftime(now, YEAR_FORMAT)  #
        records_all = self.env['hr.employee'].search([])
        records = self.env['hr.employee'].search(['|',('department_id.name','=',u'数据中心服务部'),('department_id.parent_id.name','=',u'数据中心服务部')])
        for record in records:
            objects = self.env['nantian_erp.performance_year'].search([("employee_id", "=", record.id),("create_date", ">=",CreateYDate)])
            if objects:
                object = objects[-1]
                pass
            else:
                  object = self.env['nantian_erp.performance_year'].create({"employee_id": record.id,})

    # 安排的动作 每个月自动创建月绩效表和月员工成本表
    @api.multi
    def create_month_performance_and_salary(self):
        records_all = self.env['hr.employee'].search([])
        records = self.env['hr.employee'].search(['|',('department_id.name','=',u'数据中心服务部'),('department_id.parent_id.name','=',u'数据中心服务部')])
        for record in records:
            objects = self.env['nantian_erp.performance_year'].search([("employee_id","=",record.id),('create_date', '>=',time.strftime("%Y-01-01"))])
            if objects:
                object = objects[-1]
                if object:
                    month_id = self.env['nantian_erp.employee_month_cost'].search([("employee_id", "=", record.id),('create_date', '>=',time.strftime("%Y-%m-01"))])
                    if month_id:
                        print record.name + '月工资表和绩效表已存在'
                    else:
                        month_cost = self.env['nantian_erp.performance_month'].create(
                        {"employee_id": record.id,"performance_year_id": object.id,}
                        )
                        # 手动填写的自己去找哪个项目组哪个月份下的哪个项目，自动创建就自动赋值
                        month_cost_id = self.env['nantian_erp.employee_month_cost'].create(
                            {"employee_id": record.id,
                             "performance_year_id": object.id, "performance_month_id": month_cost.id,}
                        )
            else:
                #上个自动化动作已经检测他的年边是否存在
                pass

    @api.depends('department_id')
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

    def create(self, cr, uid, vals, context=None):
        today = fields.datetime.today()
        YEAR_FORMAT = "%Y-%m-02"
        CreateYDate = datetime.datetime.strftime(today, YEAR_FORMAT)# 日期转化为字符串
        CreateDate = fields.Datetime.from_string(CreateYDate)  # 字符串转化为日期
        print type(CreateYDate)
        print type(CreateDate)
        print "nantian_erp.performance_year"
        print vals
        if vals['employee_id']:
            hr_models = self.pool.get('hr.employee')
            hr_models_ids = hr_models.search(cr, uid, [('id', '=', vals['employee_id'])],limit=1, context=None)
            if hr_models_ids:
                hr_object = hr_models.browse(cr, uid, hr_models_ids, context=None)
                print hr_object.name
                vals['working_team_id'] = hr_object.working_team_id.id
                vals['department_id'] = hr_object.department_id.id
                vals['SN'] = hr_object.SN
                vals['date'] = CreateDate
            else:
                vals['error'] = "人力资源关联失败，建议检查员工信息；"
            return super(performance_year, self).create(cr, uid, vals, context=context)
        else:
            raise exceptions.ValidationError('您没有填写员工姓名！')
            return None

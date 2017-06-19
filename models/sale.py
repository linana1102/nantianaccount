# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class weekly_reports(models.Model):
    _name = 'nantian_erp.weekly_reports'

    user_id = fields.Many2one('res.users',string='创建者',required=True,default=lambda self: self.env.user)#
    date = fields.Date(string='创建日期',default=lambda self:fields.datetime.now(),readonly = True)
    pres_sale_ids = fields.One2many('nantian_erp.pres_sale','weekly_reports_id',string='售前项目进展')
    gathering_ids = fields.One2many('nantian_erp.project_gathering','weekly_reports_id',string='项目收款')
    # pers_transfer_ids = fields.Many2many('nantian_erp.pers_transfer','weekly_reports_idemp_weekly_transfer_ref',string='人员调动')
    pers_transfer_ids = fields.One2many('nantian_erp.pers_transfer','weekly_reports_id',string='人员调动')
    demission_ids = fields.One2many('nantian_erp.demission','weekly_reports_id',string='人员离职')
    customer_adjust_ids = fields.One2many('nantian_erp.customer_adjust','weekly_reports_id',string='客户动态或人事变动')
    project_progress_ids = fields.One2many('nantian_erp.project_progress','weekly_reports_id',string='项目进度')

    job = fields.Char(string='岗位')
    count = fields.Char(string='人数')
    reason = fields.Char(string='原因')

    # 自动化动作每周创建一个周报，内容是copy上一周周报的所有内容
    @api.multi
    def copy_weekly_reports(self):
        now = fields.datetime.now()
        SevenDayAgo = fields.Date.to_string((now - datetime.timedelta(days=8)))
        records = self.env['nantian_erp.weekly_reports'].search([('create_date','>=',SevenDayAgo)])
        # print '找到了所有人上次周报',records
        for record in records:
            #print '给他创建周报',record.user_id.id
            objects = self.env['nantian_erp.weekly_reports'].create(
                {"user_id": record.user_id.id})




    @api.multi
    def fetch_contract(self):
        now = fields.datetime.now()
        records = self.env['nantian_erp.weekly_reports'].search([])
        for record in records:
            print record.user_id.name
            objects = self.env['nantian_erp.contract'].search([("header_id", "=", record.user_id.id)])
            print objects
            if objects:
                for object in objects:
                    if object.collection_ids:
                        for collection in object.collection_ids:
                            if collection.materials_date:
                                SevenDayAgo = (now + datetime.timedelta(days=0))
                                ReminderDate = fields.Date.from_string(collection.materials_date)
                                print "七天后的时间", SevenDayAgo
                                print "准备材料的时间", ReminderDate
                                if SevenDayAgo.day == ReminderDate.day and SevenDayAgo.month == ReminderDate.month and SevenDayAgo.year == ReminderDate.year:
                                    # print "创建一个项目收款的表"
                                    objects = self.env['nantian_erp.project_gathering'].create(
                                        {"contract_id": collection.contract_id.id, "gather_reminder": collection.name,
                                         "weekly_reports_id": record.id})


class pres_sale(models.Model):
    _name = 'nantian_erp.pres_sale'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports',string='周报')
    project_name = fields.Char(string='项目名称')
    contract_name = fields.Char(string='合同名称')
    partner = fields.Char(string='客户名称')
    process_scrib = fields.Text(string='本周主要进展说明')
    before_bid_amount = fields.Float(string='投标金额(万)')
    bid_commpany = fields.Char(string='中标单位')
    pre_bid_date = fields.Date(string='预计投标日期')
    competitors = fields.Char(string='竞争对手')
    rate_of_success = fields.Char(string='预计成功率（%）')
    salesman_id = fields.Many2one('res.users', string='销售负责人')
    # 合同编号、项目名称、合同名称、客户名称、进展、
    # 标书编写、标书复核人、讲标人、投标金额、投标日期、中标单位、
    # 主要竞对、成功率、合同/中标金额、检索词、涉及厂商或平台、
    # 合同主要内容、销售人员、签字人、签订日
    # 项目名称、合同名称、进展、投标金额、投标日期、中标单位、主要竞对、成功率、
    contract_number = fields.Char(string='合同编号')
    bid_write = fields.Many2one('res.users',string='标书编写人')
    bid_checkman_id = fields.Many2one('res.users',string='标书复核人',)
    bid_readman_id = fields.Many2one('res.users',string='讲标人',)
    after_bid_amount = fields.Float(string='合同/中标金额(万)',)
    term = fields.Char(string='检索词',)
    firm_platform = fields.Char(string='涉及厂商或平台',)
    context = fields.Text(string='合同主要内容',)
    siger = fields.Many2one('res.users',string='签字人',)
    sign_date = fields.Date(string='签订日期',)
    state =fields.Selection(
        [
            (u'lose',u'未中标'),
            (u'win',u'项目开始'),
        ],default = u'lose',string=u"标书进展")
    state_w = fields.Selection(
        [
            (u'will_be', u'未投标'),
            (u'have_be', u'已投标'),
        ], default=u'will_be', string=u"标书状态")


    contract_view = {
        'name': ('创建合同'),
        'res_model': 'nantian_erp.contract',
        'views': [[False,'form']],
        'type': 'ir.actions.act_window',
        # 'target': 'new',
        'views_type': 'form',
        "domain": [[]],
        'view_mode': 'tree,form',
    }# 这个可以在确定合同内容后把东西填进去
    # return {
    #     'name': _('Distribution Model Saved'),
    #     'view_type': 'form',
    #     'view_mode': 'tree,form',
    #     'res_model': 'analytic.plan.create.model',
    #     'views': [(resource_id, 'form')],
    #     'type': 'ir.actions.act_window',
    #     'target': 'new',
    # }

    @api.multi
    def creat_new_contract(self):
        return self.contract_view

    @api.multi
    def win_the_biding(self):
        self.state = 'win'
        return {'bb'}

    @api.multi
    def lose_a_bid(self):
        self.state = 'lose'
        return {'aa'}

# 项目收款
class project_gathering(models.Model):#
    _name = 'nantian_erp.project_gathering'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')
    contract_id = fields.Many2one('nantian_erp.contract', string='合同')
    gather_date = fields.Date(string='！')
    gather_progress= fields.Selection([('开始准备材料',u"开始准备材料"),
                             ('完成准备材料',u"完成准备材料"),
                             ('已提交审核',u"已提交审核"),
                             ('审核通过准备付款',u"审核通过准备付款"),
                             ('完成付款',u"完成付款"),
                             ],
                            string='收款工作进度')
    # 准备收款材料时间前一周在周报该项中提醒需要开始准备收款，并给出此项工作进度选项：
    # 开始准备材料、完成准备材料、已提交审核、审核通过准备付款、完成付款。以此来反应收款工作进度。
    gather_count = fields.Float(string='预期收款金额')
    collection_ids = fields.One2many('nantian_erp.collection','project_gathering_id',string='合同收款表')
    gather_reminder = fields.Char(string='特此提醒，开始准备收款！')
    # 这个字段填写的是到哪一期第几阶段


# 人员的调动
class pers_transfer(models.Model):#
    _name = 'nantian_erp.pers_transfer'

    # weekly_reports_id = fields.Many2many('nantian_erp.weekly_reports','emp_weekly_transfer_ref', string='周报')
    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')
    employee_id = fields.Many2one('hr.employee',string='调动人',ondelete='set null')
    res_contract_name = fields.Many2one("nantian_erp.contract",compute = "store_transfer_message",store = True,string='合同名称')
    res_contract_job = fields.Many2one("nantian_erp.jobs",compute = "store_transfer_message",store = True,string='合同岗位')
    sour_team = fields.Many2one("nantian_erp.working_team",compute = "store_transfer_message",store = True,string='原项目组')
    move_reason = fields.Char(string='调动原因')
    move_date = fields.Date(string='调动时间')
    is_recruit = fields.Boolean(string='是否招聘')
    after_leader = fields.Many2one('hr.employee',string='调动后负责人',domain="['|',('job_id','=',u'部门经理'),('job_id','=',u'副总经理')]")
    before_leader = fields.Many2one('res.users',string='调动前负责人',default=lambda self: self.env.user,readonly = True)
    # default=lambda self: self.env.user.employee_ids[0] 用户可能不是员工就不能适合default
    des_team = fields.Char(string='新项目组')
    des_contract_name = fields.Char(string='合同名称')
    des_contract_job = fields.Char(string='合同岗位')
    touch = fields.Selection([(u'调整',u"调整"),
                              (u'修改', u"修改")
                              ],string = '调整状态',store = True)

    @api.multi
    @api.depends('employee_id')
    def store_transfer_message(self):
        for x in self:
            if x.employee_id:
                x.res_contract_name = x.employee_id.nantian_erp_contract_id
                x.res_contract_job = x.employee_id.contract_jobs_id
                x.sour_team = x.employee_id.working_team_id


    @api.multi
    def send_to_after_leader(self):
        if self.touch == u'未转交':
            print self.touch
            object = self.env['nantian_erp.weekly_reports'].search([("user_id", "=", self.after_leader.user_id.id)])
            if object:
                object = object[-1]
                print object.user_id.name
                # objects1 = self.env['nantian_erp.weekly_reports'].search([("user_id", "=", self.before_leader.id)])
                # print objects1
                if object:
                    objects2 = self.env['nantian_erp.pers_transfer'].create(
                        {"weekly_reports_id": object.id, "employee_id":self.employee_id.id,
                         "res_contract_name": self.res_contract_name.id,
                         "res_contract_job": self.res_contract_job.id,
                         "sour_team": self.sour_team.id,
                         "move_reason": self.move_reason,
                         "move_date": self.move_date,
                         "after_leader": self.after_leader.id,
                         "before_leader": self.before_leader.id,
                         })
                    self.touch = u'已转交'
                    print self.touch
                    # 找到该员工项目组的项目出入表，并且创建两条信息
                    sour_id_s = self.env['nantian_erp.worktime_in_project'].search(
                        [("employee_id", "=", self.employee_id.id,"working_team_id","=",self.sour_team.id)])
                    if sour_id_s:
                        sour_id = sour_id_s[-1]
                        sour_id.exit_date = self.move_date
                    else:
                        object = self.env['nantian_erp.worktime_in_project'].create(
                            {"employee_id": self.employee_id.id,"working_team_id":self.sour_team.id,"exit_date":self.move_date})
                    # 创建一条进入项目的时间
                    object = self.env['nantian_erp.worktime_in_project'].create(
                                        {"employee_id": self.employee_id.id,"enter_date": self.move_date })
                    print self.employee_id.name + '创建一个项目进入表'
            else:
                raise exceptions.ValidationError('您没有填写调动后的负责人')

    @api.multi
    def email_to_sys(self):
        pass


# 人员的离职
class demission(models.Model):#
    _name = 'nantian_erp.demission'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')# 项目组即工作组
    employee_id = fields.Many2one('hr.employee',string='离职申请人')# 这个人的调动人是他项目组的负责人
    contract_name = fields.Many2one("nantian_erp.contract",compute = "store_demission_message",store = True,string='合同名称' )
    contract_post = fields.Many2one("nantian_erp.jobs",compute = "store_demission_message",store = True,string='合同岗位')
    sro_project = fields.Many2one("nantian_erp.working_team",compute = "store_demission_message",store = True,string='项目组')
    demission_reason = fields.Char(string='离职原因')
    demission_date = fields.Datetime(string='离职时间',require = True)
    is_recruit = fields.Boolean(string='是否招聘')

    @api.multi
    @api.depends('employee_id')
    def store_demission_message(self):
        for x in self:
            if x.employee_id:
                x.contract_name = x.employee_id.nantian_erp_contract_id
                x.contract_post = x.employee_id.contract_jobs_id
                x.sro_project = x.employee_id.working_team_id


    def create(self, cr, uid, vals, context=None):
        if vals['employee_id']:
            template_model = self.pool.get('hr.employee')
            id = str(vals['employee_id'])
            ids = template_model.search(cr, uid, [('id', '=', id)], context=None)
            objects = template_model.browse(cr, uid, ids, context=None)
            for object in objects:
                object.dis_states = u'申请离职'
                print object.dis_states
        return super(demission, self).create(cr, uid, vals, context=context)


#  客户动态或人事变动
class customer_adjust(models.Model):
    _name = 'nantian_erp.customer_adjust'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')
    major_adjust = fields.Boolean(string='近一月客户是否有重大动态或人事变动')
    major_adjust_detail = fields.Char(string='详情叙述')



# 项目进度
class project_progress(models.Model):
    _name = 'nantian_erp.project_progress'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')
    major_change = fields.Boolean(string='本周是否重大变更')
    major_change_detail = fields.Char(string='详情叙述')
    repeat = fields.Boolean(string='本周是否重保')
    repeat_detail = fields.Char(string='详情叙述')
    major_fault = fields.Boolean(string='本周是否重大事故')
    major_fault_detail = fields.Char(string='详情叙述')
    maintenance = fields.Boolean(string='本周是否主机维护')
    maintenance_detail = fields.Char(string='详情叙述')
    ver_on_line = fields.Boolean(string='本周是否版本上线')
    ver_on_line_detail = fields.Char(string='详情叙述')
    equipment_implementation = fields.Boolean(string='本周是否设备实施')
    equipment_implementation_detail = fields.Char(string='详情叙述')
    special = fields.Boolean(string='本周是否有特殊事项')
    special_detail = fields.Char(string='详情叙述')
    possible_risk = fields.Boolean(string='本周预计可能风险')
    possible_risk_detail = fields.Char(string='详情叙述')

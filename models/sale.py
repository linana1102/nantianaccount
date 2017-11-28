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
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    pres_sale_ids = fields.One2many('nantian_erp.pres_sale','weekly_reports_id',string='售前项目进展')
    gathering_ids = fields.One2many('nantian_erp.project_gathering','weekly_reports_id',string='项目收款')
    # pers_transfer_ids = fields.Many2many('nantian_erp.pers_transfer','emp_weekly_transfer_ref','weekly_reports_id',string='人员调动')
    pers_transfer_ids = fields.One2many('nantian_erp.pers_transfer','weekly_reports_id',string='人员调动')
    demission_ids = fields.One2many('nantian_erp.demission','weekly_reports_id',string='人员离职')
    customer_adjust_ids = fields.One2many('nantian_erp.customer_adjust','weekly_reports_id',string='客户动态或人事变动')
    project_progress_ids = fields.One2many('nantian_erp.project_progress','weekly_reports_id',string='项目进度')
    recruit_gap_ids = fields.One2many('nantian_erp.recruit_gap','weekly_reports_id',string='现有招聘缺口')
    project_stage_count_ids = fields.One2many('nantian_erp.project_stage_count','weekly_reports_id',string='项目阶段数目统计',required=True)
    lixiang = fields.Integer(string='立项，计划')
    todo = fields.Integer(string='实施')
    juys = fields.Integer(string='阶段验收')
    ywfw = fields.Integer(string='运维服务期')
    zhongyan = fields.Integer(string='终验')
    djx = fields.Integer(string='待结项')
    project_stage_count = fields.Integer(compute='_compute_project_stage_count',string='项目阶段数目统计',store=True)

    @api.multi
    @api.depends('lixiang', 'todo',"juys","ywfw","zhongyan","djx")
    def _compute_project_stage_count(self):
        for x in self:
            x.project_stage_count = x.lixiang +x.todo +x.juys +x.ywfw +x.zhongyan +x.djx



    # 自动化动作每周创建一个周报，内容是copy上一周周报的所有内容
    # 弃用
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

    # # 复制周报按钮，内容是copy上一周周报的所有内容
    @api.multi
    def copy_report(self):
        now = fields.datetime.now()
        SevenDayAgo = fields.Date.to_string((now - datetime.timedelta(days=8)))
        for record in self:
            weekly_report_object = self.env['nantian_erp.weekly_reports'].create(
                {"user_id": record.user_id.id,
                "lixiang": record.lixiang,
                "todo": record.todo,
                "juys": record.juys,
                "ywfw": record.ywfw,
                "zhongyan": record.zhongyan,
                "djx": record.djx},
            )
            print "查看"
            print weekly_report_object,weekly_report_object.id
            # 复制售前项目
            if record.pres_sale_ids:
                for x in record.pres_sale_ids:
                    object1 = self.env['nantian_erp.pres_sale'].search([("id", "=", x.id)],limit=1)
                    if object1:
                        obt = self.env['nantian_erp.pres_sale'].create(
                            {"weekly_reports_id": weekly_report_object.id,
                            "project_name": object1.project_name,
                            "contract_name": object1.contract_name,
                            "partner": object1.partner,
                            "process_scrib": object1.process_scrib,
                            "before_bid_amount": object1.before_bid_amount,
                            "bid_commpany": object1.bid_commpany,
                            "pre_bid_date": object1.pre_bid_date,
                            "competitors": object1.competitors,
                            "rate_of_success": object1.rate_of_success,
                            "salesman_id": object1.salesman_id,
                            "contract_number": object1.contract_number,
                            "bid_write": object1.bid_write,
                            "bid_checkman_id": object1.bid_checkman_id.id,
                            "bid_readman_id": object1.bid_readman_id.id,
                            "after_bid_amount": object1.after_bid_amount,
                            "term": object1.term,
                            "firm_platform": object1.firm_platform,
                            "siger": object1.siger.id,
                            "sign_date": object1.sign_date,
                            "state": object1.state,
                            "state_w": object1.state_w},
                        )
            # 复制项目收款
            if record.gathering_ids:
                for y in record.gathering_ids:
                    object_y = self.env['nantian_erp.project_gathering'].search([("id", "=", y.id)], limit=1)
                    if object_y:
                        obt_y = self.env['nantian_erp.project_gathering'].create(
                            {"weekly_reports_id": weekly_report_object.id,
                            "contract_id": object_y.contract_id.id,
                            "gather_date": object_y.gather_date,
                            "gather_progress": object_y.gather_progress,
                            "gather_count": object_y.gather_count,
                            "gather_reminder": object_y.gather_reminder},
                        )
            # 复制招聘缺口
            if record.recruit_gap_ids:
                for z in record.recruit_gap_ids:
                    object_z = self.env['nantian_erp.recruit_gap'].search([("id", "=", z.id)], limit=1)
                    if object_z:
                        obt_z = self.env['nantian_erp.recruit_gap'].create(
                            {"weekly_reports_id": weekly_report_object.id,
                            "job": object_z.job,
                            "count": object_z.count,
                            "reason": object_z.reason},
                        )
            if record.project_progress_ids:
                for a in record.project_progress_ids:
                    object_a = self.env['nantian_erp.project_progress'].search([("id", "=", a.id)], limit=1)
                    if object_a:
                        obt_a = self.env['nantian_erp.project_progress'].create(
                            {"weekly_reports_id": weekly_report_object.id,
                            "major_change": object_a.major_change_detail,
                            "major_change_detail": object_a.major_change_detail,
                            "repeat": object_a.repeat,
                            "repeat_detail": object_a.repeat_detail,
                            "major_fault": object_a.major_fault,
                            "major_fault_detail": object_a.major_fault_detail,
                            "maintenance": object_a.maintenance,
                            "maintenance_detail": object_a.maintenance_detail,
                            "ver_on_line": object_a.ver_on_line,
                            "ver_on_line_detail": object_a.ver_on_line_detail,
                            "equipment_implementation": object_a.equipment_implementation,
                            "equipment_implementation_detail": object_a.equipment_implementation_detail,
                            "special": object_a.special,
                            "special_detail": object_a.special_detail,
                            "possible_risk": object_a.possible_risk,
                            "possible_risk_detail": object_a.possible_risk_detail},
                        )
            # 复制招聘缺口
            if record.customer_adjust_ids :
                for b in record.customer_adjust_ids :
                    object_b = self.env['nantian_erp.customer_adjust'].search([("id", "=", b.id)], limit=1)
                    if object_b:
                        obt_b = self.env['nantian_erp.customer_adjust'].create(
                            {"weekly_reports_id": weekly_report_object.id,
                            "major_adjust": object_b.major_adjust,
                            "major_adjust_detail": object_b.major_adjust_detail},
                        )

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

    flag = fields.Char(string='同一份售前的标识',)
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
    }
    # 这个可以在确定合同内容后把东西填进去
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
class project_gathering(models.Model):
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
    _inherit = ['ir.needaction_mixin']

    @api.model
    def _needaction_domain_get(self):
        if self.env.user.employee_ids:
            employee_id = self.env.user.employee_ids[0].id
            return [('dis_states', '!=', u'调整完成'), ('after_leader', '=', employee_id)]
        else:
            return [('dis_states', '!=', u'调整完成')]

    @api.multi
    def _default_employee_id(self):
        return self.env['hr.employee'].browse(self._context.get('active_id'))


    # weekly_reports_id = fields.Many2many('nantian_erp.weekly_reports','emp_weekly_transfer_ref',"pers_transfer_ids", string='周报')
    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports',string='周报')
    # employee_id_hr = fields.Many2one('hr.employee',string='调动人',ondelete='set null')#
    employee_id = fields.Many2one('hr.employee',string='调动人',required=True,default=_default_employee_id)
    res_contract_name = fields.Many2one("nantian_erp.contract",compute = "store_transfer_message",store = True,string='合同名称')
    res_contract_job = fields.Many2one("nantian_erp.jobs",compute = "store_transfer_message",store = True,string='合同岗位')
    sour_team = fields.Many2one("nantian_erp.working_team",compute = "store_transfer_message",store = True,string='原项目组')
    move_reason = fields.Char(string='调动原因')
    move_date = fields.Date(string='调动时间')
    is_recruit = fields.Boolean(string='是否招聘')
    after_leader = fields.Many2one('hr.employee',string='调动后负责人',domain="['|','|',('job_id','=',u'部门经理'),('job_id','=',u'副总经理'),('job_id','=',u'总经理')]")
    before_leader = fields.Many2one('res.users',string='调动前负责人')
    # default=lambda self: self.env.user.employee_ids[0] 用户可能不是员工就不能适合default
    des_team = fields.Many2one("nantian_erp.working_team",string='新项目组')
    des_contract_name = fields.Many2one("nantian_erp.contract",string='新合同名称')
    des_contract_job = fields.Many2one("nantian_erp.jobs",string='新合同岗位')
    dis_states = fields.Selection([
        (u'待调整', u"待调整"),
        (u'可调用', u"可调用"),
        (u'借调中', u"借调中"),
        (u'调整完成', u"调整完成"),

    ], default=u'待调整',string="调整状态",store = "True")

    def create(self, cr, uid, vals, context=None):
        if vals['employee_id']:
            template_model = self.pool.get('hr.employee')
            id = str(vals['employee_id'])
            ids = template_model.search(cr, uid, [('id', '=', id)], limit=1, context=None)
            object = template_model.browse(cr, uid, ids, context=None)
            if vals['dis_states']:
                if object:
                    print object.dis_states
                    object.dis_states = vals['dis_states']
                    print object.dis_states
                else:
                    raise exceptions.ValidationError("人员的调整状态修改未成功，请手动修改！")
            else:
                object.dis_states = u"待调整"
        return super(pers_transfer, self).create(cr, uid, vals, context=context)

    @api.multi
    def subscribe_new(self):
        # 数据库找到然后
        object = self.env['hr.employee'].search([("id", "=", self.employee_id.id)], limit=1)
        if object:
            object.dis_states = self.dis_states
        else:
            raise exceptions.ValidationError("人员的调整状态修改未成功，请手动修改！")
        return {'aaaaaaaaaaaaaa'}

    @api.depends('employee_id')
    def store_transfer_message(self):
        for x in self:
            if x.employee_id:
                x.res_contract_name = x.employee_id.nantian_erp_contract_id
                x.res_contract_job = x.employee_id.contract_jobs_id
                x.sour_team = x.employee_id.working_team_id

    @api.onchange('dis_states')
    def _check_transfer_dis_states(self):
        if self.employee_id.dis_states == u"待调整":
            raise exceptions.ValidationError("人员正在待调整中,请取消提单，先处理他(她)的人员调动")
        elif self.employee_id.dis_states == u"可调用":
            raise exceptions.ValidationError("人员正在可调用中,请取消提单，先处理他(她)的人员调动")
        elif self.employee_id.dis_states == u"借调中":
            raise exceptions.ValidationError("人员正在借调中,请取消提单，先处理他(她)的人员调动")
        elif self.employee_id.dis_states == u"申请离职":
            raise exceptions.ValidationError("人员正在申请离职中,请取消提单，重新处理")
        else:
            print self.employee_id.dis_states
            print self.dis_states
            pass

    @api.multi
    def over_pers_transfer(self):
        object = self.env['hr.employee'].search([("id", "=", self.employee_id.id)], limit=1)
        if object:
            object.dis_states = u'正常'
            self.dis_states = u"调整完成"
            print object.dis_states
            if self.des_team:
                object.working_team_id = self.des_team
            if self.des_contract_name:
                object.nantian_erp_contract_id = self.des_contract_name
            if self.des_contract_job:
                object.contract_jobs_id = self.des_contract_job
        else:
            print "人员修改调整状态，未成功！"
            pass

    @api.multi
    def email_to_sys(self):
        pass


# 人员的离职
class demission(models.Model):#
    _name = 'nantian_erp.demission'

    @api.multi
    def _default_employee_id(self):
        return self.env['hr.employee'].browse(self._context.get('active_id'))

    @api.multi
    def subscribe(self):
        return {'aaaaaaaaaaaaaa'}

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')# 项目组即工作组
    user_id = fields.Many2one('res.users',string='创建者',required=True,default=lambda self: self.env.user)#
    employee_id = fields.Many2one('hr.employee',string='离职申请人',default=_default_employee_id)# 这个人的调动人是他项目组的负责人
    contract_name = fields.Char(compute = "store_demission_message",store = True,string='合同名称' )
    contract_post = fields.Char(compute = "store_demission_message",store = True,string='合同岗位')
    sro_project = fields.Char(compute = "store_demission_message",store = True,string='项目组')
    is_recruit = fields.Boolean(string='是否招聘')
    state = fields.Selection(
        [
            ('application', u'待确认'),
            ('done', u'完成'),
            ('no', u'拒绝'),
        ],
        default='application', string="离职申请状态")
    dealer = fields.Many2one('res.users',string="处理人")
    demission_reason = fields.Selection(
        [
            (u'薪资待遇不满意', u"薪资待遇不满意"),
            (u'工作环境不满意', u"工作环境不满意"),
            (u'工作发展方向不满意', u"工作发展方向不满意"),
            (u'有更好的公司选择', u"有更好的公司选择"),
            (u'家庭原因', u"家庭原因"),
            (u'身体原因', u'身体原因'),
            (u'其他', u'其他'),
        ],
        string="离职原因")
    demission_goto = fields.Text(string="离职去向")
    demission_date = fields.Date(string="离职时间")
    demission_why_add = fields.Text(string="其他原因")

    @api.multi
    def confirm_demission_dealer(self):
        object = self.env['hr.employee'].search([("id", "=", self.employee_id.id)],limit=1)
        print object
        if object:
            print object[0]
            if self.state == "done":
                self.dealer = self.env.user
                object.dis_states = u'已离职'
                object.states = u'离职'
                # x.nantian_erp_contract_id = None
                # x.working_team_id = None
                # x.contract_jobs_id = None
                object.active = 0
                if object.user_id:
                    object.user_id.active = 0
                if self.demission_date:
                    object.leave_time = self.demission_date
            elif self.state == "no":
                object.dis_states = u'正常'
                object.states = u'正常在岗'
            else:
                raise exceptions.ValidationError('请将<待确认>设置成<完成>')
        else:
            raise exceptions.ValidationError('员工已设置无效，或者不存在')
            return "false"


    @api.depends('employee_id')
    def store_demission_message(self):
        for x in self:
            if x.employee_id:
                x.contract_name = x.employee_id.nantian_erp_contract_id.name
                x.contract_post = x.employee_id.contract_jobs_id.name
                x.sro_project = x.employee_id.working_team_id.name

    def create(self, cr, uid, vals, context=None):
        if vals['employee_id']:
            template_model = self.pool.get('hr.employee')
            id = str(vals['employee_id'])
            ids = template_model.search(cr, uid, [('id', '=', id)], limit = 1,context=None)
            object = template_model.browse(cr, uid, ids, context=None)
            if vals['state'] == 'application':
                print object.dis_states
                print object.states
                object.dis_states = u'申请离职'
                object.states = u'离职办理中'
                print object.dis_states
                print object.states
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


class recruit_gap(models.Model):
    _name = 'nantian_erp.recruit_gap'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')
    job = fields.Char(string='岗位')
    count = fields.Char(string='人数')
    reason = fields.Char(string='原因')

class project_stage_count(models.Model):
    _name = 'nantian_erp.project_stage_count'

    weekly_reports_id = fields.Many2one('nantian_erp.weekly_reports', string='周报')
    lixiang = fields.Char(string='立项，计划')
    todo = fields.Char(string='实施')
    juys= fields.Char(string='阶段验收')
    ywfw = fields.Char(string='运维服务期')
    zhongyan= fields.Char(string='终验')
    djx = fields.Char(string='待结项')
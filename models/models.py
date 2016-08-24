# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
from email.utils import formataddr
import email,math
from email.header import Header
from datetime import datetime,timedelta
import time
import string


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    project_id = fields.Many2one('project.project',ondelete='set null',)
    analytic_line_id = fields.Many2one('account.analytic.line',ondelete='set null',domain = ["journal_id","=","销售分类账"])
    contract_jobs_id = fields.Many2one('nantian_erp.jobs', ondelete='set null',string='合同岗位')
    nantian_erp_contract_id = fields.Many2one('nantian_erp.contract', ondelete='set null',string='服务合同')
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
            (u'公司储备', u"公司储备"),
            (u'合同在岗', u"合同在岗"),
            (u'合同备岗', u"合同备岗"),
            (u'合同赠送', u"合同赠送"),
            (u'公司项目', u"公司项目"),
        ],
    default = u'公司储备', string = "人员状态"
    )
    account_id = fields .Many2one('account.analytic.account', ondelete='set null', )
    res_partner_id = fields.Many2one('res.partner', ondelete='set null', )
    specialty = fields.Text(string="特长")
    certificate_direction_id = fields.Many2one(related='certificate_ids.certificate_direction_id', string='证书方向')
    certificate_category_id = fields.Many2one(related='certificate_ids.certificate_category_id', string='证书认证类型')
    certificate_institutions_id = fields.Many2one(related='certificate_ids.certificate_institutions_id', string='证书颁发机构或行业')
    certificate_level_id = fields.Many2one(related='certificate_ids.certificate_level_id', string='证书级别')
    work_age = fields.Integer(compute='_compute_work_age',store=True)
    api_res = fields.Char(default="sys")
    customer_id = fields.Many2one('res.partner', compute='_get_customer',string="客户")

    @api.depends('project_id')
    def _get_customer(self):
        for record in self:
            if record.project_id:
                record.customer_id=record.project_id.partner_id

    @api.one
    @api.depends('work_time')
    def _compute_work_age(self):
        for record in self:
            if record.work_time:
                now=fields.datetime.now()
                work_time = fields.Datetime.from_string(record.work_time)
                months = int(str(now.month))-int(str(work_time.month))
                days =int(str(now.day)) - int(str(work_time.day))
                if months<0 or (months == 0 and days<0):
                    record.work_age=int(str(now.year))-int(str(work_time.year))-1
                else:
                    record.work_age = int(str(now.year)) - int(str(work_time.year))

    @api.multi
    def action_to_compute_work_age(self):
        recs = self.env['hr.employee'].search([])
        for record in recs:
            if record.work_time:
                now = fields.datetime.now()
                work_time = fields.Datetime.from_string(record.work_time)
                months = int(str(now.month)) - int(str(work_time.month))
                days = int(str(now.day)) - int(str(work_time.day))
                if months < 0 or (months == 0 and days < 0):
                    record.work_age = int(str(now.year)) - int(str(work_time.year)) - 1
                else:
                    record.work_age = int(str(now.year)) - int(str(work_time.year))

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

    @api.multi
    def hr_to_user(self):
        recs = self.env['hr.employee'].search([('api_res', '=', 'web_api'), ('user_id', '=', None)])
        for rec in recs:
            user = self.env['res.users'].create(
                {'login': rec.work_email, 'password': '123456', 'name': rec.name})
            rec.user_id = user

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

    """
    @api.multi
    @api.depends('name','product_id')
    def name_get(self):
       return [(r.id,(r.name+'('+(r.product_id.name)+')')) for r in self]
    """

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    need_employee_count = fields.Integer(compute='_need_count_employees',store=True)
    employee_count=fields.Integer(compute='_count_employees',store=True)

    @api.depends('line_ids.unit_amount')
    def _need_count_employees(self):
        for record in self:
            record.need_employee_count = 0
            for line in self.line_ids:
                record.need_employee_count += line.unit_amount

    @api.depends('line_ids.employee_count')
    def _count_employees(self):
        for record in self:
            #record.employee_count=0
            for line in self.line_ids:
                record.employee_count +=line.employee_count

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
    time = fields.Date(placeholder="截止日期",string="有效期",default=datetime(9999,12,31))
    is_forever_validate = fields.Boolean(string="是否长期有效",default = False)
    employee_ids = fields.Many2one('hr.employee',ondelete='set null')


    def expiration_reminder(self, cr, uid, erp_server_addr, context=None):
        '''
        证书过期提醒。
        每天执行一次，检测当天到期的证书，给证书主人及其上级发送一封到期提醒邮件。
        重复执行的设置钩子，在【设置】-【技术】-【自动化】-【安排的动作】里增加一条每天执行一次的动作。
        设置需要一个参数，表示邮件里用于用户点击的链接。
        另外，需要设置出去的邮件服务器.
        '''
        log_line_head = "### zhengshu daoqi tixing: "
        exp_cers_ids = self.search(cr, uid, [("time", "=", time.strftime("%Y-%m-%d"))], context=context)
        exp_cers = self.browse(cr, uid, exp_cers_ids, context=context)

        dai_fa_song = {}  # format:
        # {hr_employee.id: {obj: hr_employee
        #                   users: {hr_employee.id: {obj: hr_employee
        #                                            cers: [nantian_erp.certificate]
        #                                           }
        #                          }
        #                   }
        # }

        for cer in exp_cers:
            if not cer.employee_ids:
                continue
            user = cer.employee_ids
            mgr = None
            mgr_id = None
            if user.parent_id:
                mgr = user.parent_id
                mgr_id = mgr.id
            if not dai_fa_song.has_key(mgr_id):
                dai_fa_song[mgr_id] = {
                    "obj": mgr,
                    "users": {}
                }
            if not dai_fa_song[mgr_id]["users"].has_key(user.id):
                dai_fa_song[mgr_id]["users"][user.id] = {
                    "obj": user,
                    "cers": []
                }
            dai_fa_song[mgr_id]["users"][user.id]['cers'].append(cer)

        failed_users = []

        for mid, mgr in dai_fa_song.items():
            users = mgr['users']
            mgr = mgr['obj']
            if mgr != None:
                if not mgr.work_email:
                    failed_users.append(mgr)
                else:
                    to_list = [formataddr((Header(mgr.name_related, "utf8").encode(), mgr.work_email.encode("utf8")))]
                    mail_content = u"<div>%s 您好:" \
                                   u"<p>您的下属中有如下成员证书已经到期，特此提醒。</p>" \
                                   u"<ol>%s</ol>" \
                                   u"<p>详情请登录南天ERP查询：<a href='%s'>%s</a></p>" \
                                   u"<p>南天电子</p></div>" \
                        %(mgr.name_related,
                        "".join([u"<li>%s 证书【%s】到期时间 %s 。</li>" %(user['obj'].name_related, c.name, c.time)
                            for user_id, user in users.items() for c in user["cers"]]),
                        erp_server_addr, erp_server_addr)
                    mail_mail = self.pool.get('mail.mail')
                    mail_id = mail_mail.create(cr, uid, {
                        'body_html': mail_content,
                        'subject': Header(u'证书过期提醒', 'utf-8').encode(),
                        'email_to': to_list,
                        'auto_delete': True,
                    }, context=context)
                    # print("%s sending to %s(%s)..." %(log_line_head, mgr.name_related, mgr.work_email))
                    mail_mail.send(cr, uid, [mail_id], context=context)

            for user_id, user in users.items():
                cers = user['cers']
                user = user['obj']
                if not user.work_email:
                    failed_users.append(user)
                    continue
                to_list = [formataddr((Header(user.name_related, "utf8").encode(), user.work_email.encode("utf8")))]
                mail_content = u"<div>%s 您好：" \
                               u"<p>您有如下证书已经到期：</p>" \
                               u"<ol>%s</ol>" \
                               u"<p>详情请登录南天ERP查询：<a href='%s'>%s</a></p>" \
                               u"<p>南天电子</p></div>" \
                    %(user.name_related,
                    "".join([u"<li>%s 到期时间 %s</li>" % (c.name, c.time) for c in cers]),
                    erp_server_addr, erp_server_addr)

                mail_mail = self.pool.get('mail.mail')
                mail_id = mail_mail.create(cr, uid, {
                    'body_html': mail_content,
                    'subject': Header(u'证书过期提醒', 'utf-8').encode(),
                    'email_to': to_list,
                    'auto_delete': True,
                }, context=context)
                # print("%s sending to %s(%s)..." %(log_line_head, user.name_related, user.work_email))
                mail_mail.send(cr, uid, [mail_id], context=context)

        # if failed_users:
        #     print("%s send failed users(email is empty): %s items. [%s]" %(log_line_head, len(failed_users),
        #         ", ".join(["%s(%s)" %(user.name_related, user.id) for user in failed_users])))
        # print(dai_fa_song)



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
class hr_dimission(models.Model):
    _name = 'nantian_erp.hr_dimission'

    employee_ids = fields.Many2one('hr.employee', ondelete='set null',default=lambda self: self.env.user.employee_ids[0])
    dimission_why = fields.Selection(
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
    dimission_goto = fields.Text(string="离职去向")
    dimission_why_add = fields.Text(string="其他原因")
    state = fields.Selection(
        [
            ('application', u'离职申请'),
            ('check', u'审批'),
            ('again_check', u'总经理审批'),
            ('done', u'完成'),
            ('no',u'拒绝'),
        ],
        default='application', string="离职申请状态")
    dealer = fields.Many2one('res.users',string="处理人")
    hr_officer = fields.Many2one('hr.employee',string="审批人")
    hr_officer_user = fields.Many2one(related='hr_officer.user_id',string="审批人用户")
    hr_manager = fields.Many2one('hr.employee',string="最终审批人")
    hr_manager_user = fields.Many2one(related='hr_manager.user_id',string="最终审批人用户")

    @api.multi
    def dimission_apply(self):


        if  self.employee_ids.department_id.manager_id:
            if self.env['res.users'].search([('employee_ids', 'ilike', self.employee_ids.department_id.manager_id.id)],
                                            limit=1) in self.env['res.groups'].search([('name', '=', "Manager"),('category_id.name','=','Human Resources')]).users:
                self.hr_manager = self.employee_ids.department_id.manager_id
                self.state = 'application'
            elif self.employee_ids.department_id.manager_id == self.employee_ids:
                self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
                self.state = 'application'
            else:

                self.hr_officer = self.employee_ids.department_id.manager_id
                if self.employee_ids.department_id.parent_id.manager_id:
                    self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
                    self.state = 'application'
                else:
                    raise exceptions.ValidationError('您需要一个总经理去处理您的离职申请')
        else:
            raise exceptions.ValidationError('您没有经理去处理您的离职申请')
    def dimission_check(self):
        if self.hr_manager:
            if self.hr_officer:
                self.state = 'check'
                self.dealer = self.hr_officer_user
            else:
                self.state = 'again_check'
                self.dealer = self.hr_manager_user

    def dimission_again_check(self):
        self.state = 'again_check'
        self.dealer = self.hr_manager_user
    def dimission_done(self):
        self.state = 'done'
        self.employee_ids.active = 0
    def dimission_no(self):
        self.state = 'no'

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    state = fields.Selection([
         ('draft', "新建"),
         ('confirmed', "待确认"),
         ('done', "已确认"),
    ], default=lambda self: self._get_state())
    examine_user = fields.Many2one('res.users',string='审批人',default=lambda self: self._get_examine_user())

    @api.multi
    def _get_state(self):
        pro_manager = []
        dep_manager = []
        for project in self.env['project.project'].search([]):
            pro_manager.append(project.user_id)
        for department in self.env['hr.department'].search([]):
            if department.manager_id:
                em = department.manager_id

                user = self.env['res.users'].search([('employee_ids', 'ilike', em.id)])

                dep_manager.append(user)
        if self.env.user not in pro_manager and self.env.user not in dep_manager:

            return 'confirmed'
        else:
            return 'done'

    @api.multi
    def _get_examine_user(self):
        pro_manager = []
        dep_manager = []
        for project in self.env['project.project'].search([]):
            pro_manager.append(project.user_id)
        for department in self.env['hr.department'].search([]):
            if department.manager_id:
                em = department.manager_id
                user = self.env['res.users'].search([('employee_ids', 'ilike', em.id)])
                dep_manager.append(user)
        if self.env.user not in pro_manager and self.env.user not in dep_manager:
            if self.env.user.employee_ids.parent_id:
                return self.env.user.employee_ids.parent_id.user_id
            else:
                return None
        else:
            return None
    @api.one
    def action_draft(self):
        self.state = 'draft'
        self.examine_user = self.employee_id.user_id

    @api.one
    def action_confirm(self):
        self.state = 'confirmed'
        self.examine_user = self.employee_id.user_id.employee_ids[0].parent_id.user_id

    @api.one
    def action_done(self):
        self.state = 'done'
class hr_leave(models.Model):
    _name = 'nantian_erp.hr_leave'
    name = fields.Char(string='请假单',)
    state = fields.Selection(
        [
            ('application', u'请假申请'),
            ('check', u'审批'),
            ('again_check', u'总经理审批'),
            ('done', u'完成'),
            ('no', u'拒绝'),
        ],
        default='application', string="离职申请状态")
    dealer = fields.Many2one('res.users', string="处理人")
    hr_officer = fields.Many2one('hr.employee', string="审批人")
    hr_officer_user = fields.Many2one(related='hr_officer.user_id', string="审批人用户")
    hr_manager = fields.Many2one('hr.employee', string="最终审批人")
    hr_manager_user = fields.Many2one(related='hr_manager.user_id', string="最终审批人用户")
    employee_ids = fields.Many2one('hr.employee', string="申请人",ondelete='set null',default=lambda self: self.env.user.employee_ids[0])
    leave_type = fields.Many2one('nantian_erp.hr_leave_type', string="请假类型")
    date_from = fields.Datetime(string="开始日期")
    date_to = fields.Datetime(string="结束日期")
    reason = fields.Text(string="请假原因")

    @api.multi
    def leave_apply(self):

        if self.env.user in self.env['res.groups'].search([('name', '=', "Manager"),('category_id.name','=','Human Resources')]).users:
            self.state = 'done'
        elif self.employee_ids.child_ids or self.env.user in self.env['project.project'].user_id or self.employee_ids==self.employee_ids.department_id.manager_id:
            if self.leave_type.name == "轮休假":
                self.state = 'done'
            elif self.env['res.users'].search([('employee_ids', 'ilike',self.employee_ids.department_id.manager_id.id)],limit=1) in self.env['res.groups'].search([('name', '=', "Manager")]).users:

                self.hr_manager = self.employee_ids.department_id.manager_id
                self.state = 'application'
            elif self.env['res.users'].search([('employee_ids', 'ilike',self.employee_ids.department_id.parent_id.manager_id.id)],limit=1) in self.env['res.groups'].search([('name', '=', "Manager")]).users:
                self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
                self.state = 'application'
            else:
                raise exceptions.ValidationError('您需要一个总经理去处理您的请假申请')
        elif self.employee_ids.parent_id:
            if self.env['res.users'].search([('employee_ids', 'ilike',self.employee_ids.parent_id.id)],limit=1) in self.env['res.groups'].search([('name', '=', "Manager")]).users or self.leave_type.name == "轮休假":
                self.hr_manager = self.employee_ids.parent_id
            else:
                if self.leave_type.name == "轮休假":
                    self.hr_officer = self.employee_ids.department_id.manager_id
                else:
                    self.hr_officer = self.employee_ids.department_id.manager_id
                    self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
            self.state = 'application'
        else:
            raise exceptions.ValidationError('您没有经理去处理您的请假申请')

    def leave_check(self):
        if self.hr_manager:
            if self.hr_officer:
                self.state = 'check'
                self.dealer = self.hr_officer_user
            else:
                self.state = 'again_check'
                self.dealer = self.hr_manager_user

    def leave_again_check(self):
        self.state = 'again_check'
        self.dealer = self.hr_manager_user

    def leave_done(self):
        self.state = 'done'

    def leave_no(self):
        self.state = 'no'

    @api.multi
    def onchange_date_from(self, date_to, date_from):

        if (date_from and date_to) and (date_from > date_to):
            raise exceptions.ValidationError("结束日期必须大于开始日期")

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.strptime(date_from,
                                                            tools.DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        # if (date_to and date_from) and (date_from <= date_to):
        #     diff_day = self._get_number_of_days(date_from, date_to)
        #     result['value']['number_of_days'] = round(math.floor(diff_day)) + 1
        # else:
        #     result['value']['number_of_days'] = 0

        return result

    @api.multi
    def onchange_date_to(self, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise exceptions.ValidationError("结束日期必须大于开始日期")

        result = {'value': {}}

        # Compute and update the number of days
        # if (date_to and date_from) and (date_from <= date_to):
        #     diff_day = self._get_number_of_days(date_from, date_to)
        #     result['value']['number_of_days'] = round(math.floor(diff_day)) + 1
        # else:
        #     result['value']['number_of_days'] = 0

        return result
class hr_leave_type(models.Model):
    _name = 'nantian_erp.hr_leave_type'
    name = fields.Char(string='请假类型')

class jobs(models.Model):
    _name = 'nantian_erp.jobs'
    name = fields.Char(string='岗位名称')
    contract_id = fields.Many2one('nantian_erp.contract', string="合同")
    instruction = fields.Text(string='岗位说明')
    price = fields.Float(string = '单价')
    unit = fields.Selection(
        [
            ('year', u'年'),
            ('days', u'天'),
        ],
        string="计量单位", default='year'
    )
    amount = fields.Integer(string='数量', default=1)
    rate = fields.Selection(
        [
            ('0.00',u'0%'),
            ('0.11', u'11%'),
            ('0.17', u'17%'),
            ('0.06',u'6%')
        ],
        string="税率", default='0.00'
    )
    rated_moneys=fields.Float(compute='_count_rated_moneys', store=True, string ="税金")
    employee_ids = fields.One2many('hr.employee', 'contract_jobs_id', "Employees")
    subtotal = fields.Float(compute='_count_subtotal', store=True,string="小计")
    employee_count = fields.Integer(compute='_count_employees', store=True)

    @api.depends('employee_ids')
    def _count_employees(self):
        for record in self:
            record.employee_count = len(record.employee_ids)
    @api.depends('price','amount')
    def _count_subtotal(self):
        for record in self:
            record.subtotal = record.price*record.amount

    @api.depends('price','amount','rate')
    def _count_rated_moneys(self):
        for record in self:
            if record.rate:
                record.rated_moneys = record.price * record.amount*string.atof(record.rate)
class collection(models.Model):
    _name = 'nantian_erp.collection'
    name = fields.Char(string='名称')
    contract_id = fields.Many2one('nantian_erp.contract', string="合同")
    date = fields.Date(string='合同收款时间')
    evaluate_money = fields.Float(string='预期收款金额')
    money = fields.Float(string='实际收款金额')
    state = fields.Selection(
        [
            (u'创建中', u'创建中'),
            (u'未收款', u'未收款'),
            (u'已收款', u'已收款'),
        ],
        string="收款状态", compute='_change_state',default=u'创建中',store=True
    )
    user_id = fields.Many2one('res.users', string="操作人")
    time = fields.Datetime( string='确认时间'  )

    @api.multi
    @api.depends('evaluate_money','money')
    def _change_state(self):
        for record in self:
            if record.evaluate_money and not record.money:
                record.state = u'未收款'
            if record.money:
                record.state = u'已收款'
                record.user_id = self.env.user
                record.time = fields.datetime.now()


class contract(models.Model):
    _name = 'nantian_erp.contract'
    name = fields.Char(string='合同名称',required=True)
    header_id = fields.Many2one('res.users', string="合同负责人",default=lambda self: self.env.user)
    customer_id = fields.Many2one('res.partner', string="客户",domain="[('category','=',u'服务客户')]")
    date_start = fields.Date(string="开始日期")
    date_end = fields.Date(string="结束日期")
    need_employee_count = fields.Integer(compute='_need_count_employees', string="合同约定人数",store=True)
    employee_count = fields.Integer(compute='_count_employees', string='现场人数',store=True)
    jobs_ids = fields.One2many('nantian_erp.jobs', 'contract_id',string="合同岗位")
    money = fields.Float(string="合同金额" ,compute='_count_money',store=True)
    money_tax = fields.Float(string="税金" ,compute='_count_money_tax',store=True)
    money_total = fields.Float(string="总计金额" ,compute='_count_money_total',store=True)
    collection_ids = fields.One2many('nantian_erp.collection', 'contract_id',string="收款")
    hr_requirements = fields.Text(string="人员要求")
    resource_requirements = fields.Text(string="资源要求")
    other = fields.Text(string="其他")
    next_collection_date = fields.Date(compute='_count_next_date',string="下次收款日期",store=True)
    state = fields.Selection(
        [
            ('going',u'进行中'),
            ('off',u'关闭'),
        ],
        string="合同状态",default='going'
    )

    @api.depends('jobs_ids.amount')
    def _need_count_employees(self):
        for record in self:
            record.need_employee_count = 0
            for job in record.jobs_ids:
                record.need_employee_count += job.amount


    @api.depends('jobs_ids.employee_count')
    def _count_employees(self):
        for record in self:
            # record.employee_count=0
            for job in record.jobs_ids:
                record.employee_count += job.employee_count

    @api.depends('jobs_ids.subtotal')
    def _count_money(self):
        for record in self:
            for job in record.jobs_ids:
                record.money += job.subtotal

    @api.depends('jobs_ids.rated_moneys')
    def _count_money_tax(self):
        for record in self:
            for job in record.jobs_ids:
                record.money_tax += job.rated_moneys

    @api.depends('money','money_tax')
    def _count_money_total(self):
        for record in self:
            record.money_total = record.money - record.money_tax

    @api.depends('collection_ids.date')
    def _count_next_date(self):
        for record in self:
            dates=[]
            if record.collection_ids:
                for collection in record.collection_ids:
                    if collection.date==u'未收款':
                        dates.append(collection.date)
            if dates:
                record.next_collection_date=min(dates)
            else:
                record.next_collection_date=None



    @api.multi
    @api.depends('name', 'employee_count')
    def name_get(self):
        return [(r.id, (r.name + '-' + u'所需人数' + (str(r.need_employee_count)) + u'人')) for r in self]








class res_partner(models.Model):
    _inherit = 'res.partner'

    category =fields.Selection(
        [
            (u'服务客户', u'服务客户'),
            (u'case客户', u'case客户'),

        ],

    )
    customer_manager = fields.Many2one('res.users', ondelete='set null',default=lambda self: self.env.user)

    @api.multi
    def _onchange_to_service_customer(self,name):
        value = {}
        value['category'] = u'服务客户'
        value['is_company'] = 'True'
        return {'value':value}

    @api.multi
    def _onchange_to_case_customer(self,name):
        value={}
        value['category'] = u'case客户'
        value['is_company'] = 'True'
        return {'value':value}

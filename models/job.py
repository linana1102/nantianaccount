# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
from email.utils import formataddr
import email
from email.header import Header

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
    _rec_name = 'job_id'

    user_id = fields.Many2one('res.users',default=lambda self: self.env.user,string='申请人')
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
    reason = fields.Selection([('1','原有人员离职后增补人员'),('2','业务拓展后新增岗位'),('3','其他')],string='招聘理由')
    channel = fields.Selection([('1','招聘网站发布职位'),('2','伯乐奖职位'),('3','其他渠道')],string='招聘渠道')
    cycle = fields.Char(string='招聘周期')
    state = fields.Selection([(u'examineing', u'审批中'), (u'released',u'已发布'),(u'refused',u'被退回') ,(u'backed',u'被追回'),(u'archived',u'已归档')],default='examineing')
    examine_user = fields.Many2one('res.users',string='审批人',default=lambda self: self.compute_examine_user())
    examine_ids = fields.One2many('nantian_erp.job_examine','recruitment_id')

    def send_email(self,cr,uid,users,context=None):
        # template_model = self.pool.get('email.template')
        # ids = template_model.search(cr,uid,[('name','=','case邮件提醒')],context=None)
        # template = template_model.browse(cr,uid,ids,context=None)
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name,'utf-8').encode(),user.email)))
        mail_mail = self.pool.get('mail.mail')
        # for i in range(len(data)):
        #     if not data[i]:
        #         data[i] = ''
        mail_id = mail_mail.create(cr, uid, {
                        'body_html': '<div><p>您好:</p>'
                            '<p>有个岗位申请需要您处理,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a></p></div>',
                        # 'subject': 'Re: %s+%s+%s' %(str(data[0]).decode('utf-8').encode('gbk'),str(data[1]).decode('utf-8').encode('gbk'),str(data[2]).decode('utf-8').encode('gbk')),
                        'subject':'岗位申请',
                        'email_to': to_list,
                        'auto_delete': True,
                    }, context=context)
        mail_mail.send(cr, uid, [mail_id], context=context)

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
                user = department.manager_id.user_id
            else:
                user = department.parent_id.manager_id.user_id
        else:
            user = employee.working_team_id.partner_id.customer_manager
        self.send_email(user)
        return user


    @api.multi
    def action_to_confirm(self):
        self.state = u'examineing'
        self.examine_user = self.compute_examine_user()

    @api.multi
    def agree(self):
        self.env['nantian_erp.job_examine'].create({'user_id': self.env.user.id,'result':u'同意','recruitment_id':self.id,'date':fields.Date.today()})
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')],limit=1)
        nagmaer_group = self.env['res.groups'].search([('name', '=', u'总经理')],limit=1)
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        department = employee.department_id
        if self.env.user in customer_manager_group.users:

            if department.level == 2:
                examine_user = department.manager_id.user_id
            else:
                examine_user = department.parent_id.manager_id.user_id
            self.send_email(self.examine_user)
            self.examine_user = examine_user
        elif self.env.user in nagmaer_group.users:
            self.state = 'released'
            self.examine_user = None

    @api.multi
    def disagree(self):
        self.env['nantian_erp.job_examine'].create({'user_id': self.env.user.id,'result':u'不同意','recruitment_id':self.id,'date':fields.Date.today()})
        self.state = 'refused'
        self.examine_user = self.user_id

    @api.multi
    def back(self):
        self.state = 'backed'
        self.examine_user = self.user_id

    @api.multi
    def archive(self):
        self.state = 'archive'
        self.examine_user = None

    # 修改作为外键时的显示
    @api.multi
    @api.depends('job_id.name', 'user_id.name')
    def name_get(self):
        datas = []
        for r in self:
            datas.append((r.id, (r.job_id.name + '(' + (r.user_id.name) + ')')))
        return datas

class job_examine(models.Model):
    _name = 'nantian_erp.job_examine'

    user_id = fields.Many2one('res.users',string='审批人')
    result = fields.Selection([(u'同意',u'同意'),(u'不同意',u'不同意')])
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘需求')
    date = fields.Date(string='审批时间')


class resume(models.Model):
    _name = 'nantian_erp.resume'

    name = fields.Char(string='姓名')
    gender = fields.Selection([('male','男'),('female','女')],string='性别')
    age = fields.Integer(string='年龄')
    work_age = fields.Integer(string='工作年限')
    education = fields.Selection(
        [
            (u'专科', u"专科"),
            (u'本科', u"本科"),
            (u'硕士', u"硕士"),
            (u'博士', u"博士"),
            (u'专升本', u"专升本"),
            (u'高级技工', u"高级技工"),
            (u'高中', u"高中"),
        ],
         string='学历'
    )
    phone = fields.Char(string='电话')
    email = fields.Char(string='邮箱')
    job = fields.Char(string='求职职位')
    state = fields.Selection([(u'简历库中',u'简历库中'),(u'面试中',u'面试中'),(u'offer审批',u'offer审批'),(u'发offer',u'发offer'),(u'已入职',u'已入职'),(u'发offer未入职',u'发offer未入职'),(u'淘汰',u'淘汰'),(u'暂存',u'暂存')],default=u'简历库中')
    interviewer = fields.Many2one('res.users',string='面试官')
    interview_ids = fields.One2many('nantian_erp.interview','resume_id')
    offer_information_id = fields.One2many('nantian_erp.offer_information','resume_id',string='offer信息')
    attach_id = fields.Many2one('ir.attachment',string='简历')

    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', ids)])
        return action

    @api.multi
    def agree(self):
        self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)]).write({'result':'agree','date':fields.Date.today()})
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')],limit=1)
        nagmaer_group = self.env['res.groups'].search([('name', '=', u'总经理')],limit=1)
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        department = employee.department_id
        if self.env.user in customer_manager_group.users:
            if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review or not self.env['nantian_erp.offer_information'].search([('resume_id','=',self.id),('user_id','=',self.env.uid)])[-1].contract_time:
                raise exceptions.ValidationError("请填面试评价和offer信息 ")
            else:
                self.state = u'offer审批'
                if department.level == 2:
                    interviewer = department.manager_id.user_id
                else:
                    interviewer = department.parent_id.manager_id.user_id
                self.env['nantian_erp.offer_information'].search([('resume_id','=',self.id),('user_id','=',self.env.uid)]).write({'examiner_user':interviewer.id})
                self.interviewer = interviewer
        elif self.env.user == self.interview_ids[0].recruitment_id.user_id:
            if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                raise exceptions.ValidationError("请填面试评价")
            else:
                interviewer = self.interview_ids[0].recruitment_id.working_team_id.partner_id.customer_manager.id
                print interviewer
                self.env['nantian_erp.interview'].create({'resume_id':self.id,'recruitment_id':self.interview_ids[0].recruitment_id.id,'interviewer':interviewer})
                self.env['nantian_erp.offer_information'].create({'resume_id':self.id,'recruitment_id':self.interview_ids[0].recruitment_id.id,'user_id':interviewer,})
                self.interviewer = interviewer

        else:
            self.state = u'发offer'
            self.interviewer = None

    @api.multi
    def disagree(self):
        if self.state == u'简历库中':
            self.state = u'淘汰'
        else:
            if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                raise exceptions.ValidationError("请填面试评价")
            else:
                self.state = u'淘汰'
                self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)]).write({'result':'disagree','date':fields.Date.context_today()})
                self.interviewer = None

    @api.multi
    def consider(self):
        if self.state == u'简历库中':
            self.state = u'暂存'
        else:
            if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                raise exceptions.ValidationError("请填面试评价")
            else:
                self.state = u'暂存'
                self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)]).write({'result':'consider','date':fields.Date.context_today()})
                self.interviewer = None

    # @api.multi
    # @api.onchange('interview_ids')
    # def change_state(self):
    #     print 'aaaaaaaaaa'
    #     self.state = u'审批中'

class interview(models.Model):
    _name = 'nantian_erp.interview'

    resume_id = fields.Many2one('nantian_erp.resume',string='求职者')
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘需求')
    review = fields.Text(string='面试评价')
    result = fields.Selection([('agree',u'通过'),('disagree',u'淘汰'),('consider',u'暂存')],string= '面试结果',)
    interviewer = fields.Many2one('res.users',default=lambda self: self.env.user,string='面试官')
    date = fields.Date(string='面试时间')
    # @api.onchange('result','interviewer')
    # def _onchange_price(self):
    #     if self.result == 'agree':
    #
    #     elif self.result == 'consider':
    #         self.resume_id.states = u'暂存'
    #     else:
    #         self.resume_id.states = u'淘汰'

    def create(self, cr, uid, vals, context=None):
        resume_model = self.pool.get('nantian_erp.resume')
        resume = resume_model.browse(cr,uid,vals['resume_id'],context=None)
        recruitment_model = self.pool.get('nantian_erp.recruitment')
        recruitment = recruitment_model.browse(cr,uid,vals['recruitment_id'],context=None)
        if resume.state == u'简历库中':
            print vals['resume_id']
            print vals['recruitment_id']
            print recruitment.user_id.id
            resume.state = u'面试中'
            self.create(cr,uid,{'resume_id':vals['resume_id'],'recruitment_id':vals['recruitment_id'],'interviewer':recruitment.user_id.id})
            resume.interviewer = recruitment.user_id.id
            vals['date'] = fields.Date.today()
        return super(interview,self).create(cr,uid,vals,context=context)

class offer_information(models.Model):
    _name = 'nantian_erp.offer_information'

    resume_id = fields.Many2one('nantian_erp.resume')
    phone = fields.Char(related='resume_id.phone',string='电话')
    email = fields.Char(related='resume_id.email',string='邮箱')
    entrytime = fields.Date(string= '办理入职时间')
    entry_recruitment_id = fields.Many2one('nantian_erp.recruitment',string='入职岗位')
    job_level = fields.Selection([(u'1',u'1'),(u'2',u'2'),(u'3',u'3')],related='entry_recruitment_id.job_level',string='岗位级别')
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘职位')
    channel = fields.Selection([('1','招聘网站发布职位'),('2','伯乐奖职位'),('3','其他渠道')],related='recruitment_id.channel',string='招聘渠道')
    reason = fields.Selection([('1','原有人员离职后增补人员'),('2','业务拓展后新增岗位'),('3','其他')],related='recruitment_id.reason',string='招聘理由')
    first_department_id = fields.Many2one('hr.department',related='recruitment_id.department_id.parent_id',string='一级部门')
    second_department_id = fields.Many2one('hr.department',related='recruitment_id.department_id',string='二级部门')
    working_team_id = fields.Many2one('nantian_erp.working_team',related='recruitment_id.working_team_id',string='三级工作组')
    contract_time = fields.Integer(string='合同期限')
    test_time = fields.Integer(string='试用期限')
    state = fields.Selection([(u'审批中',u'审批中'),(u'已审批',u'已审批'),(u'未通过',u'未通过')],string='状态',default=u'审批中')
    user_id = fields.Many2one('res.users',string='offer填写人')
    examiner_user = fields.Many2one('res.users',string='offer审批人')
    offer_examine_id = fields.One2many('nantian_erp.offer_examine','offer_id')

    def offer_information_email(self, cr, uid, user_id,offer,offer_examine,context=None):
        context = dict(context or {})
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'nantian_erp', 'offer_information_email_template')[1]
        print template_id
        print offer
        context['offer'] = offer
        context['offer_examine'] = offer_examine
        self.pool.get('email.template').send_mail(cr, uid, template_id, user_id, force_send=True, context=context)
        return True

    @api.multi
    def agree(self):
        self.state=u'已审批'
        self.resume_id.state = u'发offer'
        self.resume_id.interviewer = None
        offer=self.search([('id','=',self.id)])
        user_id=self.env['res.users'].search([('login','=','admin')],limit=1)[0].id
        self.env['nantian_erp.offer_examine'].create({'user_id':self.examiner_user.id,'result':u'同意','offer_id':self.id})
        offer_examine = self.env['nantian_erp.offer_examine'].search([('offer_id','=',self.id)],limit=1)
        print offer_examine.user_id.name,offer_examine.result,offer_examine.time
        self.offer_information_email(user_id,offer,offer_examine)
        self.examiner_user = None

    @api.multi
    def diagree(self):
        self.state = u'未通过'
        self.resume_id.states = u'淘汰'
        self.env['nantian_erp.offer_examine'].create({'user_id':self.examiner_user.id,'result':u'不同意','offer_id':self.id})
        self.examiner_user = None
        self.resume_id.interviewer = None

class offer_examine(models.Model):
    _name = 'nantian_erp.offer_examine'

    user_id = fields.Many2one('res.users')
    result = fields.Selection([(u'同意',u'同意'),(u'不同意',u'不同意')])
    time = fields.Date(default=fields.Date.today())
    offer_id = fields.Many2one('nantian_erp.offer_information')

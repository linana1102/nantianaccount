# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
from email.utils import formataddr
import email
from email.header import Header
from cStringIO import StringIO
from docxtpl import DocxTemplate,InlineImage
import os,sys
import base64
import xlwt


# 岗位类别表
class categroy(models.Model):
    _name = 'nantian_erp.categroy'
    name = fields.Char()


# 岗位表
class jobs(models.Model):
    _name = 'nantian_erp.job'

    name = fields.Char(string='名称')
    categroy_id = fields.Many2one('nantian_erp.categroy',string='岗位类别')


# 岗位级别表
class job_categroy(models.Model):
    _name = 'nantian_erp.job_categroy'

    name = fields.Char(string='类别')
    job_id = fields.Many2one('nantian_erp.job',string='职位')

# 招聘
class recruitment(models.Model):
    _name = 'nantian_erp.recruitment'
    _rec_name = 'job_id'
    _inherit = ['ir.needaction_mixin']

    # 用于显示待处理招聘需求数量
    @api.model
    def _needaction_domain_get(self):
        return [('examine_user.id', '=', self.env.uid)]

    user_id = fields.Many2one('res.users',default=lambda self: self.env.user,string='申请人',required='True')
    department_id = fields.Many2one('hr.department',string='部门',default=lambda self: self.compute_department(),store=True,required='True')
    working_team_id = fields.Many2one('nantian_erp.working_team',string='工作组')
    working_team_id1 = fields.Many2one('nantian_erp.working_team',string='工作组')
    position_categroy_1 = fields.Many2one('nantian_erp.categroy',string='岗位类别',required='True')
    job_id =fields.Many2one('nantian_erp.job',string='职位',required='True')
    job_name = fields.Char(related='job_id.name')
    position_categroy_2 = fields.Many2one('nantian_erp.job_categroy')
    job_level = fields.Selection([(u'1',u'1'),(u'2',u'2'),(u'3',u'3'),(u'4',u'4'),(u'5',u'5')],string='职级',required='True')
    duties = fields.Text(string= '职责',required='True')
    requirements = fields.Text(string='要求',required='True')
    salary = fields.Char(string='薪资',required='True')
    current_employee_num = fields.Integer(string='现有人数')
    need_people_num = fields.Integer(string='招聘人数',required='True')
    reason = fields.Selection([('1','原有人员离职后增补人员'),('2','业务拓展后新增岗位'),('3','其他')],string='招聘理由',required='True')
    channel = fields.Selection([('1','招聘网站发布职位'),('2','伯乐奖职位'),('3','其他渠道')],string='招聘渠道',required='True')
    cycle = fields.Char(string='招聘周期')
    state = fields.Selection([(u'examineing', u'审批中'), (u'released',u'已发布'),(u'refused',u'被退回') ,(u'backed',u'被追回'),(u'archived',u'已归档')],default='examineing')
    examine_user = fields.Many2one('res.users',string='审批人',)
    examine_ids = fields.One2many('nantian_erp.job_examine','recruitment_id')
    hired_num = fields.Integer(string='已招聘人数')
    work_place = fields.Char(string= '工作地点')
    phone = fields.Char(string='联系电话')

    # 创建招聘需求
    def create(self, cr, uid, vals, context=None):
        # 获取创建人或者当前登录人
        user = self.pool.get('res.users').browse(cr,uid,uid,context=None)
        # 如果是招聘人员创建可以选择所有的工作组，根据选择的工作组赋值
        if vals['working_team_id1'] and not vals['working_team_id']:
            vals['working_team_id'] = vals['working_team_id1']
        # 获取行业负责人组
        groups_model = self.pool.get('res.groups')
        customer_group_ids = groups_model.search(cr, uid, [('name', '=', u'行业负责人')],limit=1, context=context)
        customer_manager_group = groups_model.browse(cr,uid,customer_group_ids,context=None)
        # 获取招聘组
        recruit_group_ids = groups_model.search(cr, uid, [('name', '=', u'招聘组')],limit=1,context=context)
        recruit_group = groups_model.browse(cr,uid,recruit_group_ids,context=None)

        # 获取当前登录人的员工
        employee_model = self.pool.get('hr.employee')
        employee_ids = employee_model.search(cr,uid,[('user_id','=',uid)],limit=1,context=None)
        employee =employee_model.browse(cr,uid,employee_ids,context=None)

        # 当前登录人部门
        department = employee[0].department_id

        # 获取要招聘的工作组
        working_team_model =self.pool.get('nantian_erp.working_team')
        working_team = working_team_model.browse(cr,uid,vals['working_team_id'],context=None)
        # 如果当前登录人是行业负责人或者如果所选工作组没有行业
        if (user in customer_manager_group[0].users and user not in recruit_group[0].users) or not working_team.partner_id:
            # 当前登录人的部门是二级部门(数据中心服务部)但不是部门经理,审批人为二级部门经理
            if department.level == 2 and user != department.manager_id.user_id:
                exam_user = department.manager_id.user_id
            # 当前登录人的部门是二级部门(数据中心服务部)并且是部门经理，审批人为空，并且将状态置为已发布
            elif department.level == 2 and user == department.manager_id.user_id:
                exam_user = None
                vals['state'] = 'released'
                # 发邮件通知招聘人员
                self.send_email(cr, uid, recruit_group[0].users, context=None)
            # 是行业负责人但部门不是二级部门，审批人为上级部门领导
            else:
                user_model = self.pool.get('res.users')
                user_ids = user_model.search(cr, uid, [('employee_ids', 'like', department.parent_id.manager_id.id)], limit=1, context=None)

                exam_user = user_model.browse(cr, uid,user_ids, context=None)
                print exam_user
                # exam_user = department.parent_id.manager_id.user_id
        # 如果当前登录人（创建人）不是行业负责人是招聘负责人（比如王慧）,审批人为所选工作组的行业负责人
        elif user in recruit_group[0].users:
            exam_user = working_team.partner_id.customer_manager
        # 如果当前登录人（创建人）是其他人（工作组组长），审批人为所选工作组的行业负责人
        else:
            exam_user = working_team.partner_id.customer_manager
        # 如果审批人不为空，发邮件通知审批人
        if exam_user:
            vals['examine_user']=exam_user.id
            self.send_email(cr,uid,exam_user,context=None)
        return super(recruitment,self).create(cr,uid,vals,context=context)

    # 发邮件通知有待处理的岗位需求，users为接收人,attach_ids为附件（岗位申请需求表）
    def send_email(self,cr,uid,users,attach_ids=[],context=None):
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name,'utf-8').encode(),user.email)))
        mail_mail = self.pool.get('mail.mail')
        mail_id = mail_mail.create(cr, uid, {
                        'body_html': '<div><p>您好:</p>'
                            '<p>招聘申请需要您处理,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a></p></div>',
                        'subject':'岗位申请',
                        'email_to': to_list,
                        # 'email_to':'linana@nantian.com.cn',
                        'auto_delete': True,
                        'attachment_ids':[[6,0,attach_ids]] or ''
                    }, context=context)
        mail_mail.send(cr, uid, [mail_id], context=context)

    # 用于计算需求人的的部门，给部门赋初值
    @api.multi
    @api.depends('user_id')
    def compute_department(self):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        return employee.department_id

    # 用于计算需求人的的工作组，给工作组赋初值
    @api.multi
    @api.depends('user_id')
    def compute_working_team(self):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        return employee.working_team_id

    # 用于计算审批人，主要用于被退回再次提交
    @api.multi
    def compute_examine_user(self):
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')],limit=1)
        recruit_group = self.env['res.groups'].search([('name', '=', u'招聘组')],limit=1)
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        department = employee.department_id
        if (self.env.user in customer_manager_group.users and self.env.user not in recruit_group[0].users) or not self.working_team_id .partner_id:
            if department.level == 2 and self.env.user != department.manager_id.user_id:
                user = department.manager_id.user_id
            else:
                user = self.env['res.users'].search([('employee_ids','like',department.parent_id.manager_id.id)],limit=1)
                # user = department.parent_id.manager_id.user_id
        elif self.env.user in recruit_group.users:
            user = self.working_team_id.partner_id.customer_manager
        else:
            user = self.working_team_id.partner_id.customer_manager
        self.send_email(user)
        return user

    # 提交按钮对应的函数，修改状态和审批人
    @api.multi
    def action_to_confirm(self):
        self.state = u'examineing'
        self.examine_user = self.compute_examine_user()

    # 同意按钮对应的函数，修改状态和审批人
    @api.multi
    def agree(self):
        # 系统自动创建一条同意的审批记录
        self.env['nantian_erp.job_examine'].create({'user_id': self.env.user.id,'result':u'同意','recruitment_id':self.id,'date':fields.Date.today()})
        # 行业负责人组
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')],limit=1)
        # 总经理组
        nagmaer_group = self.env['res.groups'].search([('name', '=', u'总经理')],limit=1)
        # 当前审批人对应的员工
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        # 当前审批人的部门
        department = employee.department_id
        # 招聘组
        recruitment_group = self.env['res.groups'].search([('name', '=', u'招聘组')],limit=1)
        # 当前审批人是行业负责人但不是总经理
        if self.env.user in customer_manager_group.users and self.env.user not in nagmaer_group.users:
            # 当前审批人的部门为二级部门（数据中心服务部），下步审批人为二级部门经理
            if department.level == 2:
                examine_user = department.manager_id.user_id
            else:
                examine_user = department.parent_id.manager_id.user_id
            # 发邮件通知审批人
            self.send_email(examine_user)
            # 修改审批人
            self.examine_user = examine_user
        # 当前审批人是总经理
        elif self.env.user in nagmaer_group.users:
            #根据招聘需求生成对应模板
            self.export_recruitment()
            # 查找招聘需求对应的附件
            attachment_ids = self.env['ir.attachment'].search(
                    [('res_id', '=', self.id), ('res_model', '=', 'nantian_erp.recruitment')])
            attach_ids = []
            for attach in attachment_ids:
                attach_ids.append(attach.id)
            # 发邮件给招聘负责人
            self.send_email(recruitment_group.users,attach_ids)
            # 修改状态为已发布
            self.state = 'released'
            # 审批人置为空
            self.examine_user = None

    # 不同意对应的按钮
    @api.multi
    def disagree(self):
        # 创建一条不同意的审批记录
        self.env['nantian_erp.job_examine'].create({'user_id': self.env.user.id,'result':u'不同意','recruitment_id':self.id,'date':fields.Date.today()})
        # 修改状态
        self.state = 'refused'
        #发邮件通知需求方
        self.send_email(self.user_id)
        # 处理人置为需求方
        self.examine_user = self.user_id

    # 追回对应的按钮
    @api.multi
    def back(self):
        # 创建一条追回记录
        self.env['nantian_erp.job_examine'].create({'user_id': self.env.user.id,'result':u'追回','recruitment_id':self.id,'date':fields.Date.today()})
        self.state = 'backed'
        self.examine_user = self.user_id

    # 归档按钮
    @api.multi
    def archive(self):
        self.state = 'archived'
        self.examine_user = None

    # 修改作为外键时的显示
    @api.multi
    @api.depends('job_id.name', 'user_id.name')
    def name_get(self):
        datas = []
        for r in self:
            if r.job_id.name and r.position_categroy_2.name:
                datas.append((r.id, (r.position_categroy_2.name+r.job_id.name + '(' + (r.user_id.name)+ ')')))
            elif r.job_id.name:
                datas.append((r.id, (str(r.job_id.name) + '(' + (str(r.user_id.name))+ ')')))
        return datas

    # 根据招聘需求和模板生成招聘需求文档，并创建与此条记录关联的附件
    @api.multi
    def export_recruitment(self):
        # 定义文件流
        f = StringIO()
        # 加载模板文档
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        tpl = DocxTemplate(path.replace('\\', '/') + '/myaddons/nantian_erp/position_form.docx')
        reason1=''
        reason2=''
        reason3=''
        if self.reason == '1':
            reason1 = True
        elif self.reason == '1':
            reason2 = True
        else:
            reason3 =True
        recruitment_dict = {'user': self.user_id.name or '',
                       'first_department': self.department_id.name or '',
                       'second_department':self.department_id.parent_id.name or '',
                            # self.working_team_id.name
                       'working_team': self.working_team_id.name.replace('&', '&amp;') or '',
                       'job_name': self.job_name or '',
                       'current_num': self.current_employee_num or '',
                       'need_people_num': self.need_people_num or '',
                       'salary': self.salary or '',
                       'work_place': self.work_place  or '',
                       'cycle': self.cycle or '',
                       'reason':self.reason or '',
                       'reason1': reason1 or '',
                       'reason2': reason2 or '',
                       'reason3': reason3  or '',
                       'channel': self.channel or '',
                       'requirements':self.requirements or '',
                       'duties':self.duties or '',
                       'phone':self.phone or '',
                       }
        # 生成模板文档
        tpl.render(recruitment_dict)
        tpl.save(f)
        f.seek(0)
        # 生成附件
        self.env['ir.attachment'].create({'res_model':'nantian_erp.recruitment','res_id':self.id,'datas_fname':self.job_name+u'岗位申请.docx','name':self.job_name+u'岗位申请','mimetype':'application/msword','datas':base64.encodestring(f.read()),})
        f.close()


# 招聘需求审批记录表
class job_examine(models.Model):
    _name = 'nantian_erp.job_examine'

    user_id = fields.Many2one('res.users',string='审批人')
    result = fields.Selection([(u'同意',u'同意'),(u'不同意',u'不同意'),(u'追回',u'追回')])
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘需求')
    date = fields.Date(string='审批时间')

# 简历表
class resume(models.Model):
    _name = 'nantian_erp.resume'
    _rec_name ='name'
    _inherit = ['ir.needaction_mixin']

    # 显示按钮后面对应的数字
    @api.model
    def _needaction_domain_get(self):
        return [('interviewer.id', '=', self.env.uid)]

    name = fields.Char(string='姓名',required='True')
    gender = fields.Selection([('male','男'),('female','女')],string='性别',required='True')
    age = fields.Char(string='年龄',required='True')
    work_age = fields.Char(string='工作年限',required='True')
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
         string='学历',required='True'
    )
    phone = fields.Char(string='电话',required='True')
    email = fields.Char(string='邮箱',required='True')
    job = fields.Char(string='求职职位')
    state = fields.Selection([(u'简历库中',u'简历库中'),(u'面试中',u'面试中'),(u'offer审批',u'offer审批'),(u'发offer',u'发offer'),(u'已入职',u'已入职'),(u'发offer未入职',u'发offer未入职'),(u'淘汰',u'淘汰'),(u'暂存',u'暂存')],default=u'简历库中')
    interviewer = fields.Many2one('res.users',default=lambda self: self.env.user,string='面试官')
    interview_ids = fields.One2many('nantian_erp.interview','resume_id')
    offer_information_id = fields.One2many('nantian_erp.offer_information','resume_id',string='offer信息')

    # 发邮件函数
    def send_email(self,cr,uid,user,context=None):
        to_list = []
        to_list.append(formataddr((Header(user.name,'utf-8').encode(),user.email)))
        mail_mail = self.pool.get('mail.mail')
        mail_id = mail_mail.create(cr, uid, {
                        'body_html': '<div><p>您好:</p>'
                            '<p>有个面试需要您处理,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a></p></div>',
                        'subject':'面试',
                        'email_to': to_list,
                        # 'email_to':'linana@nantian.com.cn',
                        'auto_delete': True,
                    }, context=context)
        mail_mail.send(cr, uid, [mail_id], context=context)

    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', ids)])
        return action

    # 面试时同意按钮
    @api.multi
    def agree(self):
        # 判断当前登录人是不是当前面试官，如果是，可以操作，负责报错提示没有权限
        if self.env.user == self.interviewer:
            # 修改对应的面试记录
            self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)]).write({'result':'agree','date':fields.Date.today()})
            # 行业负责人组
            customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')],limit=1)
            manager_group = self.env['res.groups'].search([('name', '=', u'总经理')],limit=1)
            # 当前用户对应的员工
            employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
            # 当前用户对应部门
            department = employee.department_id
            # 招聘组
            recruit_group = self.env['res.groups'].search([('name','=',u'招聘组')],limit=1)
            ############################
            #第一条面试记录已经由简历表的简历按钮创建，并且指定了下一个面试官
            # 当前面试官是行业负责人但不是总经理
            if (self.env.user in customer_manager_group.users and self.env.user not in manager_group.users) or (not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].recruitment_id.working_team_id.partner_id):
                # 看是否填写offer信息
                if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review or \
                        not self.env['nantian_erp.offer_information'].search([('resume_id','=',self.id),('user_id','=',self.env.uid)])[-1].contract_time or\
                        not self.env['nantian_erp.offer_information'].search([('resume_id', '=', self.id), ('user_id', '=', self.env.uid)])[-1].test_time:
                    raise exceptions.ValidationError("请填您的面试评价和offer信息里的合同期限，试用期限，三项内容")
                else:
                    # 修改状态及当前审批人
                    self.state = u'offer审批'
                    if department.level == 2:

                        interviewer = department.manager_id.user_id
                    else:
                        interviewer = self.env['res.users'].search([('employee_ids', 'ilike', department.parent_id.manager_id.id)],limit=1)
                        # print department.parent_id.manager_id
                        # interviewer = department.parent_id.manager_id.user_id
                    self.env['nantian_erp.offer_information'].search([('resume_id','=',self.id),('user_id','=',self.env.uid)]).write({'examiner_user':interviewer.id})
                    self.send_email(interviewer)
                    self.interviewer = None
            # 如果面试人是招聘发起人但不是总经理
            elif self.env.user == self.interview_ids[0].recruitment_id.user_id and self.env.user not in manager_group.users:
                if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                    raise exceptions.ValidationError("请填面试评价")
                else:
                    # 下步面试人为招聘岗位对应的行业负责人
                    interviewer = self.interview_ids[0].recruitment_id.working_team_id.partner_id.customer_manager
                    # 创建一条下步面试管的面试记录
                    self.env['nantian_erp.interview'].create({'resume_id':self.id,'recruitment_id':self.interview_ids[0].recruitment_id.id,'interviewer':interviewer.id})
                    # 生成offer信息
                    self.env['nantian_erp.offer_information'].create({
                                                 'resume_id': self.id,
                                                 'name': self.name,
                                                 'phone': self.phone,
                                                 'email': self.email,
                                                 'gender': self.gender,
                                                 'recruitment_id': self.interview_ids[0].recruitment_id.id,
                                                 'entry_recruitment_id': self.interview_ids[0].recruitment_id.id,
                                                 'job_name': self.interview_ids[0].recruitment_id.job_id.name + '(' + self.interview_ids[0].recruitment_id.job_id.categroy_id.name + ')',
                                                 'job_level': self.interview_ids[0].recruitment_id.job_level,
                                                 'user_id': interviewer.id,
                                                 'first_department_id': self.interview_ids[0].recruitment_id.department_id.parent_id.id or None,
                                                 'second_department_id': self.interview_ids[0].recruitment_id.department_id.id or None,
                                                 'working_team_id': self.interview_ids[0].recruitment_id.working_team_id.id or None,
                                                 'channel': self.interview_ids[0].recruitment_id.channel or None,
                                                 'reason': self.interview_ids[0].recruitment_id.reason or None,
                    },
                                       )
                    # 发邮件给面试官
                    self.send_email(interviewer)
                    # 修改下步面试人的值
                    self.interviewer = interviewer.id

            # 如果面试官为招聘组人员,下步面试人员为招聘需求方发起人
            elif self.env.user in recruit_group.users:
                if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                    raise exceptions.ValidationError("请填面试评价")
                else:
                    self.env['nantian_erp.interview'].create({'resume_id':self.id,'recruitment_id':self.interview_ids[-1].recruitment_id.id,'interviewer':self.interview_ids[-1].recruitment_id.user_id.id})
                    self.send_email(self.interview_ids[-1].recruitment_id.user_id)
                    self.interviewer = self.interview_ids[-1].recruitment_id.user_id.id
            # 如果当面试官是总经理
            elif self.env.user not in manager_group.users:
                # 看是否填写offer信息
                if not self.env['nantian_erp.interview'].search(
                        [('resume_id', '=', self.id), ('interviewer', '=', self.env.uid)])[-1].review or not \
                self.env['nantian_erp.offer_information'].search(
                        [('resume_id', '=', self.id), ('user_id', '=', self.env.uid)])[-1].contract_time:
                    raise exceptions.ValidationError("请填面试评价和offer信息 ")
                else:
                    # 修改状态及当前审批人
                    self.state = u'发offer'
                    # 查找当前简历对应的offer信息，修改下步处理人为空，状态改为已审批
                    self.env['nantian_erp.offer_information'].search(
                            [('resume_id', '=', self.id), ('user_id', '=', self.env.uid)]).write(
                            {'examiner_user': None,'state':u'已审批'})
                    # 查找当前简历对应的offer信息，
                    offer= self.env['nantian_erp.offer_information'].search(
                            [('resume_id', '=', self.id), ('user_id', '=', self.env.uid)],limit=1)
                    # 生成offer模板
                    offer.offer_file()
                    # 查找该offer对应的附件
                    attachment_ids = self.env['ir.attachment'].search(
                            [('res_id', '=', offer.id), ('res_model', '=', 'nantian_erp.offer_information')])
                    # 查找简历文档
                    resume_attachment_ids = self.env['ir.attachment'].search(
                            [('res_id', '=', self.id), ('res_model', '=', 'nantian_erp.resume')])
                    attach_ids = []
                    for attachment_id in attachment_ids:
                        attach_ids.append(attachment_id.id)
                    for resume in resume_attachment_ids:
                        attach_ids.append(resume.id)
                    # 发邮件给招聘人员
                    offer.offer_information_email(recruit_group.users, attach_ids)
                    self.interviewer = None
        else:
            raise exceptions.ValidationError("你没有权利操作此记录")

    # 面试不同意对应的按钮
    @api.multi
    def disagree(self):
        if self.env.user == self.interviewer:
            # 如果是简历库中的简历，直接淘汰
            if self.state == u'简历库中':
                self.state = u'淘汰'
            else:
                # 其他人一定要填面试评价
                if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                    raise exceptions.ValidationError("请填面试评价")
                else:
                    # 简历状态置为淘汰
                    self.state = u'淘汰'
                    # 修改面试记录
                    self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)]).write({'result':'disagree','date':fields.Date.context_today()})
                    self.interviewer = None
        else:
            raise exceptions.ValidationError("你没有权利操作此记录")

    # 暂存对应的按钮，将简历状态改为暂存
    @api.multi
    def consider(self):
        if self.env.user == self.interviewer:
            if self.state == u'简历库中':
                self.state = u'暂存'
            else:
                if not self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)])[-1].review:
                    raise exceptions.ValidationError("请填面试评价")
                else:
                    self.state = u'暂存'
                    self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('interviewer','=',self.env.uid)]).write({'result':'consider','date':fields.Date.context_today()})
                    self.interviewer = None
        else:
            raise exceptions.ValidationError("你没有权利操作此记录")

    # 追回按钮
    @api.multi
    def back(self):
        if self.state != u'offer审批':
            self.interviewer = self.env.user
            self.env['nantian_erp.interview'].create({'resume_id':self.id,'recruitment_id':self.interview_ids[0].recruitment_id.id,'interviewer':self.env.uid})
            self.env['nantian_erp.interview'].search([('resume_id','=',self.id),('review','=',None)]).delete()
        else:
            raise exceptions.ValidationError("不能追回")

# 面试表
class interview(models.Model):
    _name = 'nantian_erp.interview'

    resume_id = fields.Many2one('nantian_erp.resume',string='求职者')
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘需求')
    review = fields.Text(string='面试评价')
    result = fields.Selection([('agree',u'通过'),('disagree',u'淘汰'),('consider',u'暂存')],string= '面试结果',)
    interviewer = fields.Many2one('res.users',default=lambda self: self.env.user,string='面试官')
    date = fields.Date(string='面试时间')
    next_user = fields.Many2one('res.users',string='下步处理人')
    rec_user = fields.Char(related = 'recruitment_id.user_id.name',string='招聘发起人')
    customer = fields.Char(related ='recruitment_id.working_team_id.partner_id.customer_manager.name',string='行业负责人')

    def create(self, cr, uid, vals, context=None):
        # 查找当前面试的简历
        resume_model = self.pool.get('nantian_erp.resume')
        resume = resume_model.browse(cr,uid,vals['resume_id'],context=None)
        # 面试对应的招聘需求
        recruitment_model = self.pool.get('nantian_erp.recruitment')
        # 行业负责人组
        groups_model = self.pool.get('res.groups')
        customer_group_ids = groups_model.search(cr, uid, [('name', '=', u'行业负责人')], limit=1, context=context)
        customer_manager_group = groups_model.browse(cr, uid, customer_group_ids, context=None)

        if resume.state == u'简历库中':
            resume.state = u'面试中'
            # 获取下步面试官，面试官已经在页面上选出
            resume.interviewer = vals['next_user']
            vals['date'] = fields.Date.today()
            # 查看是否有选择对应的招聘需求，如果有
            print resume.interviewer
            if vals.has_key('recruitment_id'):
                #生成下步面试记录（这就是为什么新的纪录在上边）
                self.create(cr, uid, {'resume_id': vals['resume_id'], 'recruitment_id': vals['recruitment_id'],
                                      'interviewer': vals['next_user']})
                # 下步处理人是否是行业负责人，如果是生成offer信息 或者对应的招聘需求没有行业
                recruitment=recruitment_model.browse(cr, uid,vals['recruitment_id'],context=None)
                # 这个位置以后会报错的，因为有的面试创建没有招聘需求
                if resume.interviewer.name == vals['customer'] or not recruitment[0].working_team_id.partner_id:
                    recruitment = recruitment_model.browse(cr, uid, vals['recruitment_id'], context=None)
                    offer_model = self.pool.get('nantian_erp.offer_information')
                    offer_model.create(cr, uid, {'resume_id': vals['resume_id'],
                                                 'name': resume.name,
                                                 'phone': resume.phone,
                                                 'email': resume.email,
                                                 'gender': resume.gender,
                                                 'recruitment_id': vals['recruitment_id'],
                                                 'entry_recruitment_id': vals['recruitment_id'],
                                                 'job_name': recruitment.job_id.name + '(' + recruitment.job_id.categroy_id.name + ')',
                                                 'job_level': recruitment.job_level, 'user_id': vals['next_user'],
                                                 'first_department_id': recruitment.department_id.parent_id.id,
                                                 'second_department_id': recruitment.department_id.id,
                                                 'working_team_id': recruitment.working_team_id.id,
                                                 'channel': recruitment.channel, 'reason': recruitment.reason},
                                       context=context)
            # 如果没有选招聘需求，并且下步处理人为行业负责人
            elif resume.interviewer in customer_manager_group.users:
                self.create(cr, uid, {'resume_id': vals['resume_id'],
                                      'interviewer': vals['next_user']})
                offer_model = self.pool.get('nantian_erp.offer_information')
                offer_model.create(cr, uid, {'resume_id': vals['resume_id'],
                                             'name': resume.name,
                                             'phone': resume.phone,
                                             'email': resume.email,
                                             'gender': resume.gender,
                                             'user_id': vals['next_user'],
                                            },
                                   context=context)
        # if resume.state == u'暂存':
        #     pass
        return super(interview,self).create(cr,uid,vals,context=context)

# offer 信息表
class offer_information(models.Model):
    _name = 'nantian_erp.offer_information'
    _rec_name = 'resume_id'
    _inherit = ['ir.needaction_mixin']

    @api.model
    def _needaction_domain_get(self):
        return [('examiner_user.id', '=', self.env.uid)]

    resume_id = fields.Many2one('nantian_erp.resume')
    name = fields.Char(string='姓名')
    phone = fields.Char(string='电话')
    email = fields.Char(string='邮箱')
    gender = fields.Selection([('male','男'),('female','女')],string='性别',)
    entrytime = fields.Date(string= '办理入职时间')
    identification_id = fields.Char(string='身份证号')
    graduation_id = fields.Char(string='毕业证编号')
    entry_recruitment_id = fields.Many2one('nantian_erp.recruitment',string='入职岗位')
    job_name = fields.Char(string='岗位名称')
    job_level = fields.Selection([(u'1',u'1'),(u'2',u'2'),(u'3',u'3'),(u'4',u'4'),(u'5',u'5'),(u'6',u'6'),(u'7',u'7'),],related='entry_recruitment_id.job_level',string='岗位级别')
    recruitment_id = fields.Many2one('nantian_erp.recruitment',string='招聘职位')
    channel = fields.Selection([('1','招聘网站发布职位'),('2','伯乐奖职位'),('3','其他渠道')],string='招聘渠道')
    reason = fields.Selection([('1','原有人员离职后增补人员'),('2','业务拓展后新增岗位'),('3','其他')],string='招聘理由')
    first_department_id = fields.Many2one('hr.department',string='一级部门')
    second_department_id = fields.Many2one('hr.department',string='二级部门')
    working_team_id = fields.Many2one('nantian_erp.working_team',string='三级工作组')
    contract_time = fields.Integer(default = 3,string='合同期限')
    test_time = fields.Integer(default = 3,string='试用期限')
    state = fields.Selection([(u'审批中',u'审批中'),(u'已审批',u'已审批'),(u'已入职',u'已入职'),(u'未设置邮箱',u'未设置邮箱'),(u'完成',u'完成'),(u'未入职',u'未入职'),(u'未通过',u'未通过')],string='状态',default=u'审批中')
    user_id = fields.Many2one('res.users',string='offer填写人')
    examiner_user = fields.Many2one('res.users',string='offer审批人')
    offer_examine_id = fields.One2many('nantian_erp.offer_examine','offer_id')
    emp_id = fields.Many2one('hr.employee',string="员工")
    entry_id = fields.Many2one('nantian_erp.entry',string='入职办理')
    work_email = fields.Char(string= '公司邮箱')
    user = fields.Many2one('res.users',)
    interview_ids = fields.One2many(related='resume_id.interview_ids')


    # 定义发邮件函数
    def offer_information_email(self, cr, uid, users, attach_ids=[], context=None):
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name, 'utf-8').encode(), user.email)))
        mail_mail = self.pool.get('mail.mail')
        print attach_ids
        mail_id = mail_mail.create(cr, uid, {
            'body_html': '<div><p>您好:</p>'
                         '<p>这有一份offer信息,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a></p></div>',
            'subject': 'offer信息',
            'email_to': to_list,
            # 'email_to':'linana@nantian.com.cn',
            'auto_delete': True,
            'attachment_ids': [[6, 0, attach_ids]] or ''
        }, context=context)
        mail_mail.send(cr, uid, [mail_id], context=context)

    # 生成offer文档，创建对应附件
    def offer_file(self):
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet('sheet1')
        f = StringIO()
        sheet.write_merge(0,1,0,0,u'序号')
        sheet.write_merge(0,0,1,2,u'部门信息')
        sheet.write_merge(0, 0, 4, 9, u'个人信息')
        sheet.write_merge(0,0,10,11,u'职位信息')
        sheet.write_merge(0,0,12,14,u'劳动合同信息')
        sheet.write_merge(0,0,15,17,u'招聘有关信息')
        head_list=["备注","招聘渠道","对应招聘岗位","试用期限（月）","劳动合同期限（年）","入职时间（劳动合同开始日期）","职级",
           "职位名称","毕业证书编号","邮箱","联系电话","性别","身份证号","姓名","三级组","三级部门","二级部门"]
        head_list.reverse()
        for index,item in enumerate(head_list):
            sheet.write(1,index+1,item,style=xlwt.Style.default_style)
        offer_information = [self.first_department_id.name,self.second_department_id.name,self.working_team_id.name,
                             self.name, self.identification_id,self.gender, self.phone,self.email,self.graduation_id,
                             self.job_name,self.job_level,self.entrytime,self.contract_time,self.test_time,
                             self.recruitment_id.job_name,self.channel ]
        for index,item in enumerate(offer_information):
            sheet.write(2,index+1,item, style=xlwt.Style.default_style)
        book.save(f)
        f.seek(0)
        self.env['ir.attachment'].create(
                {'res_model': 'nantian_erp.offer_information', 'res_id': self.id, 'datas_fname': u'南软入职信息表-数据中心服务部——'+self.name + u'.xls',
                 'name': self.name + u'offer信息', 'mimetype': 'application/vnd.ms-excel',
                 'datas': base64.encodestring(f.read()),})
        f.close()


    # offer审批对应的同意按钮
    @api.multi
    def agree(self):
        self.state=u'已审批'
        self.resume_id.state = u'发offer'
        self.resume_id.interviewer = None
        offer=self.search([('id','=',self.id)])
        recruitment_group = self.env['res.groups'].search([('name', '=', u'招聘组')],limit=1)
        self.env['nantian_erp.offer_examine'].create({'user_id':self.examiner_user.id,'result':u'同意','offer_id':self.id})
        offer_examine = self.env['nantian_erp.offer_examine'].search([('offer_id','=',self.id)],limit=1)
        self.offer_file()
        attachment_ids = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=','nantian_erp.offer_information')])
        resume_attachment_ids  = self.env['ir.attachment'].search([('res_id','=',self.resume_id.id),('res_model','=','nantian_erp.resume')])
        attach_ids = []
        for attachment_id in attachment_ids:
            attach_ids.append(attachment_id.id)
        for resume  in resume_attachment_ids:
            attach_ids.append(resume.id)
        self.offer_information_email(recruitment_group.users,attach_ids)
        self.examiner_user = None

    # 不同意按钮
    @api.multi
    def disagree(self):
        self.state = u'未通过'
        self.resume_id.states = u'淘汰'
        self.env['nantian_erp.offer_examine'].create({'user_id':self.examiner_user.id,'result':u'不同意','offer_id':self.id})
        self.examiner_user = None
        self.resume_id.interviewer = None

    # 通过建立创建员工
    def create_employee_from_resume(self, cr, uid, ids, context=None):
        """ Create an hr.employee from the nantian_erp.offer """
        if context is None:
            context = {}
        hr_employee = self.pool.get('hr.employee')
        nantian_entry = self.pool.get('nantian_erp.entry')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        emp_id = False
        for offer in self.browse(cr, uid, ids, context=context):
            if offer.recruitment_id:
                #对应招聘需求以招聘人数加1
                offer.recruitment_id.write({'hired_num': offer.recruitment_id.hired_num + 1})
                # 如果以招聘人数等于招聘人数，招聘需求归档
                if offer.recruitment_id.hired_num == offer.recruitment_id.need_people_num:
                    offer.recruitment_id.write({'state': 'archived'})
                # 建立状态改为已入职
                offer.resume_id.write({'state': u'已入职'})
                # 创建员工
                create_ctx = dict(context, mail_broadcast=False)
                emp_id = hr_employee.create(cr, uid, {'name': offer.resume_id.name,
                                                      'position_id': offer.recruitment_id.job_id.id or False,
                                                      'department_id': offer.second_department_id.id or False,
                                                      'education':offer.resume_id.education or False,
                                                      'level':offer.job_level or False,
                                                      'mobile_phone':offer.phone or False,
                                                      'gender':offer.resume_id.gender or False,
                                                      'working_team_id':offer.recruitment_id.working_team_id.id or False,
                                                      'identification_id':offer.identification_id or False,
                                                     }, context=create_ctx)
               # 创建入职记录
                entry_id = nantian_entry.create(cr,uid,{
                    'resume_id':offer.resume_id.id,
                    'user_id':uid,

                },context=create_ctx

                )
                # 修改offer的状态为未设置邮箱
                self.write(cr, uid, [offer.id], {'emp_id': emp_id,'entry_id':entry_id,'state':u'未设置邮箱'}, context=context)

            else:
                pass
        # 跳转至员工页面
        action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
        dict_act_window = act_window.read(cr, uid, [action_id], [])[0]
        if emp_id:
            dict_act_window['res_id'] = emp_id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

    # 发offer不入职
    @api.multi
    def create_entry(self):
        self.resume_id.states = u'未入职'
        self.state = u"未入职"
        self.env['nantian_erp.entry'].create({'resume_id': self.resume_id.id,'user_id':self.env.uid,'type':'发offer未入职'})

    # 创建用户
    @api.multi
    def create_user(self):
        if self.work_email:
            i = 1
            email = self.work_email
            # 防止系统中用户名相同
            while(1):
                if self.env['res.users'].search([('login','=',email)]):
                    email = email+str(i)
                    i=i+1
                else:
                    break
            if i==1:
                user = self.env['res.users'].sudo().create({'login':self.work_email,'password':'123456','name':self.resume_id.name,'email':self.work_email,'active':1})
            else:
                print email
                a = self.env['res.users'].sudo().search([('login','=',self.work_email)])
                print a.sudo().update({'login':email})
                user = self.env['res.users'].sudo().create({'login':self.work_email,'password':'123456','name':self.resume_id.name,'email':self.work_email,'active':1})
            self.emp_id.user_id = user
            self.state = u'完成'
            self.user = user
        else:
            raise exceptions.ValidationError('请填写公司邮箱')

# offer审批表
class offer_examine(models.Model):
    _name = 'nantian_erp.offer_examine'

    user_id = fields.Many2one('res.users')
    result = fields.Selection([(u'同意',u'同意'),(u'不同意',u'不同意')])
    time = fields.Date(default=fields.Date.today())
    offer_id = fields.Many2one('nantian_erp.offer_information')

# 入职记录表
class entry(models.Model):
    _name = 'nantian_erp.entry'
    _rec_name = 'resume_id'

    resume_id = fields.Many2one('nantian_erp.resume')
    date = fields.Date(default=fields.Date.today())
    reason = fields.Char(string='原因')
    user_id = fields.Many2one('res.users')
    type = fields.Char(string='类别')



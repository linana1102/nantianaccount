# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
import datetime

class employee_sign(models.Model):
    _name = 'nantianaccount.employee_sign'

    date = fields.Date(string='创建日期', default=lambda self: fields.datetime.now())
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="创建用户")
    employee_id = fields.Many2one('hr.employee', default=lambda self: self._get_employee_id(), string="员工")
    shangwu_project = fields.Many2one("nantian_erp.working_team", string="上午项目")
    xiawu_project = fields.Many2one("nantian_erp.working_team", string="下午项目")
    jiaban = fields.Boolean(string="是否加班")
    jiaban_end_time = fields.Datetime(string="加班结束时间")
    jiaban_working_team_id = fields.Many2one("nantian_erp.working_team", string="加班项目")
    exam_user = fields.Many2one('res.users', string="审批人")
    status = fields.Selection([(u'待审批', u'待审批'), (u'已审批', u'已审批'), (u'已退回' ,u'已退回'), (u'追回', u'追回')], default=u"待审批")
    contract_job_id = fields.Many2one('nantian_erp.jobs', string="合同岗位")
    shangwu_partner_id =fields.Many2one("res.partner", string="上午客户", domain="[('category','=',u'服务客户')]")
    xiawu_partner_id = fields.Many2one("res.partner", string="下午客户", domain="[('category','=',u'服务客户')]")
    jiaban_partner_id = fields.Many2one("res.partner", string="加班客户", domain="[('category','=',u'服务客户')]")
    # contract_id = fields.Many2one("nantian_erp.contract", string="合同")

    @api.model
    def _get_employee_id(self):
        if self.env.user.employee_ids:
            return self.env.user.employee_ids[0]
        return None

    @api.onchange('shangwu_project', 'shangwu_partner_id')
    def _onchange_price(self):
        # set auto-changing field
        self.xiawu_project = self.shangwu_project
        self.xiawu_partner_id = self.shangwu_partner_id
        if self.jiaban:
            self.jiaban_working_team_id = self.shangwu_project
            self.jiaban_partner_id = self.shangwu_partner_id
        # Can optionally return a warning and domains

    @api.multi
    @api.depends('from_time', 'len')
    def _count_to_time(self):
        for record in self:
            record.to_time = record.from_time

    @api.multi
    def action_to_examine(self):
        self.status = "待审批"
        # self.exam_user = self.working_team_id.user_id

    @api.multi
    def action_to_done(self):
        self.status = "已审批'"
        self.exam_user = None

    @api.multi
    def action_to_back(self):
        self.status = "退回"
        self.exam_user = self.user_id

    @api.multi
    def action_to_back(self):
        self.status = "追回"
        self.exam_user = self.user_id
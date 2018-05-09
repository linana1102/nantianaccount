# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
import datetime

class employee_sign(models.Model):
    _name = 'nantianaccount.employee_sign'

    date = fields.Date(string='创建日期', default=lambda self: fields.datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="创建用户")
    employee_id = fields.Many2one('hr.employee', default=lambda self: self._get_employee_id(), string="员工")
    from_time = fields.Datetime(string='开始时间')
    to_time = fields.Datetime(string='结束时间', compute='_count_to_time')
    len = fields.Float(string='时长' )
    working_team_id = fields.Many2one("nantian_erp.working_team", string="项目")

    @api.model
    def _get_employee_id(self):
        if self.env.user.employee_ids:
            return self.env.user.employee_ids[0]
        return None

    @api.multi
    @api.depends('from_time', 'len')
    def _count_to_time(self):
        for record in self:
            record.to_time = record.from_time

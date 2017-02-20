# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions

class pre_sale(models.Model):
    _name = 'nantian_erp.pre_sale'

    department_id = fields.Many2one('hr.department',string='部门')
    no = fields.Char(string='编号')
    partner = fields.Many2one('res.partner',string='客户',domain="[('category','=',u'服务客户')]")
    name = fields.Char(string='项目名称')
    amount_money = fields.Integer(string='金额')
    type = fields.Char(string='类型')
    state = fields.Char(string='阶段')
    competitors = fields.Char(string='竞争对手')
    pre_bid_date = fields.Date(string='预计投标日期')
    rate_of_success = fields.Integer(string='预计成功率（%）')
    process_scrib = fields.Text(string='本周主要进展说明')
    user_id = fields.Many2one('res.users',string='销售负责人')

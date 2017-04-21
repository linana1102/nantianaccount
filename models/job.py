# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions

class jobs(models.Model):
    _name = 'nantian_erp.job'

    name = fields.Char()
    categroy = fields.Selection([(u'系统',u'系统'),(u'网络',u'网络'),(u'开发',u'开发')])


class recruitment_requirements(models.Model):
    _name = 'nantian_erp.recruitment_requirements'

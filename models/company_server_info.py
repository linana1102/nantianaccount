# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions


class company_info_deplay(models.Model):
    _name = 'nantian_erp.company_info_deplay'

    kind = fields.Char(string=u"工作项")
    title = fields.Char(string=u"标题")
    text1_1_1 = fields.Char(string=u"责任人")
    text1_1_2 = fields.Char(string=u"频次")
    text1_1_3 = fields.Text(string=u"具体内容")
    text1_1_4 = fields.Text(string=u"注意事项")
    text1_binary = fields.One2many("nantian_erp.company_info_attachment","attachment_id",string=u"所需附件")

    text1_2_1 = fields.Char(string=u"责任人")
    text1_2_2 = fields.Char(string=u"频次")
    text1_2_3 = fields.Text(string=u"具体内容")
    text1_2_4 = fields.Text(string=u"注意事项")

    text1_3_1 = fields.Char(string=u"责任人")
    text1_3_2 = fields.Char(string=u"频次")
    text1_3_3 = fields.Text(string=u"具体内容")
    text1_3_4 = fields.Text(string=u"注意事项")

    text1_4_1 = fields.Char(string=u"责任人")
    text1_4_2 = fields.Char(string=u"频次")
    text1_4_3 = fields.Text(string=u"具体内容")
    text1_4_4 = fields.Text(string=u"注意事项")

    text1_5_1 = fields.Char(string=u"责任人")
    text1_5_2 = fields.Char(string=u"频次")
    text1_5_3 = fields.Text(string=u"具体内容")
    text1_5_4 = fields.Text(string=u"注意事项")

    text2_1_1 = fields.Char(string=u"责任人")
    text2_1_2 = fields.Char(string=u"频次")
    text2_1_3 = fields.Text(string=u"具体内容")
    text2_1_4 = fields.Text(string=u"注意事项")

    text2_2_1 = fields.Char(string=u"责任人")
    text2_2_2 = fields.Char(string=u"频次")
    text2_2_3 = fields.Text(string=u"具体内容")
    text2_2_4 = fields.Text(string=u"注意事项")

    text2_3_1 = fields.Char(string=u"责任人")
    text2_3_2 = fields.Char(string=u"频次")
    text2_3_3 = fields.Text(string=u"具体内容")
    text2_3_4 = fields.Text(string=u"注意事项")

    text3_1_1 = fields.Char(string=u"责任人")
    text3_1_2 = fields.Char(string=u"频次")
    text3_1_3 = fields.Text(string=u"具体内容")
    text3_1_4 = fields.Text(string=u"注意事项")

    text3_2_1 = fields.Char(string=u"责任人")
    text3_2_2 = fields.Char(string=u"频次")
    text3_2_3 = fields.Text(string=u"具体内容")
    text3_2_4 = fields.Text(string=u"注意事项")

    text3_3_1 = fields.Char(string=u"责任人")
    text3_3_2 = fields.Char(string=u"频次")
    text3_3_3 = fields.Text(string=u"具体内容")
    text3_3_4 = fields.Text(string=u"注意事项")

    text3_4_1 = fields.Char(string=u"责任人")
    text3_4_2 = fields.Char(string=u"频次")
    text3_4_3 = fields.Text(string=u"具体内容")
    text3_4_4 = fields.Text(string=u"注意事项")

    text3_5_1 = fields.Char(string=u"责任人")
    text3_5_2 = fields.Char(string=u"频次")
    text3_5_3 = fields.Text(string=u"具体内容")
    text3_5_4 = fields.Text(string=u"注意事项")

    text4_1_1 = fields.Char(string=u"责任人")
    text4_1_2 = fields.Char(string=u"频次")
    text4_1_3 = fields.Text(string=u"具体内容")
    text4_1_4 = fields.Text(string=u"注意事项")

    text4_2_1 = fields.Char(string=u"责任人")
    text4_2_2 = fields.Char(string=u"频次")
    text4_2_3 = fields.Text(string=u"具体内容")
    text4_2_4 = fields.Text(string=u"注意事项")


    text5_1_1 = fields.Char(string=u"责任人")
    text5_1_2 = fields.Char(string=u"频次")
    text5_1_3 = fields.Char(string=u"具体内容")
    text5_1_4 = fields.Char(string=u"注意事项")

    text5_2_1 = fields.Char(string=u"责任人")
    text5_2_2 = fields.Char(string=u"频次")
    text5_2_3 = fields.Char(string=u"具体内容")
    text5_2_4 = fields.Char(string=u"注意事项")

class company_info_kind(models.Model):
    _name = 'nantian_erp.company_info_kind'

    kind = fields.Char(string=u"类")
    title = fields.Char(string=u"标题")
    text_ids = fields.One2many("nantian_erp.company_info_context","kind_id",string=u"工作项")
    attachment_ids = fields.One2many("nantian_erp.company_info_attachment","kind_id",string=u"所需附件")


class company_info_context(models.Model):
    _name = 'nantian_erp.company_info_context'

    text1 = fields.Char(string=u"责任人")
    text2 = fields.Char(string=u"频次")
    text3 = fields.Text(string=u"具体内容")
    text4 = fields.Text(string=u"注意事项")
    kind_id = fields.Many2one("nantian_erp.company_info_kind")



class company_info_attachment(models.Model):
    _name = 'nantian_erp.company_info_attachment'

    title = fields.Char(string=u"附件名称")
    text_binary = fields.Binary(string=u"表格下载区")
    kind_id = fields.Many2one("nantian_erp.company_info_kind")
    attachment_id = fields.Many2one("nantian_erp.company_info_deplay")
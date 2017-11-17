# -*- coding: utf-8 -*-
from openerp import models, fields, api,exceptions



class company_info_deplay(models.Model):
    _name = 'nantian_erp.company_info_deplay'

    kind = fields.Char(string=u"工作项")
    title = fields.Char(string=u"标题")
    text1_1_1 = fields.Char(string=u"责任人")
    text1_1_2 = fields.Char(string=u"频次")
    text1_1_3 = fields.Text(string=u"具体内容")
    text1_1_4 = fields.Text(string=u"注意事项")

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
    attachment1_id = fields.One2many("nantian_erp.company_info_attachment","deplay1_id",string=u"表格")


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
    attachment2_id = fields.One2many("nantian_erp.company_info_attachment","deplay2_id",string=u"表格")


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
    attachment3_id = fields.One2many("nantian_erp.company_info_attachment","deplay3_id",string=u"表格")


    text4_1_1 = fields.Char(string=u"责任人")
    text4_1_2 = fields.Char(string=u"频次")
    text4_1_3 = fields.Text(string=u"具体内容")
    text4_1_4 = fields.Text(string=u"注意事项")

    text4_2_1 = fields.Char(string=u"责任人")
    text4_2_2 = fields.Char(string=u"频次")
    text4_2_3 = fields.Text(string=u"具体内容")
    text4_2_4 = fields.Text(string=u"注意事项")
    attachment4_id = fields.One2many("nantian_erp.company_info_attachment","deplay4_id",string=u"表格")


    text5_1_1 = fields.Char(string=u"责任人")
    text5_1_2 = fields.Char(string=u"频次")
    text5_1_3 = fields.Char(string=u"具体内容")
    text5_1_4 = fields.Char(string=u"注意事项")

    text5_2_1 = fields.Char(string=u"责任人")
    text5_2_2 = fields.Char(string=u"频次")
    text5_2_3 = fields.Char(string=u"具体内容")
    text5_2_4 = fields.Char(string=u"注意事项")
    attachment5_id = fields.One2many("nantian_erp.company_info_attachment","deplay5_id",string=u"表格")
    attachment6_id = fields.One2many("nantian_erp.company_info_attachment", "deplay6_id", string=u"表格")
    attachment7_id = fields.One2many("nantian_erp.company_info_attachment", "deplay7_id", string=u"表格")
    attachment8_id = fields.One2many("nantian_erp.company_info_attachment", "deplay7_id", string=u"表格")

    address_list_ids = fields.One2many("nantian_erp.company_info_address_list", "deplay_id", string=u"行政人员通讯录")


class company_info_address_list(models.Model):
    _name = 'nantian_erp.company_info_address_list'

    text1 = fields.Char(string=u"姓名")
    text2 = fields.Char(string=u"移动电话")
    text3 = fields.Char(string=u"座机电话")
    deplay_id = fields.Many2one("nantian_erp.company_info_deplay")


class company_info_kind(models.Model):
    _name = 'nantian_erp.company_info_kind'

    kind = fields.Char(string=u"类")
    title = fields.Char(string=u"工作项")
    text1 = fields.Char(string=u"责任人")
    text2 = fields.Char(string=u"频次")
    text3 = fields.Text(string=u"具体内容")
    text4 = fields.Text(string=u"注意事项")
    text_ids = fields.One2many("nantian_erp.company_info_context","kind_id",string=u"工作项")
    attachment_ids = fields.One2many("nantian_erp.company_info_attachment","kind_id",string=u"所需表格")


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
    text_binary_preview = fields.Binary(string=u"表格填写示范")
    deplay1_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay2_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay3_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay4_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay5_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay6_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay7_id = fields.Many2one("nantian_erp.company_info_deplay")
    deplay8_id = fields.Many2one("nantian_erp.company_info_deplay")
    kind_id = fields.Many2one("nantian_erp.company_info_kind")



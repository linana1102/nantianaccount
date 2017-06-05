# -*- coding: utf-8 -*-
from models import models
from openerp import http

from openerp.http import request
import base64
from docxtpl import DocxTemplate,InlineImage
from docx.shared import Mm, Inches, Pt
import openerp

from cStringIO import StringIO
from openerp.http import request
from openerp.tools import ustr
import urllib2
import json
import base64
import zipfile,os
import sys

def content_disposition(filename):
    filename = ustr(filename)
    escaped = urllib2.quote(filename.encode('utf8'))
    browser = request.httprequest.user_agent.browser
    version = int((request.httprequest.user_agent.version or '0').split('.')[0])
    if browser == 'msie' and version < 9:
        return "attachment; filename=%s" % escaped
    elif browser == 'safari' and version < 537:
        return u"attachment; filename=%s" % filename.encode('ascii', 'replace')
    else:
        return "attachment; filename*=UTF-8''%s" % escaped


# class exchange_data(http.Controller):
#     @http.route('/get_ip/', type='http', auth='public', methods=['POST'])
#     def get_ip(self, **post):
#         if post['pwd'] == '123':
#             ip = http.request.httprequest.remote_addr
#
#         boos_ip = http.request.env['server_desk.case'].search([('special', '=', 'boss')],limit=1)
#         boos_ip.ip = ip
#         return "ok"

class Binary(http.Controller):
    @http.route('/web/binary/html_page', type='http', auth="public")
    #@serialize_exception
    def html_page(self, model, field, id=None, filename_field=None, **kw):
        """ Download link for files stored as binary fields.

        If the ``id`` parameter is omitted, fetches the default value for the
        binary field (via ``default_get``), otherwise fetches the field for
        that precise record.

        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename_field: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.registry[model]
        cr, uid, context = request.cr, request.uid, request.context
        fields = [field]
        if filename_field:
            fields.append(filename_field)
        if id:
            res = Model.read(cr, uid, [int(id)], fields, context)[0]
        else:
            res = Model.default_get(cr, uid, fields, context)
        filecontent = base64.b64decode(res.get(field) or '')
        if not filecontent:
            return request.not_found()
        else:
            filename = '%s_%s' % (model.replace('.', '_'), id)
            if filename_field:
                filename = res.get(filename_field, '') or filename
            return request.make_response(filecontent,
                [('Content-Type', 'text/html')])

    @http.route('/nantian_erp/export_resume', type='http', auth="public")
    def export_resume(self,ids):
        # 定义压缩文件流
        zip_stream = StringIO()
        resume_zip = zipfile.ZipFile(zip_stream,'w')

        # 将参数转为列表
        id_list = json.loads(ids)

        # 获取要到处简历的员工
        Model = request.session.model('hr.employee')
        employees = Model.search_read([('id','in',id_list)])


        job=''

        for i,employee in enumerate(employees):

            # 获取模板
            path = os.path.abspath(os.path.dirname(sys.argv[0]))
            tpl = DocxTemplate(path.replace('\\','/')+'/myaddons/nantian_erp/resume_template.docx')
            # 简历写入的文件流
            fp = StringIO()
            experiences_list = []
            certifications_dict=[]
            if employee['job_id']:
                job = employee['job_id'][1]
            if employee['work_experience_ids']:
                Model = request.session.model('nantian_erp.work_experience')
                experiences = Model.search_read([('id','in',employee['work_experience_ids'])])
                for exper in experiences:
                    exper_dict = {'date':exper['date'] or '','name':exper['name'] or '','job':exper['job'] or '','description':exper['description'] or ''}
                    experiences_list.append(exper_dict)

            if employee['certificate_ids']:
                Model = request.session.model('nantian_erp.certificate')
                certificates = Model.search_read([('id','in',employee['certificate_ids'])])
                for cer in certificates:
                    image = ''
                    if cer['image']:
                        # 将base64 转为图片
                        f = StringIO(base64.b64decode(str(cer['image'])))
                        image = InlineImage(tpl,f,height=Mm(30))
                        f.close()
                    certificate = {'name':cer['name'] or '','image': image or '',}

                    certifications_dict.append(certificate)
            gender = ''
            if employee['gender'] == 'male':
                gender = u'男'
            elif employee['gender'] == 'female':
                gender = u'女'
            # 模板所需数据
            resume_dict = {'name':employee['name'] or '',
                           'gender':gender or '',
                           'birthday':employee['birthday']or '',
                           'education':employee['education']or '',
                           'graduction':employee['graduation']or '',
                           'major':employee['major']or '',
                           'job':job or '',
                           'work_time':employee['work_time']or '',
                           'specialty':employee['specialty']or '',
                           'work_experiences':experiences_list or '',
                           'certifications':certifications_dict or '',

                           }
            tpl.render(resume_dict)
            tpl.save(fp)
            fp.seek(0)
            resume_zip.writestr(employee['name']+u'简历'+'.docx',fp.getvalue())
            fp.close()
        resume_zip.close()
        zip_stream.seek(0)
        # 返回压缩文件
        return request.make_response(zip_stream.getvalue() ,
            headers=[('Content-Disposition',
                            content_disposition(u'简历'+'.zip')),
                     ('Content-Type', 'application/zip')],
            )


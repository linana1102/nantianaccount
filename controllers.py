# -*- coding: utf-8 -*-
from models import models
from openerp import http

from openerp.http import request
import base64
from docxtpl import DocxTemplate
from cStringIO import StringIO
from openerp.http import request
from openerp.tools import ustr
import urllib2
import json


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
        #print ids
        tpl = DocxTemplate(r'myaddons/nantian_erp/resume_template.docx')
        id_list = json.loads(ids)
        Model = request.session.model('hr.employee')
        employees = Model.search_read([('id','in',id_list)])
        print employees
        for employee in employees:
            fp = StringIO()
            experiences = []
            certifications=[]
            for i in employee.work_experience_ids:
                exper = {'date':i.date,'name':i.name,'job':i.job,'description':i.description}
                experiences.append(exper)
                certificate = {'name':employee.name}
                # certifications.append(certificate)
            resume_dict = {'name':employee.name,
                           'gender':employee.name,
                           'birthday':employee.birthday,
                           'education':employee.education,
                           'graduction':employee.graduation,
                           'major':employee.major,
                           'job':employee.job,
                           'work_time':employee.work_time,
                           'specialty':employee.work_time,
                           'work_experiences':experiences,
                           # 'certifications':certifications

                           }
            tpl.render(resume_dict)
            tpl.save(fp)
            fp.seek(0)
            data = fp.read()
            fp.close()
            # print data
            request.make_response(data,
            headers=[('Content-Disposition',
                            content_disposition('employee.name'+u'简历'+'.docx')),
                     ('Content-Type', 'application/vnd.ms-word')],
            )

            #  response = HttpResponse(wrapper, content_type='application/zip')
            # response['Content-Disposition'] = 'attachment; filename=your_zipfile.zip'
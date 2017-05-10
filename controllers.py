# -*- coding: utf-8 -*-
from models import models
from openerp import http
from openerp.http import request
import base64
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
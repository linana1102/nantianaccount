# -*- coding: utf-8 -*-
from models import models
from openerp import http



# class exchange_data(http.Controller):
#     @http.route('/get_ip/', type='http', auth='public', methods=['POST'])
#     def get_ip(self, **post):
#         if post['pwd'] == '123':
#             ip = http.request.httprequest.remote_addr
#
#         boos_ip = http.request.env['server_desk.case'].search([('special', '=', 'boss')],limit=1)
#         boos_ip.ip = ip
#         return "ok"



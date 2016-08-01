# -*- coding: utf-8 -*-
from models import models
from openerp import http

"""
class ServerDesk(http.Controller):
    @http.route('/server_desk/', auth='public')
    def index(self, **kw):
        model = http.request.env['server_desk.case']
        recs = model.search([])
        return recs 

    @http.route('/server_desk/server_desk/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('server_desk.listing', {
            'root': '/server_desk/server_desk',
            'objects': http.request.env['server_desk.case'].search([]),
        })

    @http.route('/server_desk/server_desk/objects/<model("server_desk.case"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('server_desk.object', {
            'object': obj
        })
"""

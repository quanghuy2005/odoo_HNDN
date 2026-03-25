# -*- coding: utf-8 -*-
from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            # Chỉ tạo Employee nếu User này thuộc nhóm nội bộ và chưa có Employee
            if user.has_group('base.group_user'):
                employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
                if not employee and user.name:
                    self.env['hr.employee'].create({
                        'name': user.name,
                        'user_id': user.id,
                        'work_email': user.login,
                    })
        return users

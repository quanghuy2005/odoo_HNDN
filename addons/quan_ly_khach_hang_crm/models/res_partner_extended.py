# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner_TestMarker(models.Model):
    """Đánh dấu khách test"""
    _inherit = 'res.partner'

    is_test_customer = fields.Boolean(
        string='🧪 Là Khách Test',
        default=False,
        help='Khách hàng dùng để test - có thể ẩn khỏi danh sách thông thường'
    )

    is_internal = fields.Boolean(
        string='Nội Bộ',
        default=False,
        help='Công ty nội bộ hoặc nhân viên'
    )

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100, name_get_uid=None):
        """Override để ẩn khách test trong search"""
        if args is None:
            args = []
        
        # Nếu chưa check "Hiển thị khách test", thì filter bỏ
        # (Có thể thêm context để điều khiển)
        if not self.env.context.get('show_test_customers', False):
            args += [('is_test_customer', '=', False)]
        
        return super()._name_search(name, args, operator, limit, name_get_uid)

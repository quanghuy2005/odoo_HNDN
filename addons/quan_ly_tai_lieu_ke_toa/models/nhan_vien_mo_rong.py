# -*- coding: utf-8 -*-
from odoo import models, fields


class NhanVienMoRongTaiLieu(models.Model):
    """Mở rộng nhân viên cho module tài liệu"""
    _inherit = 'hr.employee'

    # One2many: Danh sách tài liệu nhân viên phụ trách
    danh_sach_tai_lieu = fields.One2many(
        'tai_lieu.ke_toa',
        'nhan_vien_phu_trach',
        string='Danh Sách Tài Liệu Phụ Trách',
        readonly=True
    )

    # Computed field
    so_tai_lieu = fields.Integer(
        string='Số Tài Liệu',
        compute='_tinh_so_tai_lieu',
        store=True
    )

    def _tinh_so_tai_lieu(self):
        """Tính số lượng tài liệu"""
        for nv in self:
            nv.so_tai_lieu = len(nv.danh_sach_tai_lieu)

# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVienMoRong(models.Model):
    """Mở rộng model Nhân Viên (hr.employee) để quản lý khách hàng"""
    _inherit = 'hr.employee'

    # Many2Many: Một nhân viên có thể phụ trách nhiều khách hàng
    danh_sach_khach_hang = fields.Many2many(
        'res.partner',
        'nhan_vien_khach_hang_rel',
        'nhan_vien_id',
        'khach_hang_id',
        string='Danh Sách Khách Hàng Phụ Trách',
        domain=[('is_company', '=', False)]
    )

    # Computed field: số lượng khách hàng
    so_luong_khach_hang = fields.Integer(
        string='Số Lượng Khách Hàng',
        compute='_tinh_so_luong_khach_hang',
        store=True
    )

    @api.depends('danh_sach_khach_hang')
    def _tinh_so_luong_khach_hang(self):
        """Tính số lượng khách hàng mà nhân viên phụ trách"""
        for nv in self:
            nv.so_luong_khach_hang = len(nv.danh_sach_khach_hang)

    def hanh_dong_xem_khach_hang(self):
        """Action để xem danh sách khách hàng của nhân viên"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Khách Hàng',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.danh_sach_khach_hang.ids)],
        }

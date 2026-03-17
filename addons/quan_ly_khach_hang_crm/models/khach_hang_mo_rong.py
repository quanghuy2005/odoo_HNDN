# -*- coding: utf-8 -*-
from odoo import models, fields, api


class KhachHangMoRong(models.Model):
    """Mở rộng model Khách Hàng (res.partner) với các trường thêm"""
    _inherit = 'res.partner'

    # Trạng thái khách hàng trong CRM
    trang_thai_khach_hang = fields.Selection([
        ('tiem_nang', 'Tiềm Năng'),
        ('dang_giao_dich', 'Đang Giao Dịch'),
        ('da_ky_hop_dong', 'Đã Ký Hợp Đồng'),
        ('dang_phuc_vu', 'Đang Phục Vụ'),
        ('ngung_hop_tac', 'Ngừng Hợp Tác'),
    ], string='Trạng Thái Khách Hàng', default='tiem_nang')

    # Thông tin thêm
    tieu_su_giao_dich = fields.Text(
        string='Lịch Sự Giao Dịch',
        help='Ghi chú về những giao dịch trước đó'
    )
    
    ghi_chu_kinh_doanh = fields.Text(
        string='Ghi Chú Kinh Doanh',
        help='Những lưu ý, yêu cầu đặc biệt từ khách hàng'
    )

    # Liên hệ
    nguoi_dai_dien = fields.Char(
        string='Người Đại Diện',
        help='Tên người phụ trách/liên hệ tại công ty khách'
    )
    
    chuc_vu_dai_dien = fields.Char(
        string='Chức Vụ Người Đại Diện',
        help='Chức vụ của người đại diện'
    )

    # Thống kê
    so_tien_da_ky = fields.Float(
        string='Tổng Giá Trị Hợp Đồng (VND)',
        compute='_tinh_tong_gia_tri',
        help='Tổng giá trị tất cả hợp đồng đã ký'
    )

    so_luong_tai_lieu = fields.Integer(
        string='Số Hợp Đồng',
        compute='_tinh_so_luong_tai_lieu'
    )
    
    so_luong_van_ban = fields.Integer(
        string='Hồ Sơ Văn Bản',
        compute='_tinh_so_luong_van_ban'
    )

    def _tinh_tong_gia_tri(self):
        for khach in self:
            tong_tien = 0.0
            if 'tai_lieu.ke_toa' in self.env:
                tai_lieus = self.env['tai_lieu.ke_toa'].search([
                    ('khach_hang', '=', khach.id),
                    ('trang_thai', 'in', ['da_ky', 'hoan_tat'])
                ])
                tong_tien = sum(tai_lieus.mapped('gia_tri_tai_lieu'))
            khach.so_tien_da_ky = tong_tien
            
    def _tinh_so_luong_tai_lieu(self):
        for khach in self:
            if 'tai_lieu.ke_toa' in self.env:
                khach.so_luong_tai_lieu = self.env['tai_lieu.ke_toa'].search_count([('khach_hang', '=', khach.id)])
            else:
                khach.so_luong_tai_lieu = 0
            
    def action_xem_tai_lieu(self):
        """Hành động mở danh sách tài liệu khi bấm vào nút thông minh"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp Đồng Kế Toán',
            'res_model': 'tai_lieu.ke_toa',
            'view_mode': 'tree,form',
            'domain': [('khach_hang', '=', self.id)],
            'context': {'default_khach_hang': self.id},
        }

    def _tinh_so_luong_van_ban(self):
        for khach in self:
            if 'ho_so_van_ban' in self.env:
                khach.so_luong_van_ban = self.env['ho_so_van_ban'].search_count([('khach_hang_id', '=', khach.id)])
            else:
                khach.so_luong_van_ban = 0
                
    def action_xem_van_ban(self):
        """Hành động mở kho văn bản hành chính khi bấm vào nút thông minh"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hồ Sơ Hành Chính',
            'res_model': 'ho_so_van_ban',
            'view_mode': 'tree,form',
            'domain': [('khach_hang_id', '=', self.id)],
            'context': {'default_khach_hang_id': self.id},
        }

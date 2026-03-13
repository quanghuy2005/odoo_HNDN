# -*- coding: utf-8 -*-
from odoo import models, fields


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
        string='Lịch Sử Giao Dịch',
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
        store=True,
        help='Tổng giá trị tất cả hợp đồng đã ký'
    )

    def _tinh_tong_gia_tri(self):
        """Tính tổng giá trị các hợp đồng (nếu module tài liệu được cài)"""
        for khach in self:
            khach.so_tien_da_ky = 0.0
            # Sẽ được tính toán khi module tài liệu được cài

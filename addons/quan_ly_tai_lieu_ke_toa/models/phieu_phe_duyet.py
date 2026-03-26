# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError

class PhieuPheDuyet(models.Model):
    """Model lưu trữ phiếu phê duyệt"""
    _name = 'phieu.phe_duyet'
    _inherit = ['mail.thread']
    _description = 'Phiếu Phê Duyệt'
    _rec_name = 'tai_lieu'

    # Liên kết
    tai_lieu = fields.Many2one(
        'tai_lieu.ke_toa',
        string='Tài Liệu',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # Người phê duyệt
    nguoi_phe_duyet = fields.Many2one(
        'res.users',
        string='Người Phê Duyệt',
        default=lambda self: self.env.user,
        tracking=True
    )

    # Trạng thái
    trang_thai_phieu = fields.Selection([
        ('pending', 'Chờ Phê Duyệt'),
        ('approved', 'Đã Phê Duyệt'),
        ('rejected', 'Từ Chối'),
        ('skipped', 'Bỏ Qua'),
    ], string='Trạng Thái', default='pending', tracking=True)

    # Ý kiến
    y_kien = fields.Text(
        string='Ý Kiến / Ghi Chú',
        tracking=True
    )

    # Thời gian
    ngay_tao = fields.Datetime(
        string='Ngày Tạo',
        default=fields.Datetime.now,
        readonly=True,
        tracking=True
    )

    ngay_phe_duyet = fields.Datetime(
        string='Ngày Phê Duyệt',
        tracking=True
    )

    # Methods
    def hanh_dong_phe_duyet(self):
        """Phê duyệt"""
        # Kiểm tra trước khi duyệt bằng phiếu
        if not self.env.user.has_group('quan_ly_tai_lieu_ke_toa.group_quan_ly_tai_lieu_admin') and not self.env.user.has_group('base.group_system'):
            raise UserError('Chỉ có Admin (Ban Giám Đốc) mới có quyền Phê duyệt!')

        self.write({
            'trang_thai_phieu': 'approved',
            'ngay_phe_duyet': fields.Datetime.now(),
            'nguoi_phe_duyet': self.env.user.id,
        })
        self.tai_lieu.hanh_dong_phe_duyet()

    def hanh_dong_tu_choi(self):
        """Từ chối phê duyệt"""
        if not self.env.user.has_group('quan_ly_tai_lieu_ke_toa.group_quan_ly_tai_lieu_admin') and not self.env.user.has_group('base.group_system'):
            raise UserError('Chỉ có Admin (Ban Giám Đốc) mới có quyền Từ chối phê duyệt!')

        self.write({
            'trang_thai_phieu': 'rejected',
            'ngay_phe_duyet': fields.Datetime.now(),
            'nguoi_phe_duyet': self.env.user.id,
        })

    def hanh_dong_bo_qua(self):
        """Bỏ qua phê duyệt"""
        self.write({
            'trang_thai_phieu': 'skipped',
            'ngay_phe_duyet': fields.Datetime.now(),
        })

# -*- coding: utf-8 -*-
from odoo import models, fields, api

class VersionComment(models.Model):
    """Model bình luận trên phiên bản tài liệu"""
    _name = 'version.comment'
    _description = 'Bình luận Phiên bản'
    _order = 'ngay_tao desc'

    version_id = fields.Many2one(
        'document.version',
        string='Phiên bản',
        required=True,
        ondelete='cascade'
    )

    nguoi_binh_luan = fields.Many2one(
        'res.users',
        string='Người bình luận',
        readonly=True,
        default=lambda self: self.env.user
    )

    noi_dung = fields.Text(
        string='Nội dung bình luận',
        required=True
    )

    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now,
        readonly=True
    )

    loai_binh_luan = fields.Selection([
        ('nhan_xet', 'Nhận xét'),
        ('de_xuat', 'Đề xuất'),
        ('yeu_cau_sua', 'Yêu cầu sửa'),
        ('phe_chuan', 'Phê chuẩn'),
    ], string='Loại bình luận', default='nhan_xet')

    co_ap_dung = fields.Boolean(
        string='Đã áp dụng',
        default=False,
        help='Những yêu cầu sửa này đã được áp dụng chưa?'
    )

    def toggle_ap_dung(self):
        """Toggle trạng thái áp dụng"""
        self.co_ap_dung = not self.co_ap_dung

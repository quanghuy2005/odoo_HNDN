# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class DocumentVersion(models.Model):
    """Model lưu trữ các phiên bản của tài liệu"""
    _name = 'document.version'
    _description = 'Phiên bản Tài liệu'
    _order = 'so_phien_ban desc'

    # Thông tin phiên bản
    so_phien_ban = fields.Integer(
        string='Số phiên bản',
        required=True,
        readonly=True,
        help='1.0, 1.1, 2.0...'
    )

    ten_phien_ban = fields.Char(
        string='Tên phiên bản',
        help='Ví dụ: Draft, First Review, Final'
    )

    mo_ta = fields.Text(
        string='Mô tả thay đổi',
        help='Những gì đã thay đổi so với phiên bản trước'
    )

    # Thông tin file
    file_data = fields.Binary(
        string='Nội dung file',
        required=True,
        readonly=True
    )

    file_name = fields.Char(
        string='Tên file',
        required=True,
        readonly=True
    )

    file_size = fields.Float(
        string='Kích thước file (KB)',
        readonly=True
    )

    file_type = fields.Char(
        string='Loại file',
        readonly=True,
        help='pdf, docx, xlsx...'
    )

    # Thông tin quản lý
    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now,
        readonly=True
    )

    nguoi_tao = fields.Many2one(
        'res.users',
        string='Người tạo phiên bản',
        readonly=True,
        default=lambda self: self.env.user
    )

    nhip_dap = fields.Selection([
        ('du_thao', 'Dự thảo'),
        ('xem_xet', 'Xem xét'),
        ('phe_duyet', 'Phê duyệt'),
        ('chinh_thuc', 'Chính thức'),
    ], string='Nhịp đập', default='du_thao')

    la_phien_ban_hien_tai = fields.Boolean(
        string='Là phiên bản hiện tại?',
        default=False,
        readonly=True
    )

    # Liên kết với document (generic)
    document_model = fields.Char(
        string='Model tài liệu',
        required=True,
        readonly=True,
        help='Tên model (tai_lieu.ke_toa, van_ban_den, v.v)'
    )

    document_id = fields.Integer(
        string='ID tài liệu',
        required=True,
        readonly=True
    )

    document_name = fields.Char(
        string='Tên tài liệu',
        readonly=True
    )

    # Thống kê
    so_lan_tai = fields.Integer(
        string='Số lần tải',
        default=0,
        readonly=True
    )

    so_nhan_xet = fields.Integer(
        string='Số lần được nhận xét',
        default=0,
        readonly=True,
        compute='_compute_so_nhan_xet'
    )

    @api.depends('comment_ids')
    def _compute_so_nhan_xet(self):
        for record in self:
            record.so_nhan_xet = len(record.comment_ids)

    # Comments/Feedback
    comment_ids = fields.One2many(
        'version.comment',
        'version_id',
        string='Bình luận'
    )

    @api.model
    def create_new_version(self, document_model, document_id, file_data, 
                          file_name, mo_ta='', so_phien_ban=None):
        """
        Hàm helper tạo phiên bản mới
        """
        try:
            import os
            
            # Lấy thông tin file
            file_size = len(file_data) / 1024 if file_data else 0
            file_type = os.path.splitext(file_name)[1].lower() if file_name else ''
            
            # Lấy tên tài liệu
            document = self.env[document_model].browse(document_id)
            document_name = document.name if hasattr(document, 'name') else f'{document_model}#{document_id}'
            
            # Nếu không cấp số phiên bản, tự tính từ phiên bản cuối
            if so_phien_ban is None:
                last_version = self.search([
                    ('document_model', '=', document_model),
                    ('document_id', '=', document_id)
                ], limit=1, order='so_phien_ban desc')
                so_phien_ban = (last_version.so_phien_ban + 1) if last_version else 1
            
            # Tắt phiên bản cũ là phiên bản hiện tại
            old_versions = self.search([
                ('document_model', '=', document_model),
                ('document_id', '=', document_id),
                ('la_phien_ban_hien_tai', '=', True)
            ])
            old_versions.write({'la_phien_ban_hien_tai': False})
            
            # Tạo phiên bản mới
            new_version = self.create({
                'so_phien_ban': so_phien_ban,
                'file_data': file_data,
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'mo_ta': mo_ta,
                'document_model': document_model,
                'document_id': document_id,
                'document_name': document_name,
                'la_phien_ban_hien_tai': True,
            })
            
            return new_version
        except Exception as e:
            _logger.error(f'Lỗi tạo phiên bản mới: {str(e)}')
            return False

    def download_version(self):
        """Tải xuống phiên bản này"""
        self.so_lan_tai += 1
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file_data/{self.file_name}',
            'target': 'new',
        }

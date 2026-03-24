# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AuditTrail(models.Model):
    """Model lưu trữ log những thay đổi trên tài liệu"""
    _name = 'audit.trail'
    _description = 'Audit Trail - Ghi chép hoạt động'
    _order = 'thoigian_thay_doi desc'

    # Thông tin chính
    thoigian_thay_doi = fields.Datetime(
        string='Thời gian thay đổi',
        default=fields.Datetime.now,
        readonly=True
    )

    nguoi_thay_doi = fields.Many2one(
        'res.users',
        string='Người thực hiện',
        readonly=True,
        default=lambda self: self.env.user
    )

    loai_hanh_dong = fields.Selection([
        ('create', 'Tạo mới'),
        ('write', 'Chỉnh sửa'),
        ('approve', 'Duyệt'),
        ('reject', 'Từ chối'),
        ('sign', 'Ký số'),
        ('submit', 'Gửi duyệt'),
        ('archive', 'Lưu trữ'),
        ('delete', 'Xóa'),
        ('share', 'Chia sẻ'),
        ('download', 'Tải xuống'),
    ], string='Loại hành động', required=True, readonly=True)

    chi_tiet = fields.Text(
        string='Chi tiết thay đổi',
        help='Mô tả chi tiết những gì đã thay đổi',
        readonly=True
    )

    dia_chi_ip = fields.Char(
        string='Địa chỉ IP',
        readonly=True,
        help='IP của thiết bị thực hiện hành động'
    )

    trang_thai_truoc = fields.Text(
        string='Trạng thái trước',
        readonly=True,
        help='Dữ liệu trước cập nhật'
    )

    trang_thai_sau = fields.Text(
        string='Trạng thái sau',
        readonly=True,
        help='Dữ liệu sau cập nhật'
    )

    ghi_chu = fields.Text(
        string='Ghi chú',
        help='Ghi chú thêm từ người dùng'
    )

    # Liên kết với document (generic - có thể dùng cho nhiều model)
    document_model = fields.Char(
        string='Model tài liệu',
        readonly=True,
        help='Tên model của tài liệu (e.g., tai_lieu.ke_toa, van_ban_den)'
    )

    document_id = fields.Integer(
        string='ID tài liệu',
        readonly=True,
        help='ID của tài liệu được thay đổi'
    )

    document_name = fields.Char(
        string='Tên tài liệu',
        readonly=True,
        help='Tên/Số hiệu tài liệu'
    )

    @api.model
    def create_audit_log(self, document_model, document_id, loai_hanh_dong, 
                        chi_tiet='', trang_thai_truoc='', trang_thai_sau='', 
                        ghi_chu='', dia_chi_ip=''):
        """
        Hàm helper để tạo audit log
        """
        try:
            document = self.env[document_model].browse(document_id)
            document_name = document.name if hasattr(document, 'name') else f'{document_model}#{document_id}'
            
            return self.create({
                'loai_hanh_dong': loai_hanh_dong,
                'chi_tiet': chi_tiet,
                'trang_thai_truoc': trang_thai_truoc,
                'trang_thai_sau': trang_thai_sau,
                'ghi_chu': ghi_chu,
                'dia_chi_ip': dia_chi_ip or self._get_client_ip(),
                'document_model': document_model,
                'document_id': document_id,
                'document_name': document_name,
            })
        except Exception as e:
            _logger.error(f'Lỗi tạo audit log: {str(e)}')
            return False

    def _get_client_ip(self):
        """Lấy IP của client"""
        try:
            import socket
            from odoo.http import request
            if hasattr(request, 'httprequest'):
                return request.httprequest.remote_addr
            return '0.0.0.0'
        except:
            return '0.0.0.0'

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class DocumentRetention(models.Model):
    """Model quản lý quy tắc lưu trữ tài liệu"""
    _name = 'document.retention'
    _description = 'Quy tắc Lưu trữ Tài liệu'

    # Thông tin quy tắc
    ten_quy_tac = fields.Char(
        string='Tên quy tắc',
        required=True
    )

    mo_ta = fields.Text(
        string='Mô tả'
    )

    # Áp dụng cho
    doc_type = fields.Selection([
        ('tai_lieu', 'Tài liệu Kế toán'),
        ('van_ban', 'Văn bản chính thức'),
        ('hop_dong', 'Hợp đồng'),
        ('hoa_don', 'Hóa đơn'),
        ('giay_phep', 'Giấy phép'),
        ('bao_cao', 'Báo cáo'),
        ('khac', 'Khác'),
    ], string='Loại tài liệu', required=True)

    # Thời gian lưu trữ
    thoi_gian_luu_tru = fields.Integer(
        string='Thời gian lưu trữ (năm)',
        required=True,
        default=5,
        help='Số năm phải lưu trữ'
    )

    co_che_luu_tru = fields.Selection([
        ('luv_chay', 'Lưu chạy'),
        ('luu_tap_trung', 'Lưu tập trung'),
        ('luu_dai_han', 'Lưu dài hạn'),
        ('luu_tren_cloud', 'Lưu trên Cloud'),
    ], string='Cơ chế lưu trữ', required=True, default='luv_chay')

    chi_so_uu_tien = fields.Integer(
        string='Chỉ số ưu tiên',
        default=10,
        help='Mức độ ưu tiên (0-100, số lớn = ưu tiên cao)'
    )

    # Quy tắc xóa
    co_the_xoa = fields.Boolean(
        string='Có thể xóa sau thời hạn?',
        default=True
    )

    tu_dong_xoa = fields.Boolean(
        string='Tự động xóa?',
        default=False,
        help='Tự động xóa sau thời hạn lưu trữ'
    )

    # Trạng thái
    hoat_dong = fields.Boolean(
        string='Hoạt động?',
        default=True,
        tracking=True
    )

    # Audit
    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now,
        readonly=True
    )

    nguoi_tao = fields.Many2one(
        'res.users',
        string='Người tạo',
        readonly=True,
        default=lambda self: self.env.user
    )

class DocumentRetentionLog(models.Model):
    """Model ghi chép lịch sử lưu trữ tài liệu"""
    _name = 'document.retention.log'
    _description = 'Lịch sử Lưu trữ'
    _order = 'ngay_tao desc'

    # Thông tin document
    document_model = fields.Char(
        string='Model tài liệu',
        required=True,
        readonly=True
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

    # Quy tắc áp dụng
    retention_rule_id = fields.Many2one(
        'document.retention',
        string='Quy tắc áp dụng',
        readonly=True
    )

    # Thời gian
    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        default=fields.Datetime.now,
        readonly=True
    )

    ngay_het_han_luu_tru = fields.Date(
        string='Ngày hết hạn lưu trữ',
        compute='_compute_ngay_het_han',
        store=True
    )

    so_ngay_con_lai = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_so_ngay_con_lai'
    )

    # Trạng thái
    trang_thai = fields.Selection([
        ('dang_luu_tru', 'Đang lưu trữ'),
        ('het_han', 'Hết hạn lưu trữ'),
        ('da_xoa', 'Đã xóa'),
        ('huy_bo', 'Hủy bỏ'),
    ], string='Trạng thái', default='dang_luu_tru', readonly=True)

    # Ghi chú
    ghi_chu = fields.Text(
        string='Ghi chú'
    )

    @api.depends('ngay_tao', 'retention_rule_id')
    def _compute_ngay_het_han(self):
        for record in self:
            if record.ngay_tao and record.retention_rule_id:
                ngay_tao_db = fields.Datetime.from_string(record.ngay_tao)
                ngay_het_han = ngay_tao_db + timedelta(days=365 * record.retention_rule_id.thoi_gian_luu_tru)
                record.ngay_het_han_luu_tru = ngay_het_han.date()
            else:
                record.ngay_het_han_luu_tru = None

    @api.depends('ngay_het_han_luu_tru')
    def _compute_so_ngay_con_lai(self):
        today = fields.Date.today()
        for record in self:
            if record.ngay_het_han_luu_tru:
                record.so_ngay_con_lai = (record.ngay_het_han_luu_tru - today).days
            else:
                record.so_ngay_con_lai = 0

    @api.model
    def create_retention_log(self, document_model, document_id, retention_rule_id):
        """
        Hàm helper tạo retention log
        """
        try:
            document = self.env[document_model].browse(document_id)
            document_name = document.name if hasattr(document, 'name') else f'{document_model}#{document_id}'
            
            return self.create({
                'document_model': document_model,
                'document_id': document_id,
                'document_name': document_name,
                'retention_rule_id': retention_rule_id,
            })
        except Exception as e:
            _logger.error(f'Lỗi tạo retention log: {str(e)}')
            return False

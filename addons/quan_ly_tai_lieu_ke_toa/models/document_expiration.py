# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class DocumentExpiration(models.Model):
    """Model quản lý ngày hết hạn & báo động"""
    _name = 'document.expiration'
    _description = 'Quản lý Hạn sử dụng Tài liệu'
    _order = 'ngay_het_han ASC'

    # Thông tin cơ bản
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

    # Thời gian
    ngay_tao = fields.Date(
        string='Ngày tạo',
        readonly=True,
        default=fields.Date.today
    )

    ngay_het_han = fields.Date(
        string='Ngày hết hạn',
        required=True,
        tracking=True,
        help='Ngày hết hạn của tài liệu'
    )

    ngay_canh_bao_1 = fields.Date(
        string='Cảnh báo lần 1',
        compute='_compute_canh_bao_dates',
        help='Cảnh báo 30 ngày trước hết hạn'
    )

    ngay_canh_bao_2 = fields.Date(
        string='Cảnh báo lần 2',
        compute='_compute_canh_bao_dates',
        help='Cảnh báo 7 ngày trước hết hạn'
    )

    ngay_canh_bao_3 = fields.Date(
        string='Cảnh báo lần 3',
        compute='_compute_canh_bao_dates',
        help='Cảnh báo 1 ngày trước hết hạn'
    )

    # Trạng thái
    trang_thai = fields.Selection([
        ('con_hieu_luc', 'Còn hiệu lực'),
        ('canh_bao_1', 'Cảnh báo - 30 ngày'),
        ('canh_bao_2', 'Cảnh báo - 7 ngày'),
        ('canh_bao_3', 'Cảnh báo - 1 ngày'),
        ('het_han', 'Hết hạn'),
        ('da_gia_han', 'Đã gia hạn'),
        ('huy_bo', 'Hủy bỏ'),
    ], string='Trạng thái', compute='_compute_trang_thai', store=True, tracking=True)

    so_ngay_con_lai = fields.Integer(
        string='Số ngày còn lại',
        compute='_compute_so_ngay_con_lai'
    )

    # Gia hạn
    da_gia_han = fields.Boolean(
        string='Đã gia hạn?',
        default=False,
        tracking=True
    )

    ngay_gia_han = fields.Date(
        string='Ngày gia hạn',
        tracking=True
    )

    ngay_het_han_moi = fields.Date(
        string='Ngày hết hạn mới',
        tracking=True,
        help='Nếu đã gia hạn'
    )

    ly_do_gia_han = fields.Text(
        string='Lý do gia hạn',
        tracking=True
    )

    # Thông báo
    da_gui_thong_bao = fields.Boolean(
        string='Đã gửi thông báo?',
        default=False,
        readonly=True
    )

    danh_sach_nguoi_canh_bao = fields.Text(
        string='Danh sách người cảnh báo',
        help='Người sẽ nhận thông báo'
    )

    # Ghi chú
    ghi_chu = fields.Text(
        string='Ghi chú'
    )

    @api.depends('ngay_het_han')
    def _compute_canh_bao_dates(self):
        for record in self:
            if record.ngay_het_han:
                record.ngay_canh_bao_1 = record.ngay_het_han - timedelta(days=30)
                record.ngay_canh_bao_2 = record.ngay_het_han - timedelta(days=7)
                record.ngay_canh_bao_3 = record.ngay_het_han - timedelta(days=1)
            else:
                record.ngay_canh_bao_1 = None
                record.ngay_canh_bao_2 = None
                record.ngay_canh_bao_3 = None

    @api.depends('ngay_het_han', 'da_gia_han', 'ngay_het_han_moi')
    def _compute_trang_thai(self):
        today = fields.Date.today()
        for record in self:
            if record.da_gia_han and record.ngay_het_han_moi:
                hsd = record.ngay_het_han_moi
            else:
                hsd = record.ngay_het_han
            
            if today > hsd:
                record.trang_thai = 'het_han'
            elif today >= (hsd - timedelta(days=1)):
                record.trang_thai = 'canh_bao_3'
            elif today >= (hsd - timedelta(days=7)):
                record.trang_thai = 'canh_bao_2'
            elif today >= (hsd - timedelta(days=30)):
                record.trang_thai = 'canh_bao_1'
            else:
                record.trang_thai = 'con_hieu_luc'

    @api.depends('ngay_het_han', 'da_gia_han', 'ngay_het_han_moi')
    def _compute_so_ngay_con_lai(self):
        today = fields.Date.today()
        for record in self:
            if record.da_gia_han and record.ngay_het_han_moi:
                hsd = record.ngay_het_han_moi
            else:
                hsd = record.ngay_het_han
            
            if hsd and today <= hsd:
                record.so_ngay_con_lai = (hsd - today).days
            else:
                record.so_ngay_con_lai = 0

    @api.model
    def create_expiration(self, document_model, document_id, ngay_het_han, 
                         danh_sach_nguoi_canh_bao='', ghi_chu=''):
        """
        Hàm helper tạo record expiration
        """
        try:
            document = self.env[document_model].browse(document_id)
            document_name = document.name if hasattr(document, 'name') else f'{document_model}#{document_id}'
            
            return self.create({
                'document_model': document_model,
                'document_id': document_id,
                'document_name': document_name,
                'ngay_het_han': ngay_het_han,
                'danh_sach_nguoi_canh_bao': danh_sach_nguoi_canh_bao,
                'ghi_chu': ghi_chu,
            })
        except Exception as e:
            _logger.error(f'Lỗi tạo expiration: {str(e)}')
            return False

    def action_gia_han(self):
        """Action gia hạn"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'document.expiration.gia_han',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_document_expiration_id': self.id}
        }

    def _send_warning_notification(self):
        """Gửi thông báo cảnh báo"""
        # TODO: Implement email notification
        pass

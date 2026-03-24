# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class DocumentNumberSequence(models.Model):
    """Model quản lý chuỗi số tự động"""
    _name = 'document.number.sequence'
    _description = 'Dãy số Tài liệu'

    # Thông tin cơ bản
    ten_day_so = fields.Char(
        string='Tên dãy số',
        required=True,
        help='Ví dụ: Số công văn đi, Số hóa đơn'
    )

    mo_ta = fields.Text(
        string='Mô tả'
    )

    # Định dạng
    prefix = fields.Char(
        string='Tiền tố',
        default='',
        help='Ví dụ: CV, HĐ, HÓA'
    )

    suffix = fields.Char(
        string='Hậu tố',
        default='',
        help='Ví dụ: /2024, /NAM'
    )

    so_chu_so_min = fields.Integer(
        string='Số chữ số tối thiểu',
        default=4,
        help='Số 0 đệm: 0001, 0002...'
    )

    template_format = fields.Char(
        string='Template định dạng',
        compute='_compute_template_format',
        help='Ví dụ: CV_{YYYY}_{MM}_{0000} → CV_2024_03_0001'
    )

    # Giá trị hiện tại
    gia_tri_hien_tai = fields.Integer(
        string='Giá trị hiện tại',
        default=0,
        readonly=True,
        help='Số tự động tăng'
    )

    gia_tri_tiep_theo = fields.Integer(
        string='Giá trị tiếp theo',
        compute='_compute_gia_tri_tiep_theo'
    )

    # Thiết lập
    tang_tu_dong = fields.Boolean(
        string='Tăng tự động?',
        default=True,
        help='Tự động tăng sau mỗi lần sử dụng'
    )

    reset_hang_nam = fields.Boolean(
        string='Reset mỗi năm?',
        default=False,
        help='Đặt lại về 1 vào đầu năm'
    )

    reset_hang_thang = fields.Boolean(
        string='Reset mỗi tháng?',
        default=False,
        help='Đặt lại về 1 vào đầu tháng'
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

    ngay_su_dung_cuoi = fields.Datetime(
        string='Lần sử dụng cuối',
        readonly=True
    )

    @api.depends('prefix', 'suffix', 'so_chu_so_min')
    def _compute_template_format(self):
        for record in self:
            format_str = record.prefix or ''
            if record.prefix and record.so_chu_so_min > 0:
                format_str += '/'
            format_str += '0' * record.so_chu_so_min if record.so_chu_so_min > 0 else 'NUMBER'
            if record.suffix:
                format_str += '/' + record.suffix
            record.template_format = format_str

    @api.depends('gia_tri_hien_tai')
    def _compute_gia_tri_tiep_theo(self):
        for record in self:
            record.gia_tri_tiep_theo = record.gia_tri_hien_tai + 1

    def get_next_number(self):
        """
        Lấy số tiếp theo và tăng counter
        """
        if not self.hoat_dong:
            raise UserError(_('Dãy số này không hoạt động'))
        
        # Check reset
        if self.reset_hang_nam:
            self._check_reset_hang_nam()
        if self.reset_hang_thang:
            self._check_reset_hang_thang()
        
        # Lấy giá trị hiện tại
        so_hien_tai = self.gia_tri_hien_tai
        
        # Tính số tự động
        so_dinh_dang = str(so_hien_tai).zfill(self.so_chu_so_min)
        
        # Tạo số hoàn chỉnh
        so_toan_bo = self.prefix or ''
        if self.prefix:
            so_toan_bo += '/'
        so_toan_bo += so_dinh_dang
        if self.suffix:
            so_toan_bo += '/' + self.suffix
        
        # Tăng counter nếu cấu hình
        if self.tang_tu_dong:
            self.write({
                'gia_tri_hien_tai': so_hien_tai + 1,
                'ngay_su_dung_cuoi': fields.Datetime.now()
            })
        
        return so_toan_bo

    def _check_reset_hang_nam(self):
        """Check và reset nếu sang năm khác"""
        today = datetime.now()
        ngay_su_dung = self.ngay_su_dung_cuoi
        
        if ngay_su_dung:
            ngay_su_dung_obj = fields.Datetime.from_string(ngay_su_dung)
            if ngay_su_dung_obj.year != today.year:
                self.write({'gia_tri_hien_tai': 0})

    def _check_reset_hang_thang(self):
        """Check và reset nếu sang tháng khác"""
        today = datetime.now()
        ngay_su_dung = self.ngay_su_dung_cuoi
        
        if ngay_su_dung:
            ngay_su_dung_obj = fields.Datetime.from_string(ngay_su_dung)
            if ngay_su_dung_obj.month != today.month or ngay_su_dung_obj.year != today.year:
                self.write({'gia_tri_hien_tai': 0})

    def action_test_number(self):
        """Action test sinh số"""
        so_test = self.get_next_number()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Số tiếp theo'),
                'message': so_test,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reset_counter(self):
        """Action reset counter"""
        self.write({'gia_tri_hien_tai': 0})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành công'),
                'message': _('Đã reset counter về 0'),
                'type': 'success',
                'sticky': False,
            }
        }

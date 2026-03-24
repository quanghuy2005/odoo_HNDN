# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class VanBanDocumentTemplate(models.Model):
    """Model template cho tài liệu căn"""
    _name = 'vanban.document.template'
    _description = 'Template Văn bản'

    # Thông tin template
    ten_template = fields.Char(
        string='Tên template',
        required=True,
        unique=True
    )

    mo_ta = fields.Text(
        string='Mô tả template'
    )

    lo_van_ban = fields.Selection([
        ('den', 'Văn bản đến'),
        ('di', 'Văn bản đi'),
    ], string='Loại văn bản', required=True)

    loai_van_ban = fields.Selection([
        ('quyet_dinh', 'Quyết định'),
        ('cong_van', 'Công văn'),
        ('thong_bao', 'Thông báo'),
        ('ke_hoach', 'Kế hoạch'),
        ('bao_cao', 'Báo cáo'),
        ('to_trinh', 'Tờ trình'),
        ('khac', 'Khác'),
    ], string='Loại cụ thể', required=True)

    # Nội dung mặc định
    do_khan_mac_dinh = fields.Selection([
        ('thuong', 'Thường'),
        ('khan', 'Khẩn'),
        ('hoa_toc', 'Hỏa tốc'),
    ], string='Độ khẩn mặc định', default='thuong')

    do_mat_mac_dinh = fields.Selection([
        ('binh_thuong', 'Bình thường'),
        ('mat', 'Mật'),
        ('tuyet_mat', 'Tuyệt mật'),
    ], string='Độ mật mặc định', default='binh_thuong')

    # Template fields
    trich_yeu_template = fields.Text(
        string='Template trích yếu',
        help='Template với ${placeholder}'
    )

    co_quan_template = fields.Char(
        string='Cơ quan mặc định (đến)',
        help='Cho template văn bản đến'
    )

    chuoi_soai_template = fields.Char(
        string='Chuỗi soạn thảo',
        help='Ví dụ: HCNS/...../2024'
    )

    # Sử dụng
    so_lan_su_dung = fields.Integer(
        string='Số lần sử dụng',
        default=0,
        readonly=True
    )

    # Quản lý
    hoat_dong = fields.Boolean(
        string='Hoạt động?',
        default=True,
        tracking=True
    )

    nguoi_tao = fields.Many2one(
        'res.users',
        string='Người tạo',
        readonly=True,
        default=lambda self: self.env.user
    )

    ngay_tao = fields.Datetime(
        string='Ngày tạo',
        readonly=True,
        default=fields.Datetime.now
    )

    def duplicate_template(self):
        """Duplicate template này"""
        new_template = self.copy({
            'ten_template': f'{self.ten_template} (Bản sao)',
            'so_lan_su_dung': 0,
        })
        return new_template

    def apply_template(self, values_dict=None):
        """
        Apply template - trả về dict có giá trị mặc định
        """
        result = {
            'loai_van_ban': self.loai_van_ban,
            'do_khan': self.do_khan_mac_dinh,
            'do_mat': self.do_mat_mac_dinh,
        }

        # Add trich_yeu
        if self.trich_yeu_template:
            result['trich_yeu'] = self._process_template(
                self.trich_yeu_template,
                values_dict or {}
            )

        # Add co_quan
        if self.co_quan_template:
            result['co_quan_ban_hanh' if self.lo_van_ban == 'den' else 'co_quan_nhan'] = self.co_quan_template

        # Tăng counter
        self.so_lan_su_dung += 1

        return result

    def _process_template(self, template_str, values_dict):
        """
        Process template string với placeholder
        ${field_name} -> được thay thế bằng giá trị
        """
        import re

        def replace_placeholder(match):
            key = match.group(1)
            return str(values_dict.get(key, ''))

        result = re.sub(r'\$\{([^}]+)\}', replace_placeholder, template_str)
        return result

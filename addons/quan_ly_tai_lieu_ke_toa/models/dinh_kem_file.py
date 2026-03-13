# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DinhKemFile(models.Model):
    """Model lưu trữ file đính kèm"""
    _name = 'dinh_kem.file'
    _description = 'File Đính Kèm'
    _rec_name = 'ten_file'

    # Liên kết
    tai_lieu = fields.Many2one(
        'tai_lieu.ke_toa',
        string='Tài Liệu',
        required=True,
        ondelete='cascade',
        tracking=True
    )

    # File
    file_noi_dung = fields.Binary(
        string='File',
        required=True,
        attachment=True,
        tracking=True
    )

    ten_file = fields.Char(
        string='Tên File',
        required=True,
        tracking=True
    )

    loai_file = fields.Char(
        string='Loại File',
        compute='_tinh_loai_file',
        store=True
    )

    kich_thuoc = fields.Float(
        string='Kích Thước (KB)',
        compute='_tinh_kich_thuoc_file',
        store=True
    )

    # Thông tin
    phien_ban_file = fields.Integer(
        string='Phiên Bản File',
        default=1,
        tracking=True
    )

    la_file_chinh = fields.Boolean(
        string='Là File Chính',
        default=False,
        tracking=True
    )

    mo_ta = fields.Text(
        string='Mô Tả',
        tracking=True
    )

    # Thời gian
    ngay_tai_len = fields.Datetime(
        string='Ngày Tải Lên',
        default=fields.Datetime.now,
        readonly=True,
        tracking=True
    )

    tai_len_boi = fields.Many2one(
        'res.users',
        string='Tải Lên Bởi',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )

    # Methods
    @api.depends('ten_file')
    def _tinh_loai_file(self):
        """Xác định loại file từ tên"""
        for dkf in self:
            if '.' in dkf.ten_file:
                dkf.loai_file = dkf.ten_file.split('.')[-1].upper()
            else:
                dkf.loai_file = 'Unknown'

    @api.depends('file_noi_dung')
    def _tinh_kich_thuoc_file(self):
        """Tính kích thước file"""
        for dkf in self:
            if dkf.file_noi_dung:
                # Kích thước của base64 string (ước tính)
                dkf.kich_thuoc = len(dkf.file_noi_dung) / 1024
            else:
                dkf.kich_thuoc = 0.0

    def hanh_dong_download(self):
        """Download file"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file_noi_dung/{self.ten_file}',
            'target': 'self',
        }

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import base64
import io

class TaiLieuKyDigital(models.Model):
    """Model lưu trữ thông tin ký điện tử"""
    _name = 'tai_lieu.ky_digital'
    _description = 'Ký Điện Tử Tài Liệu'
    _rec_name = 'tai_lieu'

    # Liên kết
    tai_lieu = fields.Many2one(
        'tai_lieu.ke_toa',
        string='Tài Liệu',
        required=True,
        ondelete='cascade'
    )

    # Thông tin người ký
    khach_hang_ky = fields.Many2one(
        'res.partner',
        string='Khách Hàng Ký',
        required=True,
        tracking=True
    )

    user_ky = fields.Many2one(
        'res.users',
        string='User Ký',
        tracking=True,
        help='User Portal của khách hàng'
    )

    email_ky = fields.Char(
        string='Email Người Ký',
        tracking=True
    )

    # Chữ ký
    chu_ky_image = fields.Binary(
        string='Chữ Ký (Ảnh)',
        help='Ảnh chữ ký từ portal'
    )

    chu_ky_image_filename = fields.Char(
        string='Tên File Chữ Ký',
        default='signature.png'
    )

    # Thời gian
    thoi_gian_ky = fields.Datetime(
        string='Thời Gian Ký',
        default=fields.Datetime.now,
        readonly=True
    )

    trang_thai_ky = fields.Selection([
        ('da_ky', 'Đã Ký'),
        ('huy_bo', 'Hủy Bỏ'),
    ], string='Trạng Thái', default='da_ky', tracking=True)

    ghi_chu = fields.Text(
        string='Ghi Chú Ký'
    )

    _sql_constraints = [
        ('tai_lieu_khach_unique', 'unique(tai_lieu, khach_hang_ky)',
         'Mỗi khách hàng chỉ được ký 1 lần trên một tài liệu!')
    ]


class TaiLieuKeToa_Extended(models.Model):
    """Mở rộng model Tài Liệu - Thêm xử lý ký"""
    _inherit = 'tai_lieu.ke_toa'

    # Trường để lưu trữ chữ ký
    ky_digitals = fields.One2many(
        'tai_lieu.ky_digital',
        'tai_lieu',
        string='Chữ Ký Điện Tử'
    )

    so_khach_da_ky = fields.Integer(
        string='Số Khách Đã Ký',
        compute='_tinh_so_khach_da_ky',
        store=True
    )

    so_khach_can_ky = fields.Integer(
        string='Số Khách Cần Ký',
        default=1,
        help='Số lượng khách hàng cần ký'
    )

    co_yeu_cau_ky = fields.Boolean(
        string='Yêu Cầu Ký',
        default=False,
        tracking=True
    )

    trang_thai_ky = fields.Selection([
        ('chua_ky', 'Chưa Ký'),
        ('dang_ky', 'Đang Ký'),
        ('da_ky_het', 'Đã Ký Hết'),
    ], string='Trạng Thái Ký', compute='_tinh_trang_thai_ky', store=True, tracking=True)

    @api.depends('ky_digitals', 'ky_digitals.trang_thai_ky')
    def _tinh_so_khach_da_ky(self):
        """Tính số khách hàng đã ký"""
        for record in self:
            record.so_khach_da_ky = len(record.ky_digitals.filtered(
                lambda k: k.trang_thai_ky == 'da_ky'
            ))

    @api.depends('so_khach_da_ky', 'so_khach_can_ky')
    def _tinh_trang_thai_ky(self):
        """Tính trạng thái ký"""
        for record in self:
            if not record.co_yeu_cau_ky:
                record.trang_thai_ky = 'chua_ky'
            elif record.so_khach_da_ky >= record.so_khach_can_ky:
                record.trang_thai_ky = 'da_ky_het'
            else:
                record.trang_thai_ky = 'dang_ky'

    def action_yeu_cau_ky(self):
        """Yêu cầu khách hàng ký"""
        self.ensure_one()
        if not self.khach_hang:
            raise UserError('Chưa chọn khách hàng!')
        
        self.co_yeu_cau_ky = True
        
        # Gửi email cho khách hàng
        template = self.env.ref('quan_ly_tai_lieu_ke_toa.email_yeu_cau_ky_template', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành Công!'),
                'message': _('Đã gửi yêu cầu ký cho khách hàng.'),
                'type': 'success',
            }
        }

    def action_tao_link_ky(self):
        """Tạo link ký cho khách hàng"""
        self.ensure_one()
        if not self.khach_hang:
            raise UserError('Chưa chọn khách hàng!')
        
        link = f"/my/hop_dong/ky/{self.id}"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Link Ký Hợp Đồng'),
                'message': f'Link: http://localhost:8069{link}',
                'type': 'info',
            }
        }


class ResPartner_Extended(models.Model):
    """Mở rộng Partner - Thêm Portal Access"""
    _inherit = 'res.partner'

    # Portal Access
    co_quyen_portal = fields.Boolean(
        string='Có Quyền Portal',
        default=False,
        help='Cho phép khách hàng truy cập portal'
    )

    email_portal = fields.Char(
        string='Email Portal',
        help='Email dùng để đăng nhập portal'
    )

    user_portal_id = fields.Many2one(
        'res.users',
        string='User Portal',
        help='User Odoo của khách hàng'
    )

    def action_tao_tai_khoan_portal(self):
        """Tạo tài khoản portal cho khách hàng"""
        self.ensure_one()
        
        if not self.email:
            raise UserError('Khách hàng chưa có email!')
        
        if self.user_portal_id:
            raise UserError('Khách hàng đã có tài khoản portal!')
        
        # Tạo User mới
        # Bắt đầu với group portal chuẩn
        group_ids = [self.env.ref('base.group_portal').id]
        # Thêm group CRM portal nếu tồn tại (tùy chọn)
        crm_portal_group = self.env.ref(
            'quan_ly_khach_hang_crm.group_crm_portal_customer',
            raise_if_not_found=False
        )
        if crm_portal_group:
            group_ids.append(crm_portal_group.id)

        user = self.env['res.users'].create({
            'name': self.name,
            'email': self.email,
            'login': self.email,
            'password': 'Portal@2024!',  # Mật khẩu tạm (nên yêu cầu đổi)
            'partner_id': self.id,
            'groups_id': [(6, 0, group_ids)],
            'active': True
        })
        
        self.user_portal_id = user.id
        self.co_quyen_portal = True
        self.email_portal = self.email
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tài Khoản Được Tạo!'),
                'message': _(f'Email: {self.email}\nMật khẩu: Portal@2024!'),
                'type': 'success',
            }
        }

    def action_reset_password_portal(self):
        """Reset mật khẩu portal"""
        self.ensure_one()
        
        if not self.user_portal_id:
            raise UserError('Khách hàng chưa có tài khoản portal!')
        
        # Gửi email reset password
        self.user_portal_id.action_send_reset_password_email()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Link Reset Được Gửi!'),
                'message': _('Email reset password đã được gửi.'),
                'type': 'success',
            }
        }

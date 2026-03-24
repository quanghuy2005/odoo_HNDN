# -*- coding: utf-8 -*-
from odoo import models, fields, api


class KhachHangMoRong(models.Model):
    """Mở rộng model Khách Hàng (res.partner) với các trường thêm"""
    _inherit = 'res.partner'

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        related='company_id.currency_id',
        readonly=True
    )

    # Trạng thái khách hàng trong CRM
    trang_thai_khach_hang = fields.Selection([
        ('tiem_nang', 'Tiềm Năng'),
        ('dang_giao_dich', 'Đang Giao Dịch'),
        ('da_ky_hop_dong', 'Đã Ký Hợp Đồng'),
        ('dang_phuc_vu', 'Đang Phục Vụ'),
        ('ngung_hop_tac', 'Ngừng Hợp Tác'),
    ], string='Trạng Thái Khách Hàng', default='tiem_nang')

    # Portal User Account
    user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        help='Tài khoản portal để khách hàng xem hợp đồng và hồ sơ'
    )

    co_portal_user = fields.Boolean(
        string='Có Portal User',
        compute='_check_portal_user',
        store=True
    )

    # Thông tin thêm
    tieu_su_giao_dich = fields.Text(
        string='Lịch Sử Giao Dịch',
        help='Ghi chú về những giao dịch trước đó'
    )
    
    ghi_chu_kinh_doanh = fields.Text(
        string='Ghi Chú Kinh Doanh',
        help='Những lưu ý, yêu cầu đặc biệt từ khách hàng'
    )

    # Liên hệ
    nguoi_dai_dien = fields.Char(
        string='Người Đại Diện',
        help='Tên người phụ trách/liên hệ tại công ty khách'
    )
    
    chuc_vu_dai_dien = fields.Char(
        string='Chức Vụ Người Đại Diện',
        help='Chức vụ của người đại diện'
    )

    # Thống kê
    so_tien_da_ky = fields.Float(
        string='Tổng Giá Trị Hợp Đồng (VND)',
        compute='_tinh_tong_gia_tri',
        help='Tổng giá trị tất cả hợp đồng đã ký'
    )

    so_luong_tai_lieu = fields.Integer(
        string='Số Hợp Đồng',
        compute='_tinh_so_luong_tai_lieu'
    )
    
    so_luong_van_ban = fields.Integer(
        string='Hồ Sơ Văn Bản',
        compute='_tinh_so_luong_van_ban'
    )

    def _tinh_tong_gia_tri(self):
        for khach in self:
            tong_tien = 0.0
            if 'tai_lieu.ke_toa' in self.env:
                doi_tac_goc = khach.commercial_partner_id
                tai_lieus = self.env['tai_lieu.ke_toa'].search([
                    ('khach_hang', 'child_of', doi_tac_goc.id),
                    ('trang_thai', 'in', ['da_ky', 'hoan_tat'])
                ])
                tong_tien = sum(tai_lieus.mapped('gia_tri_tai_lieu'))
            khach.so_tien_da_ky = tong_tien
            
    def _tinh_so_luong_tai_lieu(self):
        for khach in self:
            if 'tai_lieu.ke_toa' in self.env:
                khach.so_luong_tai_lieu = self.env['tai_lieu.ke_toa'].search_count([
                    ('khach_hang', 'child_of', khach.commercial_partner_id.id)
                ])
            else:
                khach.so_luong_tai_lieu = 0
            
    def action_xem_tai_lieu(self):
        """Hành động mở danh sách tài liệu khi bấm vào nút thông minh"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hợp Đồng Kế Toán',
            'res_model': 'tai_lieu.ke_toa',
            'view_mode': 'tree,form',
            'domain': [('khach_hang', 'child_of', self.commercial_partner_id.id)],
            'context': {'default_khach_hang': self.commercial_partner_id.id},
        }

    def _tinh_so_luong_van_ban(self):
        for khach in self:
            if 'ho_so_van_ban' in self.env:
                khach.so_luong_van_ban = self.env['ho_so_van_ban'].search_count([
                    ('khach_hang_id', 'child_of', khach.commercial_partner_id.id)
                ])
            else:
                khach.so_luong_van_ban = 0
                
    def action_xem_van_ban(self):
        """Hành động mở kho văn bản hành chính khi bấm vào nút thông minh"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hồ Sơ Hành Chính',
            'res_model': 'ho_so_van_ban',
            'view_mode': 'tree,form',
            'domain': [('khach_hang_id', 'child_of', self.commercial_partner_id.id)],
            'context': {'default_khach_hang_id': self.commercial_partner_id.id},
        }

    def _check_portal_user(self):
        """Kiểm tra xem khách hàng có portal user hay không"""
        for khach in self:
            khach.co_portal_user = bool(khach.user_id)

    def tao_portal_user(self):
        """Tạo portal user cho khách hàng"""
        from odoo.exceptions import ValidationError, UserError
        
        self.ensure_one()
        
        # Kiểm tra đã có user chưa
        if self.user_id:
            raise UserError('Khách hàng này đã có Portal User rồi!')
        
        # Kiểm tra email
        if not self.email:
            raise UserError('Vui lòng nhập email khách hàng trước tiên!')
        
        # Kiểm tra email có unique không
        existing_user = self.env['res.users'].search([
            ('login', '=', self.email),
            ('id', '!=', 2)  # Exclude internal user
        ])
        if existing_user:
            raise UserError(f'Email này đã được sử dụng bởi user khác: {existing_user.name}')
        
        try:
            # Tạo user mới
            new_user = self.env['res.users'].create({
                'name': self.name,
                'login': self.email,
                'email': self.email,
                'partner_id': self.id,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],  # Add to portal group
            })
            
            # Lưu user vào field
            self.user_id = new_user.id
            
            # Gửi invitation email (nếu lỗi, vẫn tiếp tục)
            email_sent = False
            try:
                new_user.action_reset_password()
                email_sent = True
            except Exception as email_error:
                # Gửi email fail, nhưng vẫn tạo user thành công
                pass
            
            # Thông báo kết quả
            if email_sent:
                message = f'✅ Tài khoản portal đã được tạo cho {self.name}. Email đặt lại mật khẩu đã được gửi đến {self.email}.'
            else:
                message = f'✅ Tài khoản portal đã được tạo cho {self.name}.\n⚠️ Email không gửi được. Để set mật khẩu:\n1. Vào Settings → Users\n2. Tìm user "{self.email}"\n3. Bấm "Reset Password"'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành Công!',
                    'message': message,
                    'type': 'success',
                    'sticky': True,
                }
            }
        except Exception as e:
            raise UserError(f'Lỗi tạo tài khoản: {str(e)}')

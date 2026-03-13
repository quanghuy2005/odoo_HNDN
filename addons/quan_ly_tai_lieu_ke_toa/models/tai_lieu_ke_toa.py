# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class TaiLieuKeToa(models.Model):
    """Model lưu trữ tài liệu của khách hàng"""
    _name = 'tai_lieu.ke_toa'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tài Liệu Kế Toán'
    _rec_name = 'ma_tai_lieu'

    # Thông tin cơ bản
    ma_tai_lieu = fields.Char(
        string='Mã Tài Liệu',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Mới')
    )

    ten_tai_lieu = fields.Char(
        string='Tên Tài Liệu',
        required=True,
        tracking=True
    )

    loai_tai_lieu = fields.Selection([
        ('hop_dong', 'Hợp Đồng'),
        ('bao_gia', 'Báo Giá'),
        ('hoa_don', 'Hóa Đơn'),
        ('giay_phep', 'Giấy Phép'),
        ('bao_cao', 'Báo Cáo'),
        ('hop_dong_lao_dong', 'Hợp Đồng Lao Động'),
        ('bien_ban', 'Biên Bản'),
        ('khac', 'Khác'),
    ], string='Loại Tài Liệu', required=True, tracking=True)

    mo_ta = fields.Text(
        string='Mô Tả',
        tracking=True
    )

    # Liên kết với khách hàng & nhân viên
    khach_hang = fields.Many2one(
        'res.partner',
        string='Khách Hàng',
        required=True,
        tracking=True,
        domain=[('is_company', '=', False)]
    )

    nhan_vien_phu_trach = fields.Many2one(
        'hr.employee',
        string='Nhân Viên Phụ Trách',
        tracking=True
    )

    # Thời gian
    ngay_tao = fields.Date(
        string='Ngày Tạo',
        default=fields.Date.today,
        readonly=True,
        tracking=True
    )

    ngay_hieu_luc = fields.Date(
        string='Ngày Hiệu Lực',
        tracking=True
    )

    ngay_het_han = fields.Date(
        string='Ngày Hết Hạn',
        tracking=True
    )

    # Trạng thái
    trang_thai = fields.Selection([
        ('tao_moi', '1. Tạo Mới'),
        ('da_gui', '2. Đã Gửi'),
        ('dang_duyet', '3. Đang Phê Duyệt'),
        ('da_phe_duyet', '4. Đã Phê Duyệt'),
        ('da_ky', '5. Đã Ký'),
        ('hoan_tat', '6. Hoàn Tất'),
        ('het_han', '7. Hết Hạn'),
        ('huy', '8. Hủy'),
    ], string='Trạng Thái', default='tao_moi', tracking=True, copy=False)

    # Phiên bản
    phien_ban = fields.Integer(
        string='Phiên Bản',
        default=1,
        readonly=True,
        tracking=True
    )

    # Phê duyệt
    can_phe_duyet = fields.Boolean(
        string='Cần Phê Duyệt',
        default=True,
        tracking=True
    )

    phe_duyet_boi = fields.Many2one(
        'res.users',
        string='Phê Duyệt Bởi',
        readonly=True,
        tracking=True
    )

    ngay_phe_duyet = fields.Datetime(
        string='Ngày Phê Duyệt',
        readonly=True,
        tracking=True
    )

    # Ký
    da_ky = fields.Boolean(
        string='Đã Ký',
        default=False,
        readonly=True,
        tracking=True
    )

    ky_boi = fields.Many2one(
        'res.users',
        string='Ký Bởi',
        readonly=True,
        tracking=True
    )

    ngay_ky = fields.Datetime(
        string='Ngày Ký',
        readonly=True,
        tracking=True
    )

    # Tìm kiếm
    noi_dung_tim_kiem = fields.Text(
        string='Nội Dung Tìm Kiếm',
        compute='_tinh_noi_dung_tim_kiem',
        store=True,
        help='Trường này giúp tìm kiếm toàn văn bản'
    )

    # One2many
    danh_sach_phieu_phe_duyet = fields.One2many(
        'phieu.phe_duyet',
        'tai_lieu',
        string='Danh Sách Phê Duyệt',
        readonly=True
    )

    danh_sach_file_dinh_kem = fields.One2many(
        'dinh_kem.file',
        'tai_lieu',
        string='File Đính Kèm',
        readonly=True
    )

    # Thống kê
    so_luong_phe_duyet = fields.Integer(
        string='Số Phê Duyệt',
        compute='_tinh_so_luong_phe_duyet',
        store=True
    )

    so_luong_file = fields.Integer(
        string='Số File',
        compute='_tinh_so_luong_file',
        store=True
    )

    # API Methods
    @api.model
    def create(self, vals):
        """Override create để tự động generate mã tài liệu"""
        if vals.get('ma_tai_lieu', _('Mới')) == _('Mới'):
            vals['ma_tai_lieu'] = self.env['ir.sequence'].next_by_code('tai_lieu.sequence') or 'TD/2024/03/0001'
        return super().create(vals)

    @api.constrains('ngay_het_han', 'ngay_hieu_luc')
    def _check_ngay_het_han(self):
        """Kiểm tra ngày hết hạn phải lớn hơn ngày hiệu lực"""
        for td in self:
            if td.ngay_het_han and td.ngay_hieu_luc:
                if td.ngay_het_han < td.ngay_hieu_luc:
                    raise ValidationError('Ngày hết hạn phải lớn hơn hoặc bằng ngày hiệu lực!')

    @api.depends('ten_tai_lieu', 'mo_ta', 'khach_hang', 'danh_sach_file_dinh_kem')
    def _tinh_noi_dung_tim_kiem(self):
        """Tính toán trường tìm kiếm - update khi file hoặc thông tin thay đổi"""
        for td in self:
            # Tính toán nội dung từ tài liệu + tên file
            file_search = ' '.join([f.ten_file for f in td.danh_sach_file_dinh_kem])
            td.noi_dung_tim_kiem = f"{td.ten_tai_lieu or ''} {td.mo_ta or ''} {td.khach_hang.name or ''} {file_search}"

    @api.depends('danh_sach_phieu_phe_duyet')
    def _tinh_so_luong_phe_duyet(self):
        """Tính số lượng phê duyệt"""
        for td in self:
            td.so_luong_phe_duyet = len(td.danh_sach_phieu_phe_duyet)

    @api.depends('danh_sach_file_dinh_kem')
    def _tinh_so_luong_file(self):
        """Tính số lượng file"""
        for td in self:
            td.so_luong_file = len(td.danh_sach_file_dinh_kem)

    # Business Logic Methods
    def hanh_dong_gui_phe_duyet(self):
        """Gửi tài liệu để phê duyệt"""
        if self.trang_thai != 'tao_moi':
            raise UserError('Chỉ tài liệu mới mới có thể gửi phê duyệt!')
        
        self.write({'trang_thai': 'da_gui'})
        
        # Gửi email thông báo
        self._gui_email_thong_bao('guipheduyet')

    def hanh_dong_yeu_cau_phe_duyet(self):
        """Yêu cầu phê duyệt từ nhân viên"""
        if not self.can_phe_duyet:
            raise UserError('Tài liệu này không cần phê duyệt!')
        
        if self.trang_thai not in ['tao_moi', 'da_gui']:
            raise UserError('Trạng thái không hợp lệ để yêu cầu phê duyệt!')

        self.write({'trang_thai': 'dang_duyet'})
        
        # Tạo phiếu phê duyệt
        phieu = self.env['phieu.phe_duyet'].create({
            'tai_lieu': self.id,
            'trang_thai_phieu': 'pending',
        })
        
        self._gui_email_thong_bao('yeucaupheduyet')

    def hanh_dong_phe_duyet(self):
        """Phê duyệt tài liệu"""
        if self.trang_thai != 'dang_duyet':
            raise UserError('Tài liệu không ở trạng thái đang phê duyệt!')
        
        self.write({
            'trang_thai': 'da_phe_duyet',
            'phe_duyet_boi': self.env.user.id,
            'ngay_phe_duyet': fields.Datetime.now(),
        })
        
        # Cập nhật phiếu phê duyệt
        phieu = self.danh_sach_phieu_phe_duyet.filtered(lambda x: x.trang_thai_phieu == 'pending')
        if phieu:
            phieu.write({
                'trang_thai_phieu': 'approved',
                'ngay_phe_duyet': fields.Datetime.now(),
            })
        
        self._gui_email_thong_bao('dapheduyet')

    def hanh_dong_ky(self):
        """Ký tài liệu"""
        if self.trang_thai != 'da_phe_duyet':
            raise UserError('Chỉ tài liệu đã phê duyệt mới có thể ký!')
        
        self.write({
            'trang_thai': 'da_ky',
            'da_ky': True,
            'ky_boi': self.env.user.id,
            'ngay_ky': fields.Datetime.now(),
        })
        
        self._gui_email_thong_bao('daky')

    def hanh_dong_hoan_tat(self):
        """Hoàn tất tài liệu"""
        if self.trang_thai != 'da_ky':
            raise UserError('Chỉ tài liệu đã ký mới có thể hoàn tất!')
        
        self.write({
            'trang_thai': 'hoan_tat',
        })
        
        self._gui_email_thong_bao('hoanthat')

    def hanh_dong_tao_phien_ban_moi(self):
        """Tạo phiên bản mới từ tài liệu hiện tại"""
        if self.trang_thai not in ['hoan_tat', 'het_han']:
            raise UserError('Chỉ tài liệu hoàn tất mới có thể tạo phiên bản mới!')
        
        # Sao chép tài liệu
        tai_lieu_moi = self.copy({
            'phien_ban': self.phien_ban + 1,
            'ngay_tao': fields.Date.today(),
            'trang_thai': 'tao_moi',
            'phe_duyet_boi': False,
            'ngay_phe_duyet': False,
            'da_ky': False,
            'ky_boi': False,
            'ngay_ky': False,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': tai_lieu_moi.id,
            'view_mode': 'form',
        }

    def hanh_dong_gui_cho_khach(self):
        """Gửi tài liệu cho khách hàng"""
        self._gui_email_thong_bao('guichokhach')

    def hanh_dong_huy(self):
        """Hủy tài liệu"""
        self.write({'trang_thai': 'huy'})

    def _gui_email_thong_bao(self, loai_email):
        """Gửi email thông báo dựa trên loại"""
        # Cơ chế gửi email (có thể được mở rộng sau)
        self.message_post(
            body=f'Email thông báo: {loai_email} được gửi',
            message_type='notification'
        )

    # Search Methods
    def action_xem_file(self):
        """xem danh sách file"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dinh_kem.file',
            'view_mode': 'tree,form',
            'domain': [('tai_lieu', '=', self.id)],
        }

    def action_xem_phe_duyet(self):
        """Xem danh sách phê duyệt"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'phieu.phe_duyet',
            'view_mode': 'tree,form',
            'domain': [('tai_lieu', '=', self.id)],
        }

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import base64


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
        tracking=True
    )

    nhan_vien_phu_trach = fields.Many2one(
        'hr.employee',
        string='Nhân Viên Phụ Trách',
        tracking=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Công Ty',
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền Tệ',
        related='company_id.currency_id',
        readonly=True
    )

    gia_tri_tai_lieu = fields.Float(
        string='Giá Trị (VND)',
        tracking=True,
        help='Giá trị tài chính của Hợp đồng / Báo giá / Hóa đơn'
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
        string='Ngày Sếp Ký',
        readonly=True,
        tracking=True
    )

    # Chữ Ký Số (E-Signature) Phase 4
    chu_ky_nguoi_duyet = fields.Binary(
        string="Chữ ký Giám đốc", 
        attachment=True,
        tracking=True
    )
    chu_ky_khach_hang = fields.Binary(
        string="Chữ ký Khách hàng", 
        attachment=True,
        tracking=True
    )
    ngay_khach_ky = fields.Datetime(
        string="Thời gian Khách ký", 
        readonly=True
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
    )

    file_dinh_kem_chinh_id = fields.Many2one(
        'dinh_kem.file',
        string='File Đính Kèm Chính',
        compute='_tinh_file_dinh_kem_chinh'
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

    @api.depends('danh_sach_file_dinh_kem', 'danh_sach_file_dinh_kem.la_file_chinh', 'danh_sach_file_dinh_kem.ngay_tai_len')
    def _tinh_file_dinh_kem_chinh(self):
        """Chọn file chính để hiển thị/tải xuống nhanh"""
        for td in self:
            files = td.danh_sach_file_dinh_kem.sorted(
                key=lambda f: (
                    0 if f.la_file_chinh else 1,
                    -(fields.Datetime.to_datetime(f.ngay_tai_len).timestamp() if f.ngay_tai_len else 0),
                    -f.id,
                )
            )
            td.file_dinh_kem_chinh_id = files[:1].id if files else False

    # Business Logic Methods
    def hanh_dong_gui_phe_duyet(self):
        """Gửi tài liệu để phê duyệt"""
        if self.trang_thai != 'tao_moi':
            raise UserError('Chỉ tài liệu mới mới có thể gửi phê duyệt!')
        
        self.write({'trang_thai': 'da_gui'})

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

    def hanh_dong_hoan_tat(self):
        """Hoàn tất tài liệu"""
        if self.trang_thai != 'da_ky':
            raise UserError('Chỉ tài liệu đã ký mới có thể hoàn tất!')
        
        self.write({
            'trang_thai': 'hoan_tat',
        })
        
        # Tự động sinh hóa đơn nếu là loại tài liệu sinh tài chính
        if self.loai_tai_lieu in ['hop_dong', 'bao_gia', 'hoa_don']:
            self._tao_hoa_don_nhap_tu_dong()

        # Tự động backup Google Drive nếu cấu hình bật
        self._backup_to_google_drive(event='hoan_tat')
        
    def _backup_to_google_drive(self, event='hoan_tat'):
        """Thực hiện backup các file đính kèm lên Google Drive theo sự kiện"""
        drive_config = self.env['google.drive.integration'].search([('bat_backup', '=', True)], limit=1)
        if not drive_config:
            return
            
        # Kiểm tra điều kiện backup tương ứng
        if event == 'hoan_tat' and not drive_config.backup_khi_hoan_tat:
            return
            
        # Kiểm tra file
        truong_hop_files = self.danh_sach_file_dinh_kem
        if not truong_hop_files:
            return
            
        thong_bao_backup = []
        for doc_file in truong_hop_files:
            if not doc_file.file_noi_dung:
                continue
            
            try:
                # Odoo binary fields are base64 strings
                file_content_decoded = base64.b64decode(doc_file.file_noi_dung)
                
                mime_type = 'application/octet-stream' # Default
                if doc_file.loai_file:
                    lf = doc_file.loai_file.upper()
                    if lf == 'PDF': mime_type = 'application/pdf'
                    elif lf in ['DOC', 'DOCX']: mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    elif lf in ['XLS', 'XLSX']: mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    elif lf in ['PNG', 'JPG', 'JPEG']: mime_type = f'image/{lf.lower().replace("jpg", "jpeg")}'
                
                # Format tên file kèm theo mã tài liệu
                ten_file_drive = f"[{self.ma_tai_lieu}] {doc_file.ten_file}"
                
                result = drive_config.upload_file_to_drive(
                    file_name=ten_file_drive, 
                    file_content=file_content_decoded,
                    file_type=mime_type
                )
                
                if result and result.get('link'):
                    thong_bao_backup.append(f"<li><a href='{result.get('link')}' target='_blank'>{ten_file_drive}</a></li>")
                    
            except Exception as e:
                self.message_post(body=f"⚠️ <b>Lỗi backup Drive ({doc_file.ten_file}):</b> {str(e)}")
                
        if thong_bao_backup:
            self.message_post(body=f"☁️ <b>Đã Auto-Backup lên Google Drive:</b><ul>{''.join(thong_bao_backup)}</ul>")

    def _tao_hoa_don_nhap_tu_dong(self):
        """Tự động tạo hóa đơn nháp bên phân hệ Kế toán của Odoo"""
        # Kiểm tra xem hệ thống có cài đặt module account không
        if 'account.move' in self.env:
            # Tìm tài khoản doanh thu mặc định cho loại tài liệu bán ra
            # Trong Odoo 15, search theo internal_type hoặc account_type (nếu có)
            # Hoặc fallback về tài khoản đầu tiên thuộc nhóm Doanh Thu (Income)
            income_account = self.env['account.account'].search([
                ('user_type_id.internal_group', '=', 'income')
            ], limit=1)
            
            if not income_account:
                # Thử tìm theo mã tài khoản phổ biến ở VN (511x) hoặc quốc tế (4xxx)
                income_account = self.env['account.account'].search([
                    ('code', '=like', '511%')
                ], limit=1)

            invoice_vals = {
                'move_type': 'out_invoice', 
                'partner_id': self.khach_hang.id,
                'invoice_date': fields.Date.today(),
                'ref': f"Tự động từ: {self.ma_tai_lieu}", 
                'invoice_line_ids': [(0, 0, {
                    'name': f'Thanh toán theo tài liệu: {self.ten_tai_lieu}',
                    'quantity': 1,
                    'price_unit': self.gia_tri_tai_lieu or 0.0,
                    'account_id': income_account.id if income_account else False,
                })],
            }
            try:
                invoice = self.env['account.move'].create(invoice_vals)
                self.message_post(body=f"✅ Đã tự động tạo hóa đơn nháp: <a href='/web#id={invoice.id}&model=account.move&view_type=form'>{invoice.name or 'Draft Invoice'}</a>")
            except Exception as e:
                self.message_post(body=f"⚠️ Lỗi tạo hóa đơn tự động: {str(e)}")

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
        self.ensure_one()
        template = self.env.ref('quan_ly_tai_lieu_ke_toa.email_template_gui_cho_khach', raise_if_not_found=False)
        if not template:
            raise UserError(_("Không tìm thấy mẫu email 'Gửi Cho Khách Hàng'."))
        if not self.khach_hang.email:
            raise UserError(_("Khách hàng '%s' không có địa chỉ email.", self.khach_hang.name))

        template.send_mail(self.id, force_send=True)
        self.message_post(body=_("Email đã được gửi cho khách hàng: %s", self.khach_hang.name))

    def hanh_dong_huy(self):
        """Hủy tài liệu"""
        self.write({'trang_thai': 'huy'})

    @api.model
    def cron_canh_bao_het_han(self):
        """Hàm chạy tự động (Cron Job) mỗi ngày để kiểm tra tài liệu sắp hết hạn"""
        ngay_canh_bao = fields.Date.today() + timedelta(days=7)
        # Tìm các tài liệu hoàn tất, có ngày hết hạn đúng bằng 7 ngày tới
        tai_lieus = self.search([
            ('trang_thai', 'in', ['da_ky', 'hoan_tat']),
            ('ngay_het_han', '=', ngay_canh_bao)
        ])
        for tl in tai_lieus:
            tl.write({'trang_thai': 'het_han'}) # Cập nhật trạng thái
            tl.message_post(body="⚠️ <b>CẢNH BÁO TÀI CHÍNH:</b> Tài liệu/Hợp đồng này sẽ hết hạn trong 7 ngày tới. Vui lòng liên hệ khách hàng để gia hạn hoặc xuất hóa đơn thanh toán!", message_type="notification")

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

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class DinhKemFile(models.Model):
    """Model lưu trữ file đính kèm"""
    _name = 'dinh_kem.file'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
            if dkf.ten_file and '.' in dkf.ten_file:
                dkf.loai_file = dkf.ten_file.split('.')[-1].upper()
            else:
                dkf.loai_file = 'Unknown'

    @api.depends('file_noi_dung')
    def _tinh_kich_thuoc_file(self):
        """Tính kích thước file (KB)"""
        for dkf in self:
            if dkf.file_noi_dung:
                # Kích thước thực tế của file sau khi giải mã base64
                file_decoded = base64.b64decode(dkf.file_noi_dung)
                dkf.kich_thuoc = len(file_decoded) / 1024
            else:
                dkf.kich_thuoc = 0.0

    def hanh_dong_download(self):
        """Download file"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file_noi_dung/{self.ten_file}',
            'target': 'self',
        }

    def hanh_dong_tom_tat_ai(self):
        """Hành động đọc text từ PDF và nhờ AI tóm tắt"""
        self.ensure_one()
        if not self.file_noi_dung:
            raise UserError('File đính kèm bị rỗng!')
            
        if self.loai_file != 'PDF':
            raise UserError('Hiện tại hệ thống chỉ hỗ trợ AI tóm tắt cho định dạng PDF.')
            
        if not PYPDF2_AVAILABLE:
            raise UserError('Cần cài đặt thư viện PyPDF2: pip install PyPDF2')

        # 1. Tìm cấu hình AI đang bật
        ai_config = self.env['ai.configuration'].search([('bat_tom_tat', '=', True)], limit=1)
        if not ai_config:
            raise UserError('Chưa bật Cấu hình AI nào trong hệ thống.')

        # 2. Đọc file base64 và extract text từ PDF
        try:
            file_data = base64.b64decode(self.file_noi_dung)
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            extracted_text = ""
            for i, page in enumerate(pdf_reader.pages):
                # Chỉ lấy 5 trang đầu để tiết kiệm token
                if i >= 5: 
                    break
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
                    
            if not extracted_text.strip():
                raise UserError('Không thể trích xuất văn bản từ PDF (Có thể PDF là file ảnh scan).')
                
        except Exception as e:
            raise UserError(f'Lỗi khi đọc file PDF: {str(e)}')

        # 3. Gửi lên AI
        summary_result = ai_config.tom_tat_noi_dung(extracted_text)
        
        if summary_result:
            # Lưu log vào Chatter của tài liệu cha
            log_body = f"<p>🤖 <b>AI Tóm tắt file {self.ten_file}:</b></p><p>{summary_result.replace(chr(10), '<br/>')}</p>"
            self.tai_lieu.message_post(body=log_body)
            # Cập nhật ô mô tả của file đính kèm để dễ xem
            self.write({'mo_ta': f"AI SUMMARIZED:\n{summary_result}"})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'AI Hoàn Tất',
                    'message': 'Đã tóm tắt thành công! Xem kết quả ở Mô tả file hoặc trong mục thảo luận của Tài Liệu.',
                    'type': 'success',
                }
            }
        else:
            raise UserError('AI phản hồi rỗng. Vui lòng kiểm tra lại cấu hình API Key.')

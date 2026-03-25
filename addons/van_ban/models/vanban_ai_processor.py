# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

try:
    import google.genai as genai
except ImportError:
    genai = None

_logger = logging.getLogger(__name__)


class VanBanAIProcessor(models.Model):
    """Xử lý AI cho Công văn: Phân loại, Trích từ khóa, Tóm tắt"""
    _name = 'vanban.ai.processor'
    _description = 'Xử Lý AI Công Văn'
    _rec_name = 'vanban_id'

    # Liên kết
    vanban_model = fields.Selection([
        ('van_ban_den', 'Công văn đến'),
        ('van_ban_di', 'Công văn đi'),
    ], string='Loại công văn', required=True)

    vanban_id = fields.Integer(
        string='ID Công văn',
        required=True
    )

    vanban_name = fields.Char(
        string='Số hiệu công văn',
        readonly=True
    )

    # Nội dung
    noi_dung_cong_van = fields.Text(
        string='Nội dung',
        required=True,
        help='Nội dung gốc của công văn'
    )

    # ===== PHÂN LOẠI =====
    phan_loai = fields.Selection([
        ('quyet_dinh', 'Quyết định'),
        ('cong_van', 'Công văn'),
        ('thong_bao', 'Thông báo'),
        ('ke_hoach', 'Kế hoạch'),
        ('bao_cao', 'Báo cáo'),
        ('to_trinh', 'Tờ trình'),
        ('lenh_chi_thi', 'Lệnh/Chỉ thị'),
        ('don_de_nghi', 'Đơn/Đề nghị'),
        ('khac', 'Khác'),
    ], string='Phân loại', readonly=True, store=True, help='Phân loại tự động bởi AI')

    do_tin_cay_phan_loai = fields.Float(
        string='Độ tin cậy phân loại (%)',
        readonly=True,
        store=True,
        help='Độ tin cậy của kết quả phân loại (0-100%)'
    )

    # ===== TỪ KHÓA =====
    tu_khoa = fields.Text(
        string='Từ khóa',
        readonly=True,
        store=True,
        help='Các từ/cụm từ khóa trích xuất từ nội dung'
    )

    do_tin_cay_tu_khoa = fields.Float(
        string='Độ tin cậy từ khóa (%)',
        readonly=True,
        store=True
    )

    # ===== TÓM TẮT =====
    tom_tat = fields.Text(
        string='Tóm tắt',
        readonly=True,
        store=True,
        help='Tóm tắt 2-3 câu của công văn'
    )

    do_tin_cay_tom_tat = fields.Float(
        string='Độ tin cậy tóm tắt (%)',
        readonly=True,
        store=True
    )

    # ===== AUDIT =====
    trang_thai = fields.Selection([
        ('cho', 'Chờ xử lý'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('thanh_cong', 'Thành công'),
        ('that_bai', 'Thất bại'),
    ], string='Trạng thái', default='cho', readonly=True)

    loi = fields.Text(
        string='Lỗi',
        readonly=True,
        help='Thông báo lỗi nếu xử lý AI thất bại'
    )

    ngay_xu_ly = fields.Datetime(
        string='Ngày xử lý',
        readonly=True,
        default=fields.Datetime.now
    )

    # ===== ACTIONS =====
    def action_xu_ly_ai(self):
        """
        Xử lý AI: Phân loại + Trích từ khóa + Tóm tắt
        """
        try:
            if not genai:
                raise UserError(_('Google Gemini API chưa cài đặt'))

            if not self.noi_dung_cong_van:
                raise UserError(_('Vui lòng nhập nội dung công văn'))

            self.write({'trang_thai': 'dang_xu_ly'})

            # Get API key from vanban.ai.config
            ai_config = self.env['vanban.ai.config'].search(
                [('is_active', '=', True)],
                limit=1
            )

            if not ai_config or not ai_config.api_key:
                raise UserError(_('Chưa cấu hình Google Gemini API Key cho Văn Bản.\nVào Cấu Hình → AI API Key để cài đặt.'))

            client = genai.Client(api_key=ai_config.api_key)

            # Đọc full text từ file đính kèm PDF nếu có
            vanban_record = self.env[self.vanban_model].browse(self.vanban_id)
            full_text = self.noi_dung_cong_van or ''

            if hasattr(vanban_record, 'file_dinh_kem') and vanban_record.file_dinh_kem and vanban_record.file_name and vanban_record.file_name.lower().endswith('.pdf'):
                try:
                    import base64
                    import io
                    import PyPDF2
                    file_data = base64.b64decode(vanban_record.file_dinh_kem)
                    pdf_file = io.BytesIO(file_data)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)

                    extracted = ""
                    for i, page in enumerate(pdf_reader.pages):
                        if i >= 10:  # Giới hạn 10 trang đầu
                            break
                        text = page.extract_text()
                        if text:
                            extracted += text + "\n"
                    
                    if extracted.strip():
                        # Gộp cả trích yếu và nội dung PDF
                        full_text = f"Trích yếu: {self.noi_dung_cong_van}\n\nNội dung chi tiết:\n{extracted}"
                except Exception as e:
                    _logger.warning(f"Không thể đọc text từ PDF: {str(e)}")

            if not full_text.strip():
                raise UserError(_('Không có nội dung văn bản để phân tích (Trích yếu trống và không có PDF).'))

            # === PHÂN LOẠI ===
            phan_loai_result = self._classify_vanban(client, full_text)

            # === TRÍCH TỪ KHÓA ===
            tu_khoa_result = self._extract_keywords(client, full_text)

            # === TÓM TẮT ===
            tom_tat_result = self._summarize_vanban(client, full_text)

            # Lưu kết quả
            self.write({
                'phan_loai': phan_loai_result['type'],
                'do_tin_cay_phan_loai': phan_loai_result['confidence'],
                'tu_khoa': tu_khoa_result['keywords'],
                'do_tin_cay_tu_khoa': tu_khoa_result['confidence'],
                'tom_tat': tom_tat_result['summary'],
                'do_tin_cay_tom_tat': tom_tat_result['confidence'],
                'trang_thai': 'thanh_cong',
            })

        except Exception as e:
            _logger.error(f'Lỗi xử lý AI công văn: {str(e)}')
            self.write({
                'trang_thai': 'that_bai',
                'loi': str(e)
            })

    def _classify_vanban(self, client, full_text):
        """
        Phân loại công văn thành các loại: Quyết định, Công văn, Thông báo, v.v.
        """
        try:
            prompt = f"""
            Phân loại công văn dưới đây vào một trong các loại:
            - quyet_dinh: Quyết định
            - cong_van: Công văn
            - thong_bao: Thông báo
            - ke_hoach: Kế hoạch
            - bao_cao: Báo cáo
            - to_trinh: Tờ trình
            - lenh_chi_thi: Lệnh/Chỉ thị
            - don_de_nghi: Đơn/Đề nghị
            - khac: Khác

            Nội dung: {full_text[:3000]}

            Trả lời chỉ dưới dạng JSON (không có ký tự khác):
            {{"type": "...", "confidence": 85.0}}
            """

            response = client.models.generate_content(
                model='models/gemini-2.5-flash-lite',
                contents=prompt
            )

            import json
            try:
                result = json.loads(response.text)
                return {
                    'type': result.get('type', 'khac'),
                    'confidence': result.get('confidence', 80.0)
                }
            except:
                return {'type': 'khac', 'confidence': 50.0}

        except Exception as e:
            _logger.error(f'Lỗi phân loại: {str(e)}')
            return {'type': 'khac', 'confidence': 0.0}

    def _extract_keywords(self, client, full_text):
        """
        Trích xuất từ khóa/cụm từ quan trọng từ công văn
        """
        try:
            prompt = f"""
            Trích xuất các từ khóa và cụm từ quan trọng từ công văn dưới đây.
            Chỉ trả lại danh sách từ khóa (mỗi từ trên một dòng), không giải thích.

            Nội dung: {full_text[:3000]}

            Từ khóa (mỗi từ một dòng):
            """

            response = client.models.generate_content(
                model='models/gemini-2.5-flash-lite',
                contents=prompt
            )

            keywords = response.text.strip()
            return {
                'keywords': keywords,
                'confidence': 85.0
            }

        except Exception as e:
            _logger.error(f'Lỗi trích từ khóa: {str(e)}')
            return {'keywords': '', 'confidence': 0.0}

    def _summarize_vanban(self, client, full_text):
        """
        Tóm tắt nội dung công văn thành 2-3 câu
        """
        try:
            prompt = f"""
            Tóm tắt nội dung công văn dưới đây thành 2-3 câu tiếng Việt.
            Giữ lại những thông tin chính yếu nhất.

            Nội dung: {full_text[:5000]}

            Tóm tắt:
            """

            response = client.models.generate_content(
                model='models/gemini-2.5-flash-lite',
                contents=prompt
            )

            summary = response.text.strip()
            return {
                'summary': summary,
                'confidence': 90.0
            }

        except Exception as e:
            _logger.error(f'Lỗi tóm tắt: {str(e)}')
            return {'summary': '', 'confidence': 0.0}

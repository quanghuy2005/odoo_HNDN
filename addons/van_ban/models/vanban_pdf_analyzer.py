# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

# Handle both PyPDF2 v1.x and v2.x
try:
    from PyPDF2 import PdfReader
    import io
except ImportError:
    try:
        # PyPDF2 v1.x old API
        from PyPDF2 import PdfFileReader as PdfReader
        import io
    except ImportError:
        raise UserError(_('PyPDF2 chưa cài đặt. Vui lòng chạy: pip install PyPDF2>=2.0'))

try:
    import google.generativeai as genai
except ImportError:
    genai = None

_logger = logging.getLogger(__name__)

class VanBanPdfAnalyzer(models.Model):
    """Model phân tích nội dung PDF của văn bản"""
    _name = 'vanban.pdf.analyzer'
    _description = 'Phân tích PDF Văn bản'

    # Thông tin file
    vanban_model = fields.Char(
        string='Model văn bản',
        required=True,
        help='van_ban_den hoặc van_ban_di'
    )

    vanban_id = fields.Integer(
        string='ID văn bản',
        required=True
    )

    vanban_name = fields.Char(
        string='Tên văn bản',
        readonly=True
    )

    file_data = fields.Binary(
        string='File PDF',
        required=True
    )

    file_name = fields.Char(
        string='Tên file',
        required=True
    )

    # Kết quả phân tích
    noi_dung_trich_xuat = fields.Text(
        string='Nội dung trích xuất',
        readonly=True,
        help='Toàn bộ text từ PDF'
    )

    tom_tat_ai = fields.Text(
        string='Tóm tắt (AI)',
        readonly=True,
        help='Tóm tắt được tạo bởi AI',
        store=True
    )

    tu_khoa = fields.Text(
        string='Từ khóa chính',
        readonly=True,
        help='Các từ khóa được trích xuất (dùng để categorize)'
    )

    phan_loai_tu_dong = fields.Selection([
        ('quyet_dinh', 'Quyết định'),
        ('cong_van', 'Công văn'),
        ('thong_bao', 'Thông báo'),
        ('ke_hoach', 'Kế hoạch'),
        ('bao_cao', 'Báo cáo'),
        ('to_trinh', 'Tờ trình'),
        ('khac', 'Khác'),
    ], string='Phân loại tự động', readonly=True, store=True)

    do_tin_cay = fields.Float(
        string='Độ tin cậy (%)',
        readonly=True,
        store=True,
        help='Độ tin cậy của phân loại (0-100%)'
    )

    # Audit
    ngay_phan_tich = fields.Datetime(
        string='Ngày phân tích',
        readonly=True,
        default=fields.Datetime.now
    )

    trang_thai = fields.Selection([
        ('dang_phan_tich', 'Đang phân tích'),
        ('thanh_cong', 'Thành công'),
        ('that_bai', 'Thất bại'),
    ], string='Trạng thái', default='thanh_cong', readonly=True)

    loi = fields.Text(
        string='Lỗi',
        readonly=True,
        help='Thông báo lỗi nếu phân tích thất bại'
    )

    @api.model
    def extract_text_from_pdf(self, file_data, file_name):
        """
        Trích xuất text từ file PDF
        """
        try:
            if not file_data:
                raise UserError(_('Không có dữ liệu file'))

            # Chuyển base64 about bytes
            import base64
            if isinstance(file_data, str):
                file_data = base64.b64decode(file_data)

            # Đọc PDF
            pdf_reader = PdfReader(io.BytesIO(file_data))
            text = ""
            
            # Handle both PyPDF2 v1 and v2 API
            try:
                # PyPDF2 v2.x: .pages attribute
                pages_list = pdf_reader.pages
                num_pages = len(pages_list)
            except (AttributeError, TypeError):
                # PyPDF2 v1.x: getNumPages() method
                num_pages = pdf_reader.getNumPages()
                pages_list = None
            
            # Extract text from each page
            for page_num in range(num_pages):
                try:
                    if pages_list is not None:
                        # v2.x
                        page = pages_list[page_num]
                        text += page.extract_text() + "\n"
                    else:
                        # v1.x
                        page = pdf_reader.getPage(page_num)
                        text += page.extractText() + "\n"
                except Exception as page_err:
                    _logger.warning(f'Không thể trích text trang {page_num}: {str(page_err)}')
                    continue

            return text[:5000]  # Giới hạn 5000 ký tự
        except Exception as e:
            _logger.error(f'Lỗi trích text PDF: {str(e)}')
            return f'Lỗi: {str(e)}'

    def action_phan_tich_pdf(self):
        """
        Phân tích nội dung PDF bằng AI
        """
        try:
            # Trích xuất text
            text = self.extract_text_from_pdf(self.file_data, self.file_name)

            if not text or text.startswith('Lỗi:'):
                self.write({
                    'trang_thai': 'that_bai',
                    'loi': text or 'Không thể trích xuất text'
                })
                return

            self.write({
                'noi_dung_trich_xuat': text,
                'trang_thai': 'dang_phan_tich'
            })

            # Dùng AI tóm tắt nếu có API key
            if genai:
                self._summarize_with_gemini(text)
            else:
                # Fallback: tóm tắt đơn giản
                self._simple_summarize(text)

            self.write({'trang_thai': 'thanh_cong'})

        except Exception as e:
            _logger.error(f'Lỗi phân tích PDF: {str(e)}')
            self.write({
                'trang_thai': 'that_bai',
                'loi': str(e)
            })

    def _summarize_with_gemini(self, text):
        """
        Dùng Gemini API để tóm tắt
        """
        try:
            api_key = self.env['ir.config_parameter'].sudo().get_param(
                'quan_ly_tai_lieu_ke_toa.gemini_api_key'
            )
            if not api_key:
                self._simple_summarize(text)
                return

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"""
            Vui lòng tóm tắt nội dung văn bản sau thành 3-5 câu:
            
            {text[:3000]}
            
            Tóm tắt:
            """

            response = model.generate_content(prompt)
            tom_tat = response.text if response else 'Không thể tóm tắt'

            # Phân loại văn bản
            classify_prompt = f"""
            Dựa trên nội dung, phân loại văn bản này vào một trong các loại:
            - quyet_dinh: Quyết định
            - cong_van: Công văn
            - thong_bao: Thông báo
            - ke_hoach: Kế hoạch
            - bao_cao: Báo cáo
            - to_trinh: Tờ trình
            - khac: Khác
            
            Nội dung: {text[:1000]}
            
            Trả lời chỉ với tên phân loại (không giải thích):
            """

            classify_response = model.generate_content(classify_prompt)
            phan_loai = classify_response.text.strip().lower() if classify_response else 'khac'

            # Validate phân loại
            valid_types = ['quyet_dinh', 'cong_van', 'thong_bao', 'ke_hoach', 'bao_cao', 'to_trinh', 'khac']
            if phan_loai not in valid_types:
                phan_loai = 'khac'

            self.write({
                'tom_tat_ai': tom_tat,
                'phan_loai_tu_dong': phan_loai,
                'do_tin_cay': 85.0,  # Mặc định tin cậy 85%
            })

        except Exception as e:
            _logger.error(f'Lỗi Gemini API: {str(e)}')
            self._simple_summarize(text)

    def _simple_summarize(self, text):
        """
        Tóm tắt đơn giản - lấy 3 câu đầu
        """
        sentences = text.split('.')[:3]
        tom_tat = '. '.join(sentences) + '.'
        self.write({'tom_tat_ai': tom_tat})

    @api.model
    def analyze_and_categorize(self, vanban_model, vanban_id, file_data, file_name):
        """
        Hàm helper để phân tích và categorize văn bản
        """
        try:
            vanban = self.env[vanban_model].browse(vanban_id)
            vanban_name = vanban.name if hasattr(vanban, 'name') else f'{vanban_model}#{vanban_id}'

            analyzer = self.create({
                'vanban_model': vanban_model,
                'vanban_id': vanban_id,
                'vanban_name': vanban_name,
                'file_data': file_data,
                'file_name': file_name,
            })

            analyzer.action_phan_tich_pdf()
            return analyzer

        except Exception as e:
            _logger.error(f'Lỗi phân tích văn bản: {str(e)}')
            return False

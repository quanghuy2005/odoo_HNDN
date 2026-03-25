# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import anthropic  # Claude API
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    import openai  # ChatGPT API
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class AIConfiguration(models.Model):
    """Cấu hình AI cho tóm tắt tài liệu"""
    _name = 'ai.configuration'
    _description = 'Cấu Hình AI'
    _rec_name = 'ten_config'

    ten_config = fields.Char(
        string='Tên Cấu Hình',
        required=True,
        default='AI Tóm Tắt'
    )

    loai_ai = fields.Selection([
        ('claude', 'Claude (Anthropic)'),
        ('chatgpt', 'ChatGPT (OpenAI)'),
        ('gemini', 'Google Gemini (Miễn phí)'),
    ], string='Loại AI', required=True, default='claude')

    api_key = fields.Char(
        string='API Key',
        required=True,
        help='Lấy từ: aistudio.google.com (Gemini), platform.openai.com (ChatGPT)'
    )

    model_name = fields.Char(
        string='Model Name',
        default='claude-3-sonnet-20240229',
        help='Claude: claude-3... | ChatGPT: gpt-3.5-turbo | Gemini: gemini-2.0-flash'
    )

    bat_tom_tat = fields.Boolean(
        string='Bật Tóm Tắt',
        default=True
    )

    do_dai_tom_tat = fields.Selection([
        ('ngan', 'Ngắn (2-3 câu)'),
        ('trung_binh', 'Trung Bình (5-7 câu)'),
        ('dai', 'Dài (10+ câu)'),
    ], string='Độ Dài Tóm Tắt', default='trung_binh')

    ngon_ngu = fields.Selection([
        ('vi', 'Tiếng Việt'),
        ('en', 'English'),
    ], string='Ngôn Ngữ', default='vi')

    @api.onchange('loai_ai')
    def _onchange_loai_ai(self):
        """Tự động đổi tên model mặc định khi người dùng chọn loại AI để tránh lỗi API"""
        if self.loai_ai == 'chatgpt':
            self.model_name = 'gpt-3.5-turbo'
        elif self.loai_ai == 'claude':
            self.model_name = 'claude-3-sonnet-20240229'
        elif self.loai_ai == 'gemini':
            self.model_name = 'gemini-1.5-flash'

    def test_api_connection(self):
        """Test kết nối API"""
        try:
            if self.loai_ai == 'claude':
                return self._test_claude()
            elif self.loai_ai == 'gemini':
                return self._test_gemini()
            else:
                return self._test_chatgpt()
        except Exception as e:
            raise UserError(f'Lỗi API: {str(e)}')

    def _test_claude(self):
        """Test Claude API"""
        if not CLAUDE_AVAILABLE:
            raise UserError('Cần cài đặt: pip install anthropic')

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model_name,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Xin chào, hãy nói lời chào."}
                ]
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành Công!',
                    'message': f'Claude API Connected: {message.content[0].text}',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(f'Claude API Error: {str(e)}')

    def _test_chatgpt(self):
        """Test ChatGPT API"""
        if not OPENAI_AVAILABLE:
            raise UserError('Cần cài đặt: pip install openai')

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": "Xin chào, hãy nói lời chào."}
                ],
                max_tokens=100
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành Công!',
                    'message': f'ChatGPT API Connected',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(f'ChatGPT API Error: {str(e)}')

    def _test_gemini(self):
        """Test Gemini API"""
        if not GEMINI_AVAILABLE:
            raise UserError('Cần cài đặt: pip install google-genai')

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model_name or 'models/gemini-2.5-flash-lite',
                contents="Xin chào, hãy nói lời chào."
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành Công!',
                    'message': f'Gemini API Connected: {response.text[:80]}',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(f'Gemini API Error: {str(e)}')

    def tom_tat_noi_dung(self, noi_dung):
        """Tóm tắt nội dung bằng AI"""
        if not self.bat_tom_tat or not noi_dung:
            return None

        prompt = self._tao_prompt_tom_tat(noi_dung)

        try:
            if self.loai_ai == 'claude':
                return self._tom_tat_claude(prompt)
            elif self.loai_ai == 'gemini':
                return self._tom_tat_gemini(prompt)
            else:
                return self._tom_tat_chatgpt(prompt)
        except Exception as e:
            print(f'AI Summarization Error: {e}')
            return None

    def _tao_prompt_tom_tat(self, noi_dung):
        """Tạo prompt cho tóm tắt"""
        do_dai_map = {
            'ngan': '2-3 câu',
            'trung_binh': '5-7 câu',
            'dai': '10+ câu'
        }
        
        do_dai = do_dai_map.get(self.do_dai_tom_tat, '5-7 câu')
        
        if self.ngon_ngu == 'vi':
            return f"""Hãy tóm tắt nội dung sau bằng tiếng Việt trong {do_dai}:

{noi_dung}

Tóm tắt:"""
        else:
            return f"""Please summarize the following content in {do_dai} sentences in English:

{noi_dung}

Summary:"""

    def _tom_tat_claude(self, prompt):
        """Tóm tắt bằng Claude"""
        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model_name,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def _tom_tat_chatgpt(self, prompt):
        """Tóm tắt bằng ChatGPT"""
        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

    def _tom_tat_gemini(self, prompt):
        """Tóm tắt bằng Gemini"""
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_name or 'models/gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text

    def phan_loai_tai_lieu(self, noi_dung):
        """Gợi ý loại tài liệu dựa trên nội dung"""
        prompt = f"""Dựa vào nội dung tài liệu sau, hãy gợi ý loại tài liệu phù hợp nhất.
Chỉ trả về một trong các loại này: Hợp Đồng, Báo Giá, Hóa Đơn, Giấy Phép, Báo Cáo, Biên Bản, hoặc Khác.

Nội dung:
{noi_dung[:500]}

Loại tài liệu gợi ý:"""

        try:
            if self.loai_ai == 'claude':
                return self._tom_tat_claude(prompt)
            elif self.loai_ai == 'gemini':
                return self._tom_tat_gemini(prompt)
            else:
                return self._tom_tat_chatgpt(prompt)
        except Exception as e:
            print(f'AI Classification Error: {e}')
            return None

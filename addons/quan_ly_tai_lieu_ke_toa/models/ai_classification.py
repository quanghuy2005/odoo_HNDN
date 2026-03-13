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
    ], string='Loại AI', required=True, default='claude')

    api_key = fields.Char(
        string='API Key',
        required=True,
        help='Lấy từ: https://console.anthropic.com (Claude) hoặc https://platform.openai.com (ChatGPT)'
    )

    model_name = fields.Char(
        string='Model Name',
        default='claude-3-sonnet-20240229',
        help='Claude: claude-3-sonnet-... | ChatGPT: gpt-4, gpt-3.5-turbo'
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

    def test_api_connection(self):
        """Test kết nối API"""
        try:
            if self.loai_ai == 'claude':
                return self._test_claude()
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
            openai.api_key = self.api_key
            response = openai.ChatCompletion.create(
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

    def tom_tat_noi_dung(self, noi_dung):
        """Tóm tắt nội dung bằng AI"""
        if not self.bat_tom_tat or not noi_dung:
            return None

        prompt = self._tao_prompt_tom_tat(noi_dung)

        try:
            if self.loai_ai == 'claude':
                return self._tom_tat_claude(prompt)
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
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

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
            else:
                return self._tom_tat_chatgpt(prompt)
        except Exception as e:
            print(f'AI Classification Error: {e}')
            return None

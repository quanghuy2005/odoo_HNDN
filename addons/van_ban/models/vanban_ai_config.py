# -*- coding: utf-8 -*-
from odoo import models, fields

class VanBanAIConfig(models.Model):
    _name = 'vanban.ai.config'
    _description = 'Cấu Hình AI cho Văn Bản'
    _rec_name = 'name'

    name = fields.Char(string='Tên Cấu Hình', default='Google Gemini API', required=True)
    api_key = fields.Char(string='API Key', required=True, help='Nhập API Key từ Google AI Studio')
    is_active = fields.Boolean(string='Kích hoạt', default=True)

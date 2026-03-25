# -*- coding: utf-8 -*-
from odoo import models, fields

class VanBanPDFAnalyzer(models.Model):
    """Placeholder model - kept for backward compatibility with old database records"""
    _name = 'vanban.pdf.analyzer'
    _description = 'PDF Analyzer (Deprecated)'
    
    # Minimal fields to keep old records working
    name = fields.Char(string='Name')
    trang_thai = fields.Selection([
        ('cho', 'Waiting'),
        ('dang_xu_ly', 'Processing'),
        ('thanh_cong', 'Success'),
        ('that_bai', 'Failed'),
    ], string='Status', default='cho')

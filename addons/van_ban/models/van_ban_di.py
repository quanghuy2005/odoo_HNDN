# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Văn bản đi'
    
    company_id = fields.Many2one('res.company', string='Công ty', 
        default=lambda self: self.env.company)
    
    name = fields.Char(string='Số văn bản', required=True)
    trich_yeu = fields.Text(string='Trích yếu', required=True)
    ngay_van_ban = fields.Date(string='Ngày văn bản', default=fields.Date.today)
    ngay_gui = fields.Date(string='Ngày gửi', default=fields.Date.today)
    so_di = fields.Char(string='Số đi')
    noi_nhan = fields.Text(string='Nơi nhận')
    nguoi_ky = fields.Char(string='Người ký')
    loai_van_ban = fields.Selection([
        ('quyet_dinh', 'Quyết định'),
        ('cong_van', 'Công văn'),
        ('thong_bao', 'Thông báo'),
        ('ke_hoach', 'Kế hoạch'),
        ('bao_cao', 'Báo cáo'),
        ('to_trinh', 'Tờ trình'),
        ('khac', 'Khác'),
    ], string='Loại văn bản', default='cong_van')
    do_khan = fields.Selection([
        ('thuong', 'Thường'),
        ('khan', 'Khẩn'),
        ('hoa_toc', 'Hỏa tốc'),
    ], string='Độ khẩn', default='thuong')
    do_mat = fields.Selection([
        ('binh_thuong', 'Bình thường'),
        ('mat', 'Mật'),
        ('tuyet_mat', 'Tuyệt mật'),
    ], string='Độ mật', default='binh_thuong')
    trang_thai = fields.Selection([
        ('du_thao', 'Dự thảo'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('da_gui', 'Đã gửi'),
    ], string='Trạng thái', default='du_thao')
    file_dinh_kem = fields.Binary(string='File đính kèm')
    file_name = fields.Char(string='Tên file')
    
    # ===== AI FIELDS =====
    ai_processor_id = fields.Many2one(
        'vanban.ai.processor',
        string='Xử lý AI',
        readonly=True,
        help='Link tới kết quả xử lý AI'
    )
    
    phan_loai_ai = fields.Selection([
        ('quyet_dinh', 'Quyết định'),
        ('cong_van', 'Công văn'),
        ('thong_bao', 'Thông báo'),
        ('ke_hoach', 'Kế hoạch'),
        ('bao_cao', 'Báo cáo'),
        ('to_trinh', 'Tờ trình'),
        ('lenh_chi_thi', 'Lệnh/Chỉ thị'),
        ('don_de_nghi', 'Đơn/Đề nghị'),
        ('khac', 'Khác'),
    ], string='Phân loại AI', readonly=True, compute='_compute_ai_fields', store=True)
    
    tu_khoa_ai = fields.Text(
        string='Từ khóa AI',
        readonly=True,
        compute='_compute_ai_fields',
        store=True,
        help='Từ khóa được trích xuất bởi AI'
    )
    
    tom_tat_ai = fields.Text(
        string='Tóm tắt AI',
        readonly=True,
        compute='_compute_ai_fields',
        store=True,
        help='Tóm tắt được tạo bởi AI'
    )
    
    do_tin_cay_ai = fields.Float(
        string='Độ tin cậy AI (%)',
        readonly=True,
        compute='_compute_ai_fields',
        store=True
    )
    
    @api.depends('ai_processor_id')
    def _compute_ai_fields(self):
        """Lấy dữ liệu AI từ ai_processor_id"""
        for record in self:
            if record.ai_processor_id:
                record.phan_loai_ai = record.ai_processor_id.phan_loai
                record.tu_khoa_ai = record.ai_processor_id.tu_khoa
                record.tom_tat_ai = record.ai_processor_id.tom_tat
                record.do_tin_cay_ai = (
                    record.ai_processor_id.do_tin_cay_phan_loai +
                    record.ai_processor_id.do_tin_cay_tu_khoa +
                    record.ai_processor_id.do_tin_cay_tom_tat
                ) / 3
            else:
                record.phan_loai_ai = False
                record.tu_khoa_ai = False
                record.tom_tat_ai = False
                record.do_tin_cay_ai = 0.0
    
    def action_xu_ly_ai(self):
        """Tạo request xử lý AI cho văn bản này"""
        # Tạo vanban_ai_processor record
        ai_processor = self.env['vanban.ai.processor'].create({
            'vanban_model': 'van_ban_di',
            'vanban_id': self.id,
            'vanban_name': self.name,
            'noi_dung_cong_van': self.trich_yeu or '',
        })
        
        # Link tới van_ban_di
        self.ai_processor_id = ai_processor.id
        
        # Trigger xử lý AI
        ai_processor.action_xu_ly_ai()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vanban.ai.processor',
            'res_id': ai_processor.id,
            'view_mode': 'form',
            'target': 'current',
        } 
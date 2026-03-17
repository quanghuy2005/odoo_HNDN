# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CrmLeadMoRong(models.Model):
    _inherit = 'crm.lead'

    def action_tao_tai_lieu_hop_dong(self):
        """Nút tạo nhanh Hợp đồng/Báo giá từ CRM Lead"""
        self.ensure_one()
        if 'tai_lieu.ke_toa' not in self.env:
            raise UserError(_('Vui lòng cài đặt module "Quản lý Tài Liệu" để sử dụng tính năng này.'))
            
        if not self.partner_id:
            raise UserError(_('Vui lòng chọn Khách hàng (Customer) cho Cơ hội này trước khi tạo tài liệu.'))
            
        # Lấy nhân viên an toàn hơn (phòng trường hợp user không có employee)
        nhan_vien_id = False
        if self.user_id and hasattr(self.user_id, 'employee_id') and self.user_id.employee_id:
            nhan_vien_id = self.user_id.employee_id.id

        tai_lieu = self.env['tai_lieu.ke_toa'].create({
            'ten_tai_lieu': f'Báo giá/Hợp đồng cho: {self.name}',
            'khach_hang': self.partner_id.id,
            'nhan_vien_phu_trach': nhan_vien_id,
            'loai_tai_lieu': 'bao_gia',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tai_lieu.ke_toa',
            'res_id': tai_lieu.id,
            'view_mode': 'form',
        }
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class NhanVienMoRongTaiLieu(models.Model):
    """Mở rộng nhân viên cho module tài liệu"""
    _inherit = 'hr.employee'

    # One2many: Danh sách tài liệu nhân viên phụ trách
    danh_sach_tai_lieu = fields.One2many(
        'tai_lieu.ke_toa',
        'nhan_vien_phu_trach',
        string='Danh Sách Tài Liệu Phụ Trách',
        readonly=True
    )

    # Computed field
    so_tai_lieu = fields.Integer(
        string='Số Tài Liệu',
        compute='_tinh_so_tai_lieu',
        store=True
    )
    
    so_hop_dong_chot = fields.Integer(
        string='Số Hợp Đồng Đã Ký',
        compute='_tinh_kpi_hop_dong',
        store=True
    )
    
    tong_doanh_thu_mang_ve = fields.Float(
        string='Tổng Doanh Thu (VND)',
        compute='_tinh_kpi_hop_dong',
        store=True
    )

    @api.depends('danh_sach_tai_lieu', 'danh_sach_tai_lieu.trang_thai', 'danh_sach_tai_lieu.gia_tri_tai_lieu')
    def _tinh_so_tai_lieu(self):
        """Tính số lượng tài liệu chung"""
        for nv in self:
            nv.so_tai_lieu = len(nv.danh_sach_tai_lieu)
            
    @api.depends('danh_sach_tai_lieu', 'danh_sach_tai_lieu.trang_thai', 'danh_sach_tai_lieu.gia_tri_tai_lieu')
    def _tinh_kpi_hop_dong(self):
        """Tính toán KPI hợp đồng đã hoàn tất của nhân viên"""
        for nv in self:
            # Chỉ tính những Hợp đồng/Báo giá đã ký hoặc hoàn tất
            hop_dong_thanh_cong = nv.danh_sach_tai_lieu.filtered(
                lambda t: t.loai_tai_lieu in ['hop_dong', 'bao_gia'] and t.trang_thai in ['da_ky', 'hoan_tat']
            )
            nv.so_hop_dong_chot = len(hop_dong_thanh_cong)
            nv.tong_doanh_thu_mang_ve = sum(hop_dong_thanh_cong.mapped('gia_tri_tai_lieu'))

    def write(self, vals):
        """Ghi đè hàm write để xử lý logic khi nhân viên nghỉ việc (Archive)"""
        res = super().write(vals)
        # Nếu trường 'active' được set thành False (Nghỉ việc/Lưu trữ)
        if 'active' in vals and not vals.get('active'):
            for employee in self:
                # Tìm các tài liệu đang mở của nhân viên này
                open_documents = self.env['tai_lieu.ke_toa'].search([
                    ('nhan_vien_phu_trach', '=', employee.id),
                    ('trang_thai', 'not in', ['hoan_tat', 'het_han', 'huy'])
                ])
                if not open_documents:
                    continue

                # 1. Ưu tiên chuyển cho quản lý trực tiếp của nhân viên
                target_employee = employee.parent_id

                # 2. Nếu không có quản lý, tìm một người trong nhóm Quản lý (base.group_user)
                if not target_employee:
                    manager_user = self.env['res.users'].search([
                        ('groups_id', 'in', self.env.ref('base.group_user').id),
                        ('employee_id', '!=', False),
                        ('active', '=', True)
                    ], limit=1)
                    if manager_user:
                        target_employee = manager_user.employee_id

                if target_employee:
                    open_documents.write({'nhan_vien_phu_trach': target_employee.id})
                    for doc in open_documents:
                        body = _("Tự động chuyển giao phụ trách từ <b>%s</b> sang <b>%s</b> do nhân viên được lưu trữ.") % (employee.name, target_employee.name)
                        doc.message_post(body=body)
                else:
                    # 3. Nếu vẫn không tìm được ai, tạo một activity để admin xử lý thủ công
                    for doc in open_documents:
                        doc.activity_schedule(
                            'mail.activity_data_todo',
                            summary=_('Phân công lại tài liệu'),
                            note=_('Nhân viên phụ trách %s đã được lưu trữ. Vui lòng phân công người phụ trách mới.') % employee.name,
                            user_id=self.env.ref('base.user_admin').id
                        )
        return res

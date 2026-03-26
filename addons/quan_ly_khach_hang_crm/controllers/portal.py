# -*- coding: utf-8 -*-
from odoo import http, _, fields
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request

class KhachHangPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(KhachHangPortal, self)._prepare_home_portal_values(counters)
        
        partner = request.env.user.partner_id.commercial_partner_id
        
        # Đếm số lượng Hợp đồng kế toán và Hồ sơ hành chính
        if 'hop_dong_count' in counters:
            if 'tai_lieu.ke_toa' in request.env:
                values['hop_dong_count'] = request.env['tai_lieu.ke_toa'].sudo().search_count([('khach_hang', 'child_of', partner.id)])
            else:
                values['hop_dong_count'] = 0
            
        if 'ho_so_count' in counters:
            if 'ho_so_van_ban' in request.env:
                values['ho_so_count'] = request.env['ho_so_van_ban'].sudo().search_count([('khach_hang_id', 'child_of', partner.id)])
            else:
                values['ho_so_count'] = 0
            
        return values

    @http.route(['/my/hop_dong', '/my/hop_dong/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_hop_dong(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id.commercial_partner_id
        
        if 'tai_lieu.ke_toa' not in request.env:
            return request.redirect('/my')
            
        TaiLieu = request.env['tai_lieu.ke_toa'].sudo()

        domain = [('khach_hang', 'child_of', partner.id)]
        hop_dong_count = TaiLieu.search_count(domain)

        pager = portal_pager(
            url="/my/hop_dong",
            total=hop_dong_count,
            page=page,
            step=10
        )

        hop_dongs = TaiLieu.search(domain, limit=10, offset=pager['offset'])

        values.update({
            'hop_dongs': hop_dongs,
            'page_name': 'hop_dong',
            'pager': pager,
            'default_url': '/my/hop_dong',
        })
        return request.render("quan_ly_khach_hang_crm.portal_my_hop_dong_list", values)

    @http.route(['/my/ho_so', '/my/ho_so/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_ho_so(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id.commercial_partner_id
        
        if 'ho_so_van_ban' not in request.env:
            return request.redirect('/my')
            
        HoSo = request.env['ho_so_van_ban'].sudo()

        domain = [('khach_hang_id', 'child_of', partner.id)]
        ho_so_count = HoSo.search_count(domain)

        pager = portal_pager(
            url="/my/ho_so",
            total=ho_so_count,
            page=page,
            step=10
        )

        ho_sos = HoSo.search(domain, limit=10, offset=pager['offset'])

        values.update({
            'ho_sos': ho_sos,
            'page_name': 'ho_so_van_ban',
            'pager': pager,
            'default_url': '/my/ho_so',
        })
        return request.render("quan_ly_khach_hang_crm.portal_my_ho_so_list", values)

    @http.route(['/my/hop_dong/ky/<model("tai_lieu.ke_toa"):hop_dong>'], type='http', auth="user", website=True)
    def portal_my_hop_dong_ky(self, hop_dong, **kw):
        """Hiển thị trang Vẽ chữ ký cho 1 Hợp đồng cụ thể"""
        if 'tai_lieu.ke_toa' not in request.env:
            return request.redirect('/my')
            
        # Kiểm tra quyền tự nhiên: Chỉ cho phép ký nếu đúng là Hợp đồng của đối tác đang đăng nhập
        if hop_dong.khach_hang.commercial_partner_id.id != request.env.user.partner_id.commercial_partner_id.id:
            return request.redirect('/my/hop_dong')
            
        values = self._prepare_portal_layout_values()
        values.update({
            'hop_dong': hop_dong,
            'page_name': 'ky_hop_dong',
        })
        return request.render("quan_ly_khach_hang_crm.portal_my_hop_dong_ky", values)

    @http.route(['/my/hop_dong/luu_chu_ky'], type='json', auth="user", methods=['POST'], website=True)
    def portal_my_hop_dong_luu_chu_ky(self, doc_id, signature, **kw):
        """API nhận luồng dội về Base64 Ảnh chữ ký từ trình duyệt và Lưu vào Database Odoo"""
        if 'tai_lieu.ke_toa' not in request.env:
            return {'error': 'Hệ thống tài liệu chưa được cài đặt.'}
            
        hop_dong = request.env['tai_lieu.ke_toa'].sudo().browse(int(doc_id))
        
        # Validation
        if not hop_dong.exists() or hop_dong.khach_hang.commercial_partner_id.id != request.env.user.partner_id.commercial_partner_id.id:
            return {'error': 'Không có quyền truy cập hợp đồng này.'}
            
        if hop_dong.chu_ky_khach_hang or hop_dong.trang_thai in ['hoan_tat', 'het_han', 'huy']:
            return {'error': 'Hợp đồng này đã đóng hoặc bạn đã ký rồi, không thể ký lại.'}

        # Validate signature data format (base64 image headers)
        if not signature or 'data:image' not in signature:
            return {'error': 'Dữ liệu chữ ký không hợp lệ.'}

        try:
            # Tách lấy thuật toán Base64 từ đoạn mã Data URL (VD: data:image/png;base64,iVBORw0KGgo...)
            signature_data = signature.split(',')[1]
            
            # 1. Lưu CSDL Chữ ký ảnh
            hop_dong.write({
                'chu_ky_khach_hang': signature_data,
                'ngay_khach_ky': fields.Datetime.now(),
                'co_yeu_cau_ky': True, # Cập nhật cờ để tính toán trạng thái ký đúng
            })
            
            # 2. Tạo bản ghi Tracking ở bảng Phân Tích (Ký Điện Tử)
            request.env['tai_lieu.ky_digital'].sudo().create({
                'tai_lieu': hop_dong.id,
                'khach_hang_ky': hop_dong.khach_hang.id,
                'user_ky': request.env.user.id,
                'email_ky': request.env.user.partner_id.email,
                'trang_thai_ky': 'da_ky'
            })

            # 3. TỰ ĐỘNG CHUYỂN TRẠNG THÁI THEO YÊU CẦU CỦA GIÁM ĐỐC
            if hop_dong.trang_thai == 'da_ky':
                # Nếu Admin đã ký Nội bộ xong r, Khách chốt Ký cuối -> Tự Tự đóng Hợp đồng (Hoàn Tất) và Xuất Hóa Đơn luôn!
                hop_dong.hanh_dong_hoan_tat()
            elif hop_dong.trang_thai == 'da_phe_duyet':
                # Nếu Khách lanh chanh ký trước khi Admin ký mộc, tiến Hợp đồng lên 1 nấc "Đã Ký" chờ Admin ấn Hoàn Tất
                hop_dong.write({'trang_thai': 'da_ky', 'da_ky': True})
            
            # Báo về Chatter hệ thống để Giám đốc biết Khách vừa ký
            tgs = fields.Datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            hop_dong.message_post(body=f"✍️ <b>KHÁCH HÀNG ĐÃ KÝ ĐIỆN TỬ</b> qua Web Portal lúc {tgs}")
            
            return {'success': True}
        except Exception as e:
            return {'error': str(e)}

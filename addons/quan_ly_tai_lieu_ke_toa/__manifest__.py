# -*- coding: utf-8 -*-
{
    'name': 'Quản Lý Tài Liệu Kế Toán',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Documents',
    'author': 'Quang Developer',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'attachment_indexation',
        'hr',
        'quan_ly_khach_hang_crm',
        'quan_ly_nhan_su_mo_rong',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/tao_day_chu.xml',
        'data/email_template.xml',
        'data/automation.xml',
        'views/tai_lieu_view.xml',
        'views/phieu_phe_duyet_view.xml',
        'views/dinh_kem_file_view.xml',
        'views/nhan_vien_view.xml',
        'views/external_api_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 3,
    'summary': 'Quản lý tài liệu khách hàng, phê duyệt đa cấp, số hóa hồ sơ',
    'description': '''
    Hệ thống quản lý tài liệu tập trung:
    - Tạo, quản lý, phê duyệt tài liệu
    - Upload và lưu trữ file
    - Quy trình phê duyệt đa cấp
    - Số hóa hồ sơ khách hàng
    - Tích hợp email thông báo
    - Tracking version và lịch sử
    - Google Drive Backup tự động
    - AI Tóm Tắt & Phân Loại
    ''',
    'external_dependencies': {
        'python': ['anthropic', 'google-auth-httplib2', 'google-auth-oauthlib', 'openai'],
    },
}

# -*- coding: utf-8 -*-
{
    'name': 'Quản Lý Nhân Sự Mở Rộng',
    'version': '15.0.1.0.0',
    'category': 'Human Resources',
    'author': 'Quang Developer',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'quan_ly_khach_hang_crm',
    ],
    'data': [
        'views/nhan_vien_mo_rong.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 2,
    'summary': 'Mở rộng quản lý nhân sự: khách hàng phụ trách, tài liệu liên kết',
    'external_dependencies': {},
}

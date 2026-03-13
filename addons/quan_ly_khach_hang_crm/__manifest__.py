# -*- coding: utf-8 -*-
{
    'name': 'Quản Lý Khách Hàng CRM',
    'version': '15.0.1.0.0',
    'category': 'CRM',
    'author': 'Quang Developer',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'contacts',
    ],
    'data': [
        'views/trang_web_khach_hang.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
    'summary': 'Quản lý thông tin khách hàng, tiềm năng kinh doanh, lịch sử giao dịch',
}

{
    'name': 'Customer Document Management',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summary': 'Manage contracts, quotations, and legal documents for customers',
    'description': """
        Customer Document Management System
        ====================================
        
        This module helps you:
        - Manage customer contracts, quotations, and legal documents
        - Link documents to customers and responsible employees
        - Version control and approval workflows
        - Electronic signature support
        - Full-text search in documents
        - Email documents to customers
        
        Integrates with CRM and HR modules.
    """,
    'author': 'Your Company',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'hr',
        'mail',
        'attachment_indexation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/customer_document_view.xml',
        'views/document_approval_view.xml',
        'views/customer_document_attachment_view.xml',
        'views/hr_employee_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

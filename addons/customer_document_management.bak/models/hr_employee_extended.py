from odoo import models, fields


class HrEmployeeExtended(models.Model):
    _inherit = 'hr.employee'

    customer_ids = fields.Many2many(
        'res.partner',
        'hr_employee_customer_rel',
        'employee_id',
        'customer_id',
        string='Customers Managed',
        domain="[('customer_rank', '>', 0)]"
    )

    document_ids = fields.One2many(
        'customer.document',
        'employee_id',
        string='Managed Documents'
    )

    document_count = fields.Integer(
        'Number of Documents',
        compute='_compute_document_count'
    )

    def _compute_document_count(self):
        for emp in self:
            emp.document_count = len(emp.document_ids)

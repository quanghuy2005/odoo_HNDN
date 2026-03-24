from odoo import models, fields, api
from datetime import datetime


class DocumentApproval(models.Model):
    _name = 'document.approval'
    _description = 'Document Approval Process'
    _order = 'create_date DESC'

    document_id = fields.Many2one(
        'customer.document',
        string='Document',
        required=True,
        ondelete='cascade'
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True
    )

    approver_email = fields.Char(
        related='approver_id.email',
        readonly=True
    )

    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('skipped', 'Skipped'),
        ],
        string='Status',
        default='pending',
        tracking=True
    )

    comment = fields.Text('Approval Comment')
    
    approval_date = fields.Datetime('Approval Date', readonly=True)
    
    sequence = fields.Integer('Sequence', default=1)

    def action_approve(self):
        """Approve document"""
        self.write({
            'state': 'approved',
            'approval_date': datetime.now()
        })
        self.document_id.message_post(
            body=f'Document approved by {self.approver_id.name}'
        )

    def action_reject(self):
        """Reject document"""
        self.write({'state': 'rejected'})
        self.document_id.write({'state': 'draft'})
        self.document_id.message_post(
            body=f'Document rejected by {self.approver_id.name}. Comment: {self.comment}'
        )

    def action_skip(self):
        """Skip this approval"""
        self.write({'state': 'skipped'})

    def send_approval_notification(self):
        """Send approval notification to approver"""
        template = self.env.ref(
            'customer_document_management.email_approval_request',
            False
        )
        if template:
            template.send_mail(self.id)

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class CustomerDocument(models.Model):
    _name = 'customer.document'
    _description = 'Customer Document Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date DESC'

    # Basic Information
    name = fields.Char('Document Name', required=True, tracking=True)
    reference = fields.Char('Reference Code', readonly=True, copy=False)
    description = fields.Text('Description')
    
    # Document Type
    document_type = fields.Selection(
        [
            ('contract', 'Contract'),
            ('quotation', 'Quotation'),
            ('legal', 'Legal Document'),
            ('invoice', 'Invoice'),
            ('other', 'Other'),
        ],
        string='Document Type',
        required=True,
        tracking=True
    )
    
    # Customer Information
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        domain="[('customer_rank', '>', 0)]"
    )
    
    # Responsible Employee
    employee_id = fields.Many2one(
        'hr.employee',
        string='Responsible Employee',
        tracking=True
    )
    
    # Dates
    issue_date = fields.Date('Issue Date', default=fields.Date.today, tracking=True)
    effective_date = fields.Date('Effective Date', tracking=True)
    expiry_date = fields.Date('Expiry Date', tracking=True)
    
    # Status Fields
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('signed', 'Signed'),
            ('completed', 'Completed'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True
    )
    
    # Approval Fields
    approval_required = fields.Boolean('Approval Required', default=True)
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )
    approval_date = fields.Datetime('Approval Date', readonly=True)
    
    # Signature Fields
    signature_required = fields.Boolean('Signature Required', default=True)
    signed = fields.Boolean('Signed', readonly=True, default=False)
    signed_date = fields.Datetime('Signed Date', readonly=True)
    signed_by = fields.Char('Signed By', readonly=True)
    
    # Version Control
    document_version = fields.Integer('Version', default=1, readonly=True)
    parent_document_id = fields.Many2one(
        'customer.document',
        string='Previous Version',
        readonly=True
    )
    version_ids = fields.One2many(
        'customer.document',
        'parent_document_id',
        string='Document Versions'
    )
    
    # Attachment
    attachment_ids = fields.One2many(
        'customer.document.attachment',
        'document_id',
        string='Attachments'
    )
    main_attachment_id = fields.Many2one(
        'customer.document.attachment',
        string='Main File'
    )
    
    # Approval Process
    approval_ids = fields.One2many(
        'document.approval',
        'document_id',
        string='Approvals'
    )
    
    # Tags for Search
    tag_ids = fields.Many2many(
        'customer.document.tag',
        string='Tags'
    )
    
    # Content for Full-text Search
    content_search = fields.Text(
        'Searchable Content',
        compute='_compute_content_search',
        store=True
    )
    
    # Statistics
    attachment_count = fields.Integer(
        'Number of Attachments',
        compute='_compute_attachment_count'
    )
    approval_count = fields.Integer(
        'Number of Approvals',
        compute='_compute_approval_count'
    )
    
    # Notes
    notes = fields.Text('Internal Notes')
    
    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 'Reference Code must be unique!'),
    ]

    @api.model
    def create(self, vals):
        if not vals.get('reference'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('customer.document.seq')
        return super().create(vals)

    @api.depends('name', 'description', 'partner_id', 'employee_id', 'attachment_ids')
    def _compute_content_search(self):
        """Compute full-text search content"""
        for record in self:
            content = []
            content.append(record.name or '')
            content.append(record.description or '')
            content.append(record.partner_id.name or '')
            content.append(record.employee_id.name or '')
            for att in record.attachment_ids:
                content.append(att.name or '')
            record.content_search = ' '.join(content).lower()

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = len(record.attachment_ids)

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_submit(self):
        """Submit document for review"""
        if self.state != 'draft':
            raise ValidationError('Only draft documents can be submitted!')
        self.write({'state': 'submitted'})
        self.send_notification('Document submitted for review')

    def action_request_approval(self):
        """Request approval from specified approvers"""
        if not self.approval_required:
            raise ValidationError('This document does not require approval!')
        if not self.approval_ids:
            raise ValidationError('Please add approvers before requesting approval!')
        self.write({'state': 'under_review'})
        self.send_approval_requests()

    def action_approve(self):
        """Approve document"""
        if self.state not in ['submitted', 'under_review']:
            raise ValidationError('Only submitted documents can be approved!')
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': datetime.now()
        })
        self.send_notification('Document approved')

    def action_sign(self):
        """Mark document as signed"""
        if not self.signature_required:
            self.action_complete()
        else:
            if self.state not in ['approved', 'submitted']:
                raise ValidationError('Only approved documents can be signed!')
            self.write({
                'state': 'signed',
                'signed': True,
                'signed_date': datetime.now(),
                'signed_by': self.env.user.partner_id.name
            })
            self.send_notification('Document signed')

    def action_complete(self):
        """Mark document as completed"""
        self.write({'state': 'completed'})
        self.send_notification('Document completed')

    def action_cancel(self):
        """Cancel document"""
        self.write({'state': 'cancelled'})
        self.send_notification('Document cancelled')

    def action_create_new_version(self):
        """Create new version of document"""
        new_doc = self.copy()
        new_doc.write({
            'parent_document_id': self.id,
            'document_version': self.document_version + 1,
            'state': 'draft'
        })
        return new_doc

    def send_notification(self, message):
        """Send internal notification"""
        self.message_post(body=message)

    def send_approval_requests(self):
        """Send approval requests to approvers"""
        for approval in self.approval_ids:
            approval.send_approval_notification()

    def action_send_to_customer(self):
        """Send document to customer via email"""
        template = self.env.ref('customer_document_management.email_document_template', False)
        if not template:
            raise ValidationError('Email template not found!')
        return template.send_mail(self.id)

    @api.constrains('expiry_date', 'issue_date')
    def _check_dates(self):
        for record in self:
            if record.expiry_date and record.issue_date and record.expiry_date < record.issue_date:
                raise ValidationError('Expiry date must be after issue date!')

    def _check_expiry(self):
        """Check and update expiry status (called via cron)"""
        today = fields.Date.today()
        expired_docs = self.search([('expiry_date', '<', today), ('state', '!=', 'expired')])
        for doc in expired_docs:
            doc.write({'state': 'expired'})

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Enhance search with full-text search support"""
        # Support searching in content_search field
        return super().search(args, offset=offset, limit=limit, order=order, count=count)


class CustomerDocumentTag(models.Model):
    _name = 'customer.document.tag'
    _description = 'Customer Document Tag'

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!'),
    ]

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomerDocumentAttachment(models.Model):
    _name = 'customer.document.attachment'
    _description = 'Customer Document Attachment'
    _order = 'sequence, create_date DESC'

    document_id = fields.Many2one(
        'customer.document',
        string='Document',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char('File Name', required=True)

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='File',
        required=True,
        ondelete='cascade'
    )

    file_size = fields.Integer(
        'File Size (bytes)',
        related='attachment_id.file_size',
        readonly=True
    )

    file_type = fields.Char(
        'File Type',
        compute='_compute_file_type',
        store=True
    )

    description = fields.Text('Description')

    version = fields.Integer('Version', default=1)

    is_main_file = fields.Boolean('Is Main File', default=False)

    uploaded_by = fields.Many2one(
        'res.users',
        string='Uploaded By',
        default=lambda self: self.env.user,
        readonly=True
    )

    upload_date = fields.Datetime(
        'Upload Date',
        default=fields.Datetime.now,
        readonly=True
    )

    sequence = fields.Integer('Sequence', default=1)

    @api.depends('attachment_id.name')
    def _compute_file_type(self):
        for record in self:
            if record.attachment_id:
                filename = record.attachment_id.name
                record.file_type = filename.split('.')[-1].upper() if '.' in filename else 'Unknown'
            else:
                record.file_type = 'Unknown'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        # If this is the first attachment, mark it as main file
        if len(record.document_id.attachment_ids) == 1:
            record.write({'is_main_file': True})
            record.document_id.write({'main_attachment_id': record.id})
        return record

    def button_download(self):
        """Download attachment"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.attachment_id.id,
            'target': 'new',
        }

    def action_set_as_main(self):
        """Set this attachment as main file"""
        # Unset previous main file
        for att in self.document_id.attachment_ids:
            if att.is_main_file:
                att.write({'is_main_file': False})
        
        # Set this as main
        self.write({'is_main_file': True})
        self.document_id.write({'main_attachment_id': self.id})

    def action_new_version(self):
        """Create new version of this attachment"""
        new_version = self.copy()
        new_version.write({
            'version': self.version + 1
        })
        return new_version

    def get_file_content(self):
        """Get file content"""
        return self.attachment_id.datas

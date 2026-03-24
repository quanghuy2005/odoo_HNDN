# Customer Document Management Module

## Overview
**Customer Document Management** is an Odoo 15 module designed to manage customer-related documents including contracts, quotations, legal documents, and invoices. It integrates seamlessly with HR (Human Resources) and CRM modules for comprehensive document lifecycle management.

## Features

### 📄 Document Management
- **Multiple Document Types**: Support for contracts, quotations, legal documents, invoices, and custom types
- **Document Versioning**: Keep track of all document versions with full history
- **Attachment Management**: Upload, download, and organize multiple files per document
- **Full-Text Search**: Search documents by content, metadata, and related information

### 👥 Employee Integration (HR)
- **Responsibility Assignment**: Link documents to responsible employees
- **Customer Management**: Employees can manage multiple customers
- **Document Tracking**: View all documents managed by each employee
- **Permission Control**: Role-based access control (Sales User, Manager, HR User)

### ✅ Approval Workflow
- **Multi-Step Approval**: Configure multiple approvers with sequence
- **Status Tracking**: Track approval status (Pending, Approved, Rejected, Skipped)
- **Comments**: Add approval comments and feedback
- **Notifications**: Automatic email notifications to approvers

### 🖊️ Signature Management
- **Signature Tracking**: Record who signed the document and when
- **Signature Status**: Track signature status separately from approval
- **Date Recording**: Automatically record signature date and time

### 📧 Customer Communication
- **Email Distribution**: Send documents to customers directly
- **Status Updates**: Notify customers of document status changes
- **Link Tracking**: Track document access and downloads

### 🏷️ Organization & Search
- **Tags**: Tag documents for better organization and filtering
- **Advanced Filtering**: Filter by type, status, customer, employee, and more
- **GroupBy Options**: Group documents by type, status, customer, or employee
- **Full-Text Search**: Search across document names, descriptions, and attachments

## Installation

1. **Copy module to addons directory**:
   ```bash
   cp -r customer_document_management /path/to/odoo/addons/
   ```

2. **Restart Odoo and Update Module List**:
   - Go to Apps → Update Apps List
   - Search for "Customer Document Management"
   - Click **Install**

3. **Verify Installation**:
   - A new menu "Document Management" should appear in the sidebar
   - Sub-menus: "Documents" and "Approvals"

## Model Structure

### 1. **customer.document** (Main Model)
- Central model for document management
- Fields: name, reference, document_type, partner_id, employee_id, dates, status, etc.
- Relations: Links to partner (customer) and employee (responsible person)
- Inheritance: Includes mail.thread for messaging

### 2. **document.approval** (Approval Workflow)
- Manages approval process
- Fields: document_id, approver_id, state, comment, approval_date
- States: pending, approved, rejected, skipped

### 3. **customer.document.attachment** (File Management)
- Manages file attachments
- Fields: document_id, attachment_id, name, file_type, version
- Features: Version tracking, main file designation

### 4. **customer.document.tag** (Organization)
- Tags for document categorization
- Fields: name, color

### 5. **hr.employee** (Extended)
- Extended with: customer_ids, document_ids, document_count
- Link between employees and customers they manage

## Workflow

### Document Lifecycle
```
Draft → Submit → Requested Approval → Under Review → Approved → Signed → Completed
                                                  ↓
                                              Rejected (back to Draft)
```

### Status Descriptions
- **Draft**: Initial document creation, editable
- **Submitted**: Document submitted, awaiting actions
- **Under Review**: Undergoing approval process
- **Approved**: Approved by designated approvers
- **Signed**: Electronically signed
- **Completed**: Final status, document is active
- **Expired**: Document has passed expiry date
- **Cancelled**: Document cancelled

## Usage

### Creating a Document
1. Go to **Document Management → All Documents**
2. Click **Create**
3. Fill in:
   - Document Name
   - Document Type
   - Customer
   - Responsible Employee (optional)
   - Dates (Issue, Effective, Expiry)
4. Add attachments in the "Files" tab
5. Click **Save**

### Adding Approvers
1. In the document form, go to **Approvals** tab
2. Click **Add a line**
3. Select approver from employee list
4. Set sequence (order of approval)
5. Save the document
6. Click **Request Approval**

### Requesting Approval
1. Document must be in "Submitted" state
2. Click **Request Approval** button
3. Notifications sent to approvers
4. Approvers can approve/reject from their notifications

### Signing Document
1. Document must be "Approved"
2. Click **Sign** button
3. System records signature with date/time
4. Document moves to "Signed" state

### Creating New Version
1. From completed/signed document
2. Click **Create New Version**
3. New version created as draft with incremented version number
4. Link to previous version maintained

### Sending to Customer
1. Document must be approved/signed
2. Click **Send to Customer**
3. Email template used for distribution
4. Customer receives document attachment

## Access Control (Security)

| Role | Create | Read | Write | Delete |
|------|--------|------|-------|--------|
| Sales User | Yes | Yes | Yes | No |
| Sales Manager | Yes | Yes | Yes | Yes |
| HR User | Yes | Yes | Yes | No |
| Portal User | No | Limited | No | No |

## Reports (Extensible)

- **Documents by Customer**: List all documents per customer
- **Documents by Employee**: Track employee workload
- **Approval Status Report**: Monitor approval progress
- **Expiry Report**: Documents expiring soon

## API Endpoints

### Create Document
```python
document = env['customer.document'].create({
    'name': 'Contract ABC',
    'document_type': 'contract',
    'partner_id': customer_id,
    'employee_id': employee_id,
    'issue_date': '2024-01-01',
})
```

### Request Approval
```python
document.action_request_approval()
```

### Approve Document
```python
document.action_approve()
```

### Sign Document
```python
document.action_sign()
```

## Search Capabilities

- **Full-Text Search**: Search by document name, description, content
- **Customer Filter**: Find all documents for a specific customer
- **Employee Filter**: Track documents by responsible employee
- **Status Filters**: Quick filters for common statuses
- **Date Range**: Filter by issue date or expiry date
- **Tags**: Search by document tags

## Configuration

### Email Templates
- `email_document_template`: Template for sending documents to customers
- `email_approval_request`: Template for requesting approval

### Sequences
- `customer.document.seq`: Auto-generates document reference codes (format: DOC-00001)

### Cron Jobs (Future Enhancement)
- Automated expiry status update
- Reminder notifications for pending approvals
- Escalation for overdue documents

## Troubleshooting

### Module Not Appearing
- Run: `Reload` modules via Settings
- Check error logs: `tail -f /var/log/odoo/odoo.log`

### Cannot Install Module
- Check Python dependencies: `pip install -r requirements.txt`
- Verify Odoo version: Module requires Odoo 15+

### Access Denied Error
- Verify user has Sales or HR group permissions
- Check ir.model.access.csv for correct group assignments

## Development & Extension

### Adding New Document Types
Edit `customer.document.py` and add to `document_type` selection:
```python
document_type = fields.Selection(
    [
        ...
        ('custom_type', 'Custom Type'),
    ],
    ...
)
```

### Custom Workflow States
Extend the `state` field selection in the model.

### Adding Email Templates
Create XML template in `data/email_templates.xml`.

## Future Enhancements

- [ ] OCR for automatic text extraction
- [ ] Digital signature with certificate
- [ ] Document audit trail
- [ ] Automated reminders
- [ ] Integration with eSignature providers
- [ ] Batch document upload
- [ ] Mobile app support
- [ ] Document templates

## Contributors
- Development Team

## License
LGPL-3

## Support
For issues or feature requests, contact the development team.

---

**Version**: 15.0.1.0.0  
**Last Updated**: March 2024

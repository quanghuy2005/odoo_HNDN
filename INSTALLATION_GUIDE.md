# Installation & Deployment Guide

## Prerequisites

- Odoo 15.0
- Python 3.10+
- PostgreSQL 12+
- Virtual Environment activated

## Installation Steps

### Step 1: Verify Module Location
```bash
ls -la /home/quang/TTDN-15-01-N1/addons/customer_document_management/
```

Should see:
- `__manifest__.py`
- `__init__.py`
- `models/` directory
- `views/` directory
- `security/` directory
- `data/` directory

### Step 2: Activate Virtual Environment
```bash
source /home/quang/TTDN-15-01-N1/venv/bin/activate
```

### Step 3: Start Odoo with Module Update
```bash
cd /home/quang/TTDN-15-01-N1
python3 odoo-bin.py -c odoo.conf -d odoo -u all
```

**Output should include:**
```
INFO ? odoo.modules.loading: ... customer_document_management ...
INFO ? odoo.modules.loading: ... customer_document_management: installed
```

### Step 4: Access Odoo Interface
- Open browser: http://localhost:8069
- Login: admin / admin
- Database: odoo

### Step 5: Install Module via UI

**Method 1: Manual Installation**
1. Click **Apps** in top menu
2. Search: "Customer Document Management"
3. Click on module
4. Click **Install**

**Method 2: Search with "All"**
1. Apps → Search → Remove "Installed" filter
2. Search: "Document Management"
3. Install the module

### Step 6: Verify Installation
After installation, you should see:
- New menu: **"Document Management"** in sidebar
- Sub-menus:
  - All Documents
  - Approvals
- New fields in HR Employee module

---

## Configuration

### 1. Configure User Groups
1. Go to **Settings → Users & Companies → Users**
2. Select user
3. Add to group: "Sales Manager" or "HR User"

### 2. Create Sample Data (Optional)
```bash
# Login to Odoo via script interface or manually create:
# - 1 Customer (res.partner)
# - 1 Employee (hr.employee)
# - 1 Document (customer.document)
```

### 3. Setup Email Templates
1. Go to **Settings → Email → Templates**
2. Verify templates:
   - `email_document_template` (for sending docs)
   - `email_approval_request` (for approvals)

---

## First-Time Setup Checklist

- [ ] Module folder in correct location
- [ ] Odoo restarted with `--update=all`
- [ ] Module shows in Apps
- [ ] Module installed successfully
- [ ] New menus appear in sidebar
- [ ] Users have correct permissions
- [ ] Email configured (if using notifications)
- [ ] Test document creation

---

## Testing the Module

### Test 1: Create Document
1. Go to **Document Management → All Documents**
2. Click **Create**
3. Fill in details:
   - Name: "Test Contract"
   - Type: "Contract"
   - Customer: Select any customer
   - Save
4. **Result**: Document created in DRAFT status ✅

### Test 2: Add Attachment
1. Open created document
2. Go to **Files** tab
3. Click **Add a line**
4. Upload a PDF file
5. Save
6. **Result**: File appears with metadata ✅

### Test 3: Request Approval
1. Click **Request Approval** button
2. Add approvers in **Approvals** tab
3. Save and click **Request Approval**
4. **Result**: Status changes to UNDER_REVIEW ✅

### Test 4: Search Documents
1. Go to **Document Management → All Documents**
2. Search: "Test"
3. **Result**: Document appears in search results ✅

### Test 5: HR Integration
1. Go to **Employees** (HR module)
2. Open an employee
3. Go to **Customer Documents** tab
4. Add customers
5. Save
6. **Result**: Employee can manage customers ✅

---

## Troubleshooting

### Module not found in Apps
**Solution**: 
- Restart Odoo
- Go to Settings → Apps → Update Apps List
- Search again

### Permission Denied errors
**Solution**:
- Check user group: Settings → Users
- Add: "Sales Manager" or "HR User" group
- Verify security/ir.model.access.csv

### XML Validation errors
**Solution**:
- Check all `.xml` files for syntax errors
- Look for mismatched tags `</>` 
- Check file encoding (UTF-8)

### Database errors
**Solution**:
- Ensure PostgreSQL is running
- Check database name in odoo.conf
- Verify database exists

---

## Development Mode

### Enable Debug Mode
```bash
python3 odoo-bin.py -c odoo.conf -d odoo --dev=all
```

### View Module Logs
```bash
tail -f /home/quang/TTDN-15-01-N1/odoo.log
```

### Python Debugging
Add to code:
```python
import pdb; pdb.set_trace()  # Breakpoint
```

---

## Performance Optimization

### Database Indices
Add to model fields that are frequently searched:
```python
field_name = fields.Many2one(..., index=True)
```

### Query Optimization
- Use `search()` with proper domain
- Use `select_related()` for ForeignKey lookups
- Limit returned fields with `fields_list`

### Caching
Odoo automatically caches computed fields marked with `store=True`.

---

## Security Configuration

### Role-Based Access (Already configured)
- **Sales User**: Read, Create, Write
- **Sales Manager**: Full access (Read, Create, Write, Delete)
- **HR User**: Read, Create, Write
- **HR Manager**: Full access

### Document-Level Security (Future enhancement)
Can implement record-level permissions using `ir.rule`.

### Data Encryption (Future enhancement)
For sensitive data, implement field encryption.

---

## Backup & Recovery

### Backup Database
```bash
# Using pg_dump
pg_dump -U odoo -Fc odoo > /backups/odoo_$(date +%Y%m%d).dump
```

### Restore Database
```bash
# Using pg_restore
pg_restore -U odoo -d odoo /backups/odoo_YYYYMMDD.dump
```

### Backup Module Files
```bash
tar -czf customer_document_management_backup.tar.gz \
  /home/quang/TTDN-15-01-N1/addons/customer_document_management/
```

---

## Updates & Maintenance

### Apply Module Updates
```bash
# When code changes:
python3 odoo-bin.py -c odoo.conf -d odoo -u customer_document_management
```

### Upgrade Odoo Version
1. Backup database
2. Backup module
3. Upgrade Odoo
4. Reinstall module
5. Test in staging environment first

### Reset Module (Danger!)
```sql
-- In PostgreSQL, to uninstall:
SELECT ir_module_module_uninstall('customer_document_management');
```

---

## Monitoring

### Health Check
1. Create test document
2. Verify in database:
   ```sql
   SELECT COUNT(*) FROM customer_document;
   ```
3. Check Odoo logs for errors

### Performance Monitoring
1. Monitor slow queries
2. Check disk space
3. Monitor database size
4. Monitor server resources

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Module won't load | Python syntax error | Check `*.py` files with Python linter |
| XML error | Malformed XML | Validate XML syntax |
| Permission error | Wrong user group | Add user to "Sales Manager" group |
| Document not saved | Missing required field | Fill in all NOT NULL fields |
| Email not sent | Email not configured | Setup email in Odoo settings |
| Slow performance | Large dataset | Add database indices |

---

## Support Resources

### Documentation
- [Module README](../addons/customer_document_management/README.md)
- [Business Analysis](../addons/customer_document_management/BUSINESS_ANALYSIS.md)
- [Odoo Documentation](https://www.odoo.com/documentation/15.0/)

### Community
- [Odoo Community Forum](https://www.odoo.com/forum/help-1)
- [Stack Overflow - Odoo Tag](https://stackoverflow.com/questions/tagged/odoo)
- [Odoo GitHub](https://github.com/odoo/odoo)

### Contact
- Development Team: quang@example.com
- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/TTDN-15-01-N1/issues)

---

**Document Version**: 1.0  
**Last Updated**: March 13, 2024  
**Status**: Ready for Production

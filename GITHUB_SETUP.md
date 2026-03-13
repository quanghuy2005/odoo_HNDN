# GitHub Setup Guide

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Log in to your account
3. Click **"+"** icon → **New repository**
4. Fill in:
   - **Repository name**: `TTDN-15-01-N1` (or your preferred name)
   - **Description**: Odoo 15 Customer Document Management System with HR Integration
   - **Visibility**: Public (for coursework) or Private (for commercial)
5. Click **"Create repository"**

## Step 2: Connect Local Repository to GitHub

Copy the SSH URL from GitHub (for SSH setup) or HTTPS URL.

### Option A: Using HTTPS (Easier for beginners)

```bash
cd /home/quang/TTDN-15-01-N1

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/TTDN-15-01-N1.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using SSH (More secure)

First time SSH setup:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Save in ~/.ssh/id_ed25519
# Copy public key to GitHub Settings → SSH and GPG keys

cat ~/.ssh/id_ed25519.pub  # Copy this
```

Then push:
```bash
cd /home/quang/TTDN-15-01-N1

git remote add origin git@github.com:YOUR_USERNAME/TTDN-15-01-N1.git
git branch -M main
git push -u origin main
```

## Step 3: Verify on GitHub

- Go to your repository URL: `https://github.com/YOUR_USERNAME/TTDN-15-01-N1`
- You should see the module files uploaded

## Step 4: Add More Details (Optional)

### Create GitHub README at root level (if not exists)

```markdown
# Odoo 15 - Customer Document Management System

An integrated solution for managing customer documents with HR module integration.

## Features
- Document management (contracts, quotations, legal docs)
- Multi-step approval workflow
- Electronic signature support
- Version control
- Full-text search
- Employee responsibility assignment

## Installation
See [Module README](./addons/customer_document_management/README.md)

## Documentation
- [Business Analysis](./addons/customer_document_management/BUSINESS_ANALYSIS.md)
- [Module README](./addons/customer_document_management/README.md)
```

### Add Topics/Labels to Repository
1. Go to repository → Settings
2. Scroll to "Topics"
3. Add: `odoo`, `erp`, `document-management`, `crm`, `hr`

## Step 5: Future Commits

After making changes:

```bash
# Stage changes
git add addons/customer_document_management/

# Commit
git commit -m "fix: resolve approval workflow issue"

# Push to GitHub
git push origin main
```

## Branching Strategy (Recommended)

```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Make changes, commit
git add .
git commit -m "feat: add new feature"

# Push branch
git push origin feature/new-feature-name

# Create Pull Request on GitHub
```

## Common Git Commands

```bash
# View commit history
git log --oneline

# See current status
git status

# View differences
git diff

# Revert last commit
git revert HEAD

# View remote URL
git remote -v

# Change remote URL
git remote set-url origin NEW_URL
```

## Troubleshooting

### Cannot push - Permission denied
- Make sure SSH key is added to GitHub Settings
- Or use HTTPS with Personal Access Token instead

### Remote URL error
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/TTDN-15-01-N1.git
```

### Authentication issue
```bash
# Clear credentials
git credential-cache exit

# Try push again (will ask for credentials)
git push origin main
```

## GitHub Pages (Optional)

To host documentation:

1. Go to Settings → Pages
2. Choose Source: main branch / docs folder
3. Documentation will be available at: `https://YOUR_USERNAME.github.io/TTDN-15-01-N1`

---

## Repository File Structure

```
TTDN-15-01-N1/
├── .git/
├── .github/
│   └── workflows/          (CI/CD - optional)
├── addons/
│   └── customer_document_management/
│       ├── README.md
│       ├── BUSINESS_ANALYSIS.md
│       ├── __manifest__.py
│       ├── models/
│       ├── views/
│       ├── security/
│       └── data/
├── README.md               (Project root README)
└── .gitignore
```

---

**Need help?** Contact the development team or refer to [Git Documentation](https://git-scm.com/doc)

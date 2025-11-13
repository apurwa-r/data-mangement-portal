# Deployment Guide

This guide will help you push the EPAR Data Portal to GitHub and deploy it.

## Prerequisites

- Git installed on your machine
- GitHub account
- Repository created on GitHub (or ready to create one)

## Step 1: Initial Git Setup

If you haven't initialized git yet, run:

```bash
git init
```

## Step 2: Configure Git (if not already done)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 3: Add All Files

```bash
# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status
```

**Files that will be committed:**
- ✅ Source code (api/, frontend/, db/)
- ✅ Configuration files (config.py, constants.py)
- ✅ Documentation (README.md, .env.sample)
- ✅ Package files (requirements.txt, package.json)

**Files that will NOT be committed (in .gitignore):**
- ❌ `.env.dev` (your secrets)
- ❌ `db/*.sqlite` (database files)
- ❌ `node_modules/` (dependencies)
- ❌ `venv/` (Python virtual environment)
- ❌ `__pycache__/` (Python cache)
- ❌ `api/local.settings.json` (local Azure settings)

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: EPAR Data Portal with dual-portal architecture

Features:
- Uploader portal for project metadata and file uploads
- Downloader portal with search, filters, and downloads
- Azure Functions backend with 3 API endpoints
- SQLite database with FTS5 full-text search
- React frontend with UW theme
- Dual-mode support (mock/Azure Storage)
- Comprehensive documentation"
```

## Step 5: Create GitHub Repository

### Option A: Create New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `epar-data-portal` (or your preferred name)
3. Description: "EPAR Data Portal - Dual-portal web application for research outputs"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Option B: Use Existing Repository

If you already have a repository, get the URL from GitHub.

## Step 6: Add Remote and Push

Replace `<your-username>` and `<repository-name>` with your values:

```bash
# Add remote
git remote add origin https://github.com/<your-username>/<repository-name>.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/epar-data-portal.git
git branch -M main
git push -u origin main
```

## Step 7: Verify on GitHub

1. Go to your repository URL: `https://github.com/<your-username>/<repository-name>`
2. You should see:
   - ✅ README.md displayed on the main page
   - ✅ All folders (api, frontend, db, etc.)
   - ✅ .gitignore and .env.sample files
   - ❌ No .env.dev file (good - it's secret!)
   - ❌ No database files (good - they're local!)

## Step 8: Set Up Repository Secrets (for Production)

If you plan to deploy to production, add secrets to GitHub:

1. Go to your repository on GitHub
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add these secrets:
   - `AZURE_STORAGE_CONNECTION_STRING` - Your Azure Storage connection string
   - `AZURE_FUNCTIONS_PUBLISH_PROFILE` - For Azure Functions deployment

## Future Updates

When you make changes to the code:

```bash
# Check what changed
git status

# Add changed files
git add .

# Commit with descriptive message
git commit -m "Add feature: description of what you changed"

# Push to GitHub
git push
```

## Deployment Options

### Option 1: Local Development (Current Setup)
- ✅ Already working
- Run backend: `cd api && func start`
- Run frontend: `cd frontend && npm run dev`

### Option 2: Azure Deployment

#### Backend (Azure Functions)
```bash
cd api
func azure functionapp publish <your-function-app-name>
```

#### Frontend (Azure Static Web Apps)
```bash
cd frontend
npm run build
# Deploy dist/ folder to Azure Static Web Apps
```

### Option 3: Other Cloud Providers
- **Vercel**: Deploy frontend directly from GitHub
- **Netlify**: Deploy frontend directly from GitHub
- **AWS Lambda**: Deploy backend as Lambda functions
- **Heroku**: Deploy both frontend and backend

## Troubleshooting

### "Permission denied" when pushing
- Check your GitHub credentials
- Use personal access token instead of password
- Or set up SSH keys

### "Remote already exists"
```bash
git remote remove origin
git remote add origin <new-url>
```

### Want to undo last commit (before push)
```bash
git reset --soft HEAD~1
```

### Accidentally committed secrets
1. Remove from git: `git rm --cached .env.dev`
2. Add to .gitignore (already done)
3. Commit: `git commit -m "Remove secrets"`
4. **Change your secrets** (they're now in git history!)

## Best Practices

1. **Never commit secrets** - Use .env files and .gitignore
2. **Write descriptive commit messages** - Explain what and why
3. **Commit often** - Small, focused commits are better
4. **Test before pushing** - Make sure everything works
5. **Use branches** - For new features, create a branch:
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "Add new feature"
   git push -u origin feature/new-feature
   # Create pull request on GitHub
   ```

## Need Help?

- GitHub Docs: https://docs.github.com
- Git Docs: https://git-scm.com/doc
- Azure Functions Deployment: https://docs.microsoft.com/azure/azure-functions/

---

**Ready to push to GitHub?** Follow Steps 1-7 above!


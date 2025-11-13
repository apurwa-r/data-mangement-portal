# Quick Start Guide

Get the EPAR Data Portal running in 5 minutes!

## Prerequisites Check

Before starting, make sure you have:

- [ ] Python 3.9-3.13 installed
- [ ] Node.js 16+ installed
- [ ] Azure Functions Core Tools installed
- [ ] Git installed (if cloning from GitHub)

### Check Versions

```bash
python --version    # Should be 3.9-3.13
node --version      # Should be 16+
func --version      # Should be 4.x
```

## 5-Minute Setup

### 1️⃣ Get the Code (30 seconds)

**If cloning from GitHub:**
```bash
git clone https://github.com/<your-username>/epar-data-portal.git
cd epar-data-portal
```

**If you already have it:**
```bash
cd data-management
```

### 2️⃣ Setup Backend (2 minutes)

```bash
# Go to api folder
cd api

# Create virtual environment (if not exists)
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1    # Windows PowerShell
# OR
.\venv\Scripts\activate.bat    # Windows CMD
# OR
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Go back to root
cd ..
```

### 3️⃣ Setup Database (30 seconds)

```bash
# Initialize database with sample data
cd db
python init_db.py
cd ..
```

You should see:
```
✓ Database created: ./db/docs.sqlite
✓ Tables created: projects, files, files_fts
✓ Sample data inserted: 3 projects, 6 files
```

### 4️⃣ Setup Frontend (1 minute)

```bash
# Go to frontend folder
cd frontend

# Install dependencies
npm install

# Go back to root
cd ..
```

### 5️⃣ Configure Environment (30 seconds)

```bash
# Copy sample environment file
cp .env.sample .env.dev

# Edit .env.dev if needed (optional - defaults work fine)
```

**Default configuration uses MOCK mode** - no Azure Storage needed!

### 6️⃣ Run the Application (30 seconds)

**Open TWO terminal windows:**

**Terminal 1 - Backend:**
```bash
cd api
.\venv\Scripts\Activate.ps1    # Windows
# source venv/bin/activate     # Mac/Linux
func start
```

Wait for:
```
Functions:
  download: [GET] http://localhost:7071/api/download
  search: [GET] http://localhost:7071/api/search
  upload: [POST,OPTIONS] http://localhost:7071/api/upload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Wait for:
```
  ➜  Local:   http://localhost:5173/
```

### 7️⃣ Open in Browser

Navigate to: **http://localhost:5173**

🎉 **You're done!**

## First Steps

### Test the Downloader Portal

1. Click **"Sign In with Microsoft"** (mock authentication)
2. You'll see the search page
3. Click **"Apply Filters"** without entering anything
4. You should see **3 sample projects**
5. Try searching for **"kenya"** → should show 2 projects
6. Click **Download** on any file → shows mock download message

### Test the Uploader Portal

1. Click **"Upload Portal"** button in the header
2. Fill out the form:
   - Project Code: `EPAR-2024-TEST`
   - Title: `My Test Project`
   - Select at least one Research Area
   - Select at least one Geography
   - Select an Output Type
   - PO Contact: `Your Name`
   - Date of Completion: Select any month
3. Drag and drop a file (or click Browse)
4. Click **"Upload Project"**
5. Should show success message!
6. Switch back to **Downloader Portal**
7. Search for `EPAR-2024-TEST`
8. Your project should appear! 🎉

## Troubleshooting

### Backend won't start

**Error: "Python version not supported"**
```bash
# Check Python version
python --version

# If 3.14+, you need to install Python 3.13 or lower
# Download from: https://www.python.org/downloads/
```

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
cd api
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start

**Error: "Cannot find module"**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Error: "Port 5173 already in use"**
```bash
# Kill the process using port 5173
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5173 | xargs kill
```

### Database errors

**Error: "Database not found"**
```bash
# Recreate database
cd db
python init_db.py
```

**Error: "Permission denied"**
```bash
# Make sure no other process is using the database
# Close any SQLite browser tools
# Restart the backend
```

### CORS errors in browser

**Error: "CORS policy blocked"**
- Make sure backend is running on `http://localhost:7071`
- Make sure frontend is running on `http://localhost:5173`
- Check browser console for exact error
- Restart both servers

## Next Steps

### Switch to Azure Storage (Production)

1. Create Azure Storage account
2. Get connection string from Azure Portal
3. Edit `.env.dev`:
   ```env
   BLOB_CONN=DefaultEndpointsProtocol=https;AccountName=...
   ```
4. Restart backend
5. Now uploads go to Azure and downloads are real!

### Add Real Microsoft Authentication

See `README.md` for instructions on setting up Azure AD OAuth.

### Deploy to Production

See `DEPLOYMENT.md` for deployment instructions.

## Common Commands

### Start Backend
```bash
cd api
.\venv\Scripts\Activate.ps1
func start
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Reset Database
```bash
cd db
rm docs.sqlite
python init_db.py
```

### View Database
```bash
# Install SQLite browser or use command line
sqlite3 db/docs.sqlite
.tables
SELECT * FROM projects;
.quit
```

### Update Dependencies

**Backend:**
```bash
cd api
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm update
```

## Getting Help

- Check `README.md` for detailed documentation
- Check `DEPLOYMENT.md` for deployment help
- Check backend logs in terminal for errors
- Check browser console (F12) for frontend errors

---

**Still stuck?** Open an issue on GitHub or contact the EPAR team.

**Everything working?** Great! Start uploading your research outputs! 🚀


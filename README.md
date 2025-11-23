# Data Portal

A dual-portal web application for uploading, searching, and downloading  research outputs and datasets. Built for  a project at the University of Washington.

## Overview

The  Data Portal provides two distinct interfaces:
- **Uploader Portal**: For  staff to upload research outputs with comprehensive metadata
- **Downloader Portal**: For users to search, filter, and download  resources

The system uses React for the frontend, Azure Functions for the backend API, SQLite with FTS5 for full-text search, and Azure Blob Storage for file storage.

## Features

### Uploader Portal
- **Project Metadata Form**: Comprehensive form for project information
- **Multi-Select Filters**: Research areas, geographies, output types
- **Drag-and-Drop Upload**: Easy file upload with preview
- **File Type Support**: PDF, DOCX, XLSX, TXT, and Markdown files
- **Database Integration**: Automatic indexing for search

### Downloader Portal
- **Full-Text Search**: Search projects by keywords with FTS5 indexing
- **Advanced Filtering**: Filter by research areas, geographies, dates, PO contacts, AgDev partners, output types
- **Multi-Select Capability**: Select multiple options within each filter category
- **Secure Downloads**: Temporary SAS URLs for secure file access
- **Empty State**: Results only shown after applying filters
- **UW Themed**: University of Washington purple and gold branding

### Backend & Infrastructure
- **Azure Functions**: Serverless backend with 3 API endpoints
- **SQLite + FTS5**: Full-text search with automatic indexing
- **Dual-Mode Support**: Works with or without Azure Storage (mock mode for development)
- **CORS Enabled**: Secure cross-origin requests
- **Configuration-Based**: Easy switching between development and production

## Project Structure

```
├── api/                          # Azure Functions backend (Python)
│   ├── function_app.py          # Main API with 3 endpoints (search, download, upload)
│   ├── db_helper.py             # Database query helper
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Python virtual environment
├── frontend/                     # React web application
│   ├── src/
│   │   ├── components/
│   │   │   ├── MainPortal.jsx   # Downloader portal (search & download)
│   │   │   ├── UploaderPortal.jsx # Uploader portal (upload & metadata)
│   │   │   ├── SignInPage.jsx   # Authentication page
│   │   │   ├── HelpModal.jsx    # Help/information modal
│   │   │   └── ...              # Other components
│   │   ├── App.jsx              # Main app with routing
│   │   └── main.jsx             # Entry point
│   ├── package.json             # Node dependencies
│   └── vite.config.js           # Vite configuration
├── db/                          # Database files
│   ├── database.py              # Database helper class
│   ├── init_db.py               # Database initialization script
│   └── docs.sqlite              # SQLite database (not committed)
├── tools/                       # Utility scripts
├── docs/                        # Documentation
├── data/                        # Sample files for testing
├── tests/                       # Test files
├── config.py                    # Configuration loader
├── constants.py                 # System constants
└── .env.dev                     # Environment config (not committed)
```

## Quick Start

### Prerequisites

- **Python 3.9-3.13** (Azure Functions requirement)
- **Node.js 16+** (for React frontend)
- **Azure Functions Core Tools** (for local development)
- **Azure Storage Account** (optional - works in mock mode without it)

### Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/apurwa-r/data-mangement-portal.git
cd data-management
```

#### 2. Backend Setup

```bash
cd api

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Database Setup

```bash
# From project root
cd db
python init_db.py
```

This creates `docs.sqlite` with:
- 3 sample projects
- 6 sample files
- FTS5 full-text search index

#### 4. Configure Environment

Create or edit `.env.dev` in the project root:

```env
# Database
DB_PATH=./db/docs.sqlite

# Azure Storage (optional - use MOCK for development)
BLOB_CONN=MOCK
BLOB_CONTAINER=docs

# For production, replace with real connection string:
# BLOB_CONN=DefaultEndpointsProtocol=https;AccountName=youraccountname;AccountKey=...

# Other settings
REQUIRE_AUTH=true
MAX_ABSTRACT_BYTES=3000
SUPPORTED_EXT=.pdf,.txt,.md,.docx,.xlsx
DOWNLOAD_RATE_LIMIT=30
LOG_LEVEL=DEBUG
```

#### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

#### 6. Run the Application

**Terminal 1 - Backend:**
```bash
cd api
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Mac/Linux
func start
```

Backend will run on: `http://localhost:7071`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:5173`

#### 7. Access the Portal

Open your browser and navigate to: **http://localhost:5173**

1. Click "Sign In with Microsoft" (mock authentication)
2. You'll see the **Downloader Portal**
3. Click "Upload Portal" to switch to the **Uploader Portal**

## API Endpoints

### Backend API (http://localhost:7071/api)

#### 1. Search Projects
```
GET /api/search
```

**Query Parameters:**
- `q` - Search query (optional)
- `researchAreas` - Comma-separated list (optional)
- `geographies` - Comma-separated list (optional)
- `outputTypes` - Comma-separated list (optional)
- `poContacts` - Comma-separated list (optional)
- `dateFrom` - Start date in YYYY-MM format (optional)
- `dateTo` - End date in YYYY-MM format (optional)

**Example:**
```bash
curl "http://localhost:7071/api/search?q=kenya&geographies=Kenya"
```

#### 2. Download File
```
GET /api/download?fileId={id}
```

**Query Parameters:**
- `fileId` - File ID (required)

**Returns:**
- Mock mode: Message indicating mock download
- Azure mode: SAS URL for secure download

**Example:**
```bash
curl "http://localhost:7071/api/download?fileId=1"
```

#### 3. Upload Project
```
POST /api/upload
```

**Form Data:**
- `projectCode` - Project code (required)
- `title` - Project title (required)
- `researchAreas` - JSON array of research areas (required)
- `geographies` - JSON array of geographies (required)
- `outputType` - Type of output (required)
- `poContact` - Primary contact (required)
- `dateCompletion` - Completion date in YYYY-MM format (required)
- `otherPos` - JSON array of other contacts (optional)
- `agdevPartner` - AgDev partner organization (optional)
- `dateInitialRequest` - Initial request date in YYYY-MM format (optional)
- `file_0`, `file_1`, ... - Files to upload (required)

**Example:**
```bash
# Use the uploader portal UI for easier uploads
```

## Usage Guide

### Downloader Portal

1. **Sign In**: Click "Sign In with Microsoft" (currently mock authentication)
2. **Search**:
   - Enter keywords in the search box
   - Or leave blank to search by filters only
3. **Apply Filters**:
   - Select research areas (multi-select)
   - Select geographies (multi-select)
   - Select output types (multi-select)
   - Select PO contacts (multi-select)
   - Set date range (optional)
4. **View Results**: Click "Apply Filters" to see matching projects
5. **Download**: Click download button on any file

### Uploader Portal

1. **Switch Mode**: Click "Upload Portal" button in header
2. **Fill Project Information**:
   - Project Code (required)
   - Title (required)
   - Research Areas (select at least one)
   - Geographies (select at least one)
   - Output Type (required)
3. **Fill Contact & Timeline**:
   - PO Contact (required)
   - Date of Completion (required)
   - Other fields optional
4. **Upload Files**:
   - Drag and drop files, or click "Browse Files"
   - Supported: PDF, TXT, MD, DOCX, XLSX
5. **Submit**: Click "Upload Project"
6. **Verify**: Switch to Downloader Portal and search for your project

## Configuration Modes

### Mock Mode (Development)
Set in `.env.dev`:
```env
BLOB_CONN=MOCK
```

**Features:**
- ✅ All functionality works
- ✅ Files saved to database
- ✅ Search and filters work
- ⚠️ Downloads show message instead of actual file
- ⚠️ Files not uploaded to Azure Storage

### Azure Mode (Production)
Set in `.env.dev`:
```env
BLOB_CONN=DefaultEndpointsProtocol=https;AccountName=youraccountname;AccountKey=...
```

**Features:**
- ✅ All functionality works
- ✅ Files uploaded to Azure Blob Storage
- ✅ Real SAS URLs for downloads
- ✅ Secure file access with expiring links

## Development Status

- [x] Repository structure
- [x] Environment configuration
- [x] Azure Functions backend
- [x] SQLite database with FTS5
- [x] Search API with filters
- [x] Download API with SAS URLs
- [x] Upload API with file handling
- [x] React frontend
- [x] Downloader portal (search & download)
- [x] Uploader portal (upload & metadata)
- [x] Multi-page authentication flow
- [x] Mode switching (uploader/downloader)
- [x] Dual-mode support (mock/Azure)
- [ ] Microsoft authentication (optional)
- [ ] Content extraction from files (optional)
- [ ] Edit/delete functionality (optional)

## Troubleshooting

### Backend won't start
- Make sure you're using Python 3.9-3.13 (not 3.14+)
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Check Azure Functions Core Tools is installed

### Frontend won't start
- Run `npm install` in frontend directory
- Check Node.js version: `node --version` (should be 16+)

### Database not found
- Run `python db/init_db.py` from project root
- Check `DB_PATH` in `.env.dev` points to correct location

### CORS errors
- Make sure backend is running on `http://localhost:7071`
- Make sure frontend is running on `http://localhost:5173`
- Check CORS headers in `api/function_app.py`

### Upload not working
- Check backend logs for errors
- Verify file types are supported (.pdf, .txt, .md, .docx, .xlsx)
- Check database permissions




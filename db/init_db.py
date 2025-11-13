"""
EPAR Data Portal - Database Initialization Script
Creates SQLite database with FTS5 full-text search index.
"""

import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import config
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import config


def create_database(db_path: str):
    """Create database with schema and FTS5 index."""
    
    print(f"Creating database at: {db_path}")
    
    # Ensure db directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
    cursor = conn.cursor()
    
    # ========================================================================
    # Table 1: projects - Project metadata
    # ========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            research_areas TEXT,  -- JSON array
            date_initial_request TEXT,
            date_completion TEXT,
            po_contact TEXT,
            other_pos TEXT,  -- JSON array
            agdev_partner TEXT,
            output_type TEXT,
            geographies TEXT,  -- JSON array
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ========================================================================
    # Table 2: files - File metadata
    # ========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER,  -- Size in bytes
            blob_path TEXT UNIQUE NOT NULL,
            text_content TEXT,  -- Extracted text for search (limited to MAX_ABSTRACT_BYTES)
            upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    
    # ========================================================================
    # Table 3: files_fts - FTS5 full-text search index
    # ========================================================================
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
            file_id,
            project_code,
            title,
            file_name,
            text_content
        )
    """)
    
    # ========================================================================
    # Triggers: Keep FTS5 index in sync with files table
    # ========================================================================
    
    # Trigger: Insert
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON files BEGIN
            INSERT INTO files_fts(file_id, project_code, title, file_name, text_content)
            SELECT 
                new.id,
                p.project_code,
                p.title,
                new.file_name,
                new.text_content
            FROM projects p
            WHERE p.id = new.project_id;
        END
    """)
    
    # Trigger: Delete
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS files_ad AFTER DELETE ON files BEGIN
            DELETE FROM files_fts WHERE file_id = old.id;
        END
    """)
    
    # Trigger: Update
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS files_au AFTER UPDATE ON files BEGIN
            DELETE FROM files_fts WHERE file_id = old.id;
            INSERT INTO files_fts(file_id, project_code, title, file_name, text_content)
            SELECT 
                new.id,
                p.project_code,
                p.title,
                new.file_name,
                new.text_content
            FROM projects p
            WHERE p.id = new.project_id;
        END
    """)
    
    # ========================================================================
    # Indexes for better query performance
    # ========================================================================
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_blob_path ON files(blob_path)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_code ON projects(project_code)")
    
    conn.commit()
    print("✓ Database schema created successfully")
    
    return conn


def populate_mock_data(conn: sqlite3.Connection):
    """Populate database with mock data for testing."""
    
    print("\nPopulating mock data...")
    cursor = conn.cursor()
    
    # Mock projects data (matching the frontend mockData.js)
    mock_projects = [
        {
            "project_code": "EPAR-2024-015",
            "title": "Agricultural Market Systems in Kenya",
            "research_areas": ["Agricultural Economics", "Market Systems"],
            "date_initial_request": "2024-01",
            "date_completion": "2024-08",
            "po_contact": "Sarah Johnson",
            "other_pos": ["Michael Chen"],
            "agdev_partner": "Kenya Agricultural Research Institute",
            "output_type": "Final Report",
            "geographies": ["Kenya"],
            "files": [
                {"name": "Final_Report.pdf", "type": "pdf", "size": 2516582, "blob_path": "epar-2024-015/Final_Report.pdf", 
                 "text": "Agricultural Market Systems in Kenya. This report examines market access, price volatility, and supply chain efficiency in Kenyan agricultural markets."},
                {"name": "Data_Analysis.xlsx", "type": "xlsx", "size": 1153434, "blob_path": "epar-2024-015/Data_Analysis.xlsx",
                 "text": "Market price data, farmer surveys, and supply chain analysis for Kenya agricultural markets."},
            ]
        },
        {
            "project_code": "EPAR-2024-012",
            "title": "Food Security Assessment in Tanzania",
            "research_areas": ["Food Security", "Rural Development"],
            "date_initial_request": "2023-11",
            "date_completion": "2024-06",
            "po_contact": "John Smith",
            "other_pos": ["Emily Davis"],
            "agdev_partner": "Tanzania Food Security Network",
            "output_type": "Technical Note",
            "geographies": ["Tanzania"],
            "files": [
                {"name": "Technical_Note.pdf", "type": "pdf", "size": 1887437, "blob_path": "epar-2024-012/Technical_Note.pdf",
                 "text": "Food Security Assessment Tanzania. Analysis of household food security, nutrition indicators, and agricultural productivity in rural Tanzania."},
                {"name": "Field_Data.xlsx", "type": "xlsx", "size": 3355443, "blob_path": "epar-2024-012/Field_Data.xlsx",
                 "text": "Household survey data, nutrition measurements, crop yields, and food consumption patterns from Tanzania field research."},
            ]
        },
        {
            "project_code": "EPAR-2023-089",
            "title": "Gender and Agricultural Extension Services",
            "research_areas": ["Gender Studies", "Agricultural Extension"],
            "date_initial_request": "2023-05",
            "date_completion": "2023-12",
            "po_contact": "Sarah Johnson",
            "other_pos": ["Emily Rodriguez"],
            "agdev_partner": "International Food Policy Research Institute",
            "output_type": "Final Report",
            "geographies": ["Kenya", "Tanzania", "Uganda"],
            "files": [
                {"name": "Final_Report.pdf", "type": "pdf", "size": 3355443, "blob_path": "epar-2023-089/Final_Report.pdf",
                 "text": "Gender and Agricultural Extension Services. Study of gender disparities in access to agricultural extension services across East Africa. Examines barriers women farmers face."},
                {"name": "Survey_Data.xlsx", "type": "xlsx", "size": 2621440, "blob_path": "epar-2023-089/Survey_Data.xlsx",
                 "text": "Survey responses from male and female farmers in Kenya, Tanzania, and Uganda regarding extension service access and agricultural training."},
            ]
        },
    ]
    
    # Insert projects and files
    for project_data in mock_projects:
        # Insert project
        cursor.execute("""
            INSERT INTO projects (
                project_code, title, research_areas, date_initial_request, 
                date_completion, po_contact, other_pos, agdev_partner, 
                output_type, geographies
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_data["project_code"],
            project_data["title"],
            json.dumps(project_data["research_areas"]),
            project_data["date_initial_request"],
            project_data["date_completion"],
            project_data["po_contact"],
            json.dumps(project_data["other_pos"]),
            project_data["agdev_partner"],
            project_data["output_type"],
            json.dumps(project_data["geographies"])
        ))
        
        project_id = cursor.lastrowid
        
        # Insert files for this project
        for file_data in project_data["files"]:
            cursor.execute("""
                INSERT INTO files (
                    project_id, file_name, file_type, file_size, 
                    blob_path, text_content
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                file_data["name"],
                file_data["type"],
                file_data["size"],
                file_data["blob_path"],
                file_data["text"]
            ))
    
    conn.commit()
    print(f"✓ Inserted {len(mock_projects)} projects with files")


def verify_database(conn: sqlite3.Connection):
    """Verify database was created correctly."""
    
    print("\nVerifying database...")
    cursor = conn.cursor()
    
    # Check projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    project_count = cursor.fetchone()[0]
    print(f"✓ Projects: {project_count}")
    
    # Check files
    cursor.execute("SELECT COUNT(*) FROM files")
    file_count = cursor.fetchone()[0]
    print(f"✓ Files: {file_count}")
    
    # Check FTS5 index
    cursor.execute("SELECT COUNT(*) FROM files_fts")
    fts_count = cursor.fetchone()[0]
    print(f"✓ FTS5 index entries: {fts_count}")
    
    # Test FTS5 search
    cursor.execute("SELECT file_id, project_code, title FROM files_fts WHERE files_fts MATCH 'kenya' LIMIT 3")
    results = cursor.fetchall()
    print(f"✓ FTS5 search test ('kenya'): {len(results)} results")
    
    if results:
        print("\n  Sample results:")
        for file_id, project_code, title in results:
            print(f"    - {project_code}: {title}")


def main():
    """Main function."""
    
    print("=" * 60)
    print("EPAR Data Portal - Database Initialization")
    print("=" * 60)
    
    db_path = config.db_path
    
    # Create database
    conn = create_database(db_path)
    
    # Populate with mock data
    populate_mock_data(conn)
    
    # Verify
    verify_database(conn)
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ Database initialization complete!")
    print(f"  Location: {db_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()


"""
EPAR Data Portal - Database Helper Module
Provides functions to query the SQLite database with FTS5 search.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys

# Add parent directory to path to import config
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import config


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def search_projects(
    query: Optional[str] = None,
    research_areas: Optional[List[str]] = None,
    geographies: Optional[List[str]] = None,
    output_types: Optional[List[str]] = None,
    po_contacts: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search projects with filters.
    
    Args:
        query: Full-text search query
        research_areas: Filter by research areas (OR within, AND between)
        geographies: Filter by geographies
        output_types: Filter by output types
        po_contacts: Filter by PO contacts
        date_from: Filter by completion date (from)
        date_to: Filter by completion date (to)
    
    Returns:
        List of projects with their files
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build query
    sql_parts = []
    params = []
    
    # If there's a text query, use FTS5 search
    if query and query.strip():
        # Search in FTS5 index and join with projects
        sql_parts.append("""
            SELECT DISTINCT p.* 
            FROM projects p
            INNER JOIN files f ON f.project_id = p.id
            INNER JOIN files_fts fts ON fts.file_id = f.id
            WHERE files_fts MATCH ?
        """)
        params.append(query.strip())
    else:
        # No text query, just filter by metadata
        sql_parts.append("SELECT * FROM projects WHERE 1=1")
    
    # Add metadata filters
    filter_conditions = []
    
    if research_areas:
        # OR within research areas
        area_conditions = []
        for area in research_areas:
            area_conditions.append("research_areas LIKE ?")
            params.append(f'%"{area}"%')
        filter_conditions.append(f"({' OR '.join(area_conditions)})")
    
    if geographies:
        # OR within geographies
        geo_conditions = []
        for geo in geographies:
            geo_conditions.append("geographies LIKE ?")
            params.append(f'%"{geo}"%')
        filter_conditions.append(f"({' OR '.join(geo_conditions)})")
    
    if output_types:
        # OR within output types
        type_conditions = []
        for output_type in output_types:
            type_conditions.append("output_type = ?")
            params.append(output_type)
        filter_conditions.append(f"({' OR '.join(type_conditions)})")
    
    if po_contacts:
        # OR within PO contacts
        po_conditions = []
        for po in po_contacts:
            po_conditions.append("po_contact = ?")
            params.append(po)
        filter_conditions.append(f"({' OR '.join(po_conditions)})")
    
    if date_from:
        filter_conditions.append("date_completion >= ?")
        params.append(date_from)
    
    if date_to:
        filter_conditions.append("date_completion <= ?")
        params.append(date_to)
    
    # Combine filters with AND
    if filter_conditions:
        if query and query.strip():
            # FTS query already has WHERE, add AND
            sql_parts.append("AND " + " AND ".join(filter_conditions))
        else:
            # No FTS query, add filters to WHERE
            sql_parts.append("AND " + " AND ".join(filter_conditions))
    
    # Execute query
    sql = " ".join(sql_parts)
    cursor.execute(sql, params)
    
    projects_rows = cursor.fetchall()
    
    # Convert to dictionaries and fetch files for each project
    projects = []
    for row in projects_rows:
        project = dict(row)
        
        # Parse JSON fields
        project['researchAreas'] = json.loads(project.pop('research_areas', '[]'))
        project['otherPos'] = json.loads(project.pop('other_pos', '[]'))
        project['geographies'] = json.loads(project.pop('geographies', '[]'))
        
        # Rename fields to match frontend expectations
        project['projectCode'] = project.pop('project_code')
        project['dateInitialRequest'] = project.pop('date_initial_request')
        project['dateCompletion'] = project.pop('date_completion')
        project['poContact'] = project.pop('po_contact')
        project['agdevPartner'] = project.pop('agdev_partner')
        project['outputType'] = project.pop('output_type')
        
        # Fetch files for this project
        cursor.execute("""
            SELECT id, file_name, file_type, file_size, blob_path
            FROM files
            WHERE project_id = ?
        """, (project['id'],))
        
        files_rows = cursor.fetchall()
        project['files'] = []
        
        for file_row in files_rows:
            file_dict = dict(file_row)
            # Format size
            size_bytes = file_dict['file_size']
            if size_bytes:
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                size_str = "Unknown"
            
            project['files'].append({
                'id': file_dict['id'],
                'name': file_dict['file_name'],
                'type': file_dict['file_type'],
                'size': size_str,
                'blobPath': file_dict['blob_path']
            })
        
        projects.append(project)
    
    conn.close()
    return projects


def get_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:
    """
    Get file metadata by ID.
    
    Args:
        file_id: File ID
    
    Returns:
        File metadata dictionary or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT f.*, p.project_code
        FROM files f
        INNER JOIN projects p ON p.id = f.project_id
        WHERE f.id = ?
    """, (file_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    file_dict = dict(row)
    
    # Format size
    size_bytes = file_dict['file_size']
    if size_bytes:
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        size_str = "Unknown"
    
    return {
        'id': file_dict['id'],
        'name': file_dict['file_name'],
        'type': file_dict['file_type'],
        'size': size_str,
        'blobPath': file_dict['blob_path'],
        'projectCode': file_dict['project_code']
    }


def get_filter_options() -> Dict[str, List[str]]:
    """
    Get all unique values for filter dropdowns.
    
    Returns:
        Dictionary with lists of unique values for each filter
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all unique research areas
    cursor.execute("SELECT DISTINCT research_areas FROM projects")
    research_areas_set = set()
    for row in cursor.fetchall():
        areas = json.loads(row[0])
        research_areas_set.update(areas)
    
    # Get all unique geographies
    cursor.execute("SELECT DISTINCT geographies FROM projects")
    geographies_set = set()
    for row in cursor.fetchall():
        geos = json.loads(row[0])
        geographies_set.update(geos)
    
    # Get all unique output types
    cursor.execute("SELECT DISTINCT output_type FROM projects")
    output_types = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Get all unique PO contacts
    cursor.execute("SELECT DISTINCT po_contact FROM projects")
    po_contacts = [row[0] for row in cursor.fetchall() if row[0]]
    
    conn.close()
    
    return {
        'researchAreas': sorted(list(research_areas_set)),
        'geographies': sorted(list(geographies_set)),
        'outputTypes': sorted(output_types),
        'poContacts': sorted(po_contacts)
    }


if __name__ == "__main__":
    # Test the database functions
    print("Testing database functions...\n")
    
    # Test 1: Search for "kenya"
    print("Test 1: Search for 'kenya'")
    results = search_projects(query="kenya")
    print(f"  Found {len(results)} projects")
    for project in results:
        print(f"    - {project['projectCode']}: {project['title']}")
    
    # Test 2: Filter by geography
    print("\nTest 2: Filter by geography (Tanzania)")
    results = search_projects(geographies=["Tanzania"])
    print(f"  Found {len(results)} projects")
    for project in results:
        print(f"    - {project['projectCode']}: {project['title']}")
    
    # Test 3: Get file by ID
    print("\nTest 3: Get file by ID (1)")
    file_info = get_file_by_id(1)
    if file_info:
        print(f"  File: {file_info['name']} ({file_info['size']})")
        print(f"  Blob path: {file_info['blobPath']}")
    
    # Test 4: Get filter options
    print("\nTest 4: Get filter options")
    options = get_filter_options()
    print(f"  Research Areas: {options['researchAreas']}")
    print(f"  Geographies: {options['geographies']}")
    print(f"  Output Types: {options['outputTypes']}")
    print(f"  PO Contacts: {options['poContacts']}")


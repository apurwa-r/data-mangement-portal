"""
EPAR Data Portal - Database Helper
Provides database query functions for the API.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path to import config
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config import config

logger = logging.getLogger(__name__)


class DatabaseHelper:
    """Helper class for database operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize database helper."""
        self.db_path = db_path or config.db_path
        logger.info(f"Database helper initialized with path: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def search_files(
        self,
        query: str = None,
        research_areas: List[str] = None,
        geographies: List[str] = None,
        output_types: List[str] = None,
        po_contacts: List[str] = None,
        agdev_partners: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search files with filters.
        
        Args:
            query: Full-text search query
            research_areas: Filter by research areas
            geographies: Filter by geographies
            output_types: Filter by output types
            po_contacts: Filter by PO contacts
            agdev_partners: Filter by AgDev partners
            date_from: Filter by completion date (from)
            date_to: Filter by completion date (to)
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of projects with files
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build query based on filters
            if query:
                # Use FTS5 search
                sql = """
                    SELECT DISTINCT
                        p.id as project_id,
                        p.project_code,
                        p.title,
                        p.research_areas,
                        p.date_initial_request,
                        p.date_completion,
                        p.po_contact,
                        p.other_pos,
                        p.agdev_partner,
                        p.output_type,
                        p.geographies
                    FROM projects p
                    INNER JOIN files f ON p.id = f.project_id
                    INNER JOIN files_fts fts ON f.id = fts.file_id
                    WHERE files_fts MATCH ?
                """
                params = [query]
            else:
                # No search query, just filter
                sql = """
                    SELECT DISTINCT
                        p.id as project_id,
                        p.project_code,
                        p.title,
                        p.research_areas,
                        p.date_initial_request,
                        p.date_completion,
                        p.po_contact,
                        p.other_pos,
                        p.agdev_partner,
                        p.output_type,
                        p.geographies
                    FROM projects p
                    WHERE 1=1
                """
                params = []
            
            # Add filters
            if research_areas:
                # JSON array contains any of the research areas
                conditions = " OR ".join(["p.research_areas LIKE ?" for _ in research_areas])
                sql += f" AND ({conditions})"
                params.extend([f'%{area}%' for area in research_areas])
            
            if geographies:
                conditions = " OR ".join(["p.geographies LIKE ?" for _ in geographies])
                sql += f" AND ({conditions})"
                params.extend([f'%{geo}%' for geo in geographies])
            
            if output_types:
                placeholders = ",".join(["?" for _ in output_types])
                sql += f" AND p.output_type IN ({placeholders})"
                params.extend(output_types)
            
            if po_contacts:
                placeholders = ",".join(["?" for _ in po_contacts])
                sql += f" AND p.po_contact IN ({placeholders})"
                params.extend(po_contacts)
            
            if agdev_partners:
                conditions = " OR ".join(["p.agdev_partner LIKE ?" for _ in agdev_partners])
                sql += f" AND ({conditions})"
                params.extend([f'%{partner}%' for partner in agdev_partners])
            
            if date_from:
                sql += " AND p.date_completion >= ?"
                params.append(date_from)
            
            if date_to:
                sql += " AND p.date_completion <= ?"
                params.append(date_to)
            
            # Add ordering and pagination
            sql += " ORDER BY p.date_completion DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            logger.info(f"Executing search query: {sql[:100]}... with {len(params)} params")
            cursor.execute(sql, params)
            
            projects_dict = {}
            for row in cursor.fetchall():
                project_id = row['project_id']
                
                if project_id not in projects_dict:
                    projects_dict[project_id] = {
                        'id': project_id,
                        'projectCode': row['project_code'],
                        'title': row['title'],
                        'researchAreas': json.loads(row['research_areas']) if row['research_areas'] else [],
                        'dateInitialRequest': row['date_initial_request'],
                        'dateCompletion': row['date_completion'],
                        'poContact': row['po_contact'],
                        'otherPos': json.loads(row['other_pos']) if row['other_pos'] else [],
                        'agdevPartner': row['agdev_partner'],
                        'outputType': row['output_type'],
                        'geographies': json.loads(row['geographies']) if row['geographies'] else [],
                        'files': []
                    }
            
            # Get files for each project
            if projects_dict:
                project_ids = list(projects_dict.keys())
                placeholders = ",".join(["?" for _ in project_ids])
                
                cursor.execute(f"""
                    SELECT 
                        id,
                        project_id,
                        file_name,
                        file_type,
                        file_size,
                        blob_path
                    FROM files
                    WHERE project_id IN ({placeholders})
                    ORDER BY file_name
                """, project_ids)
                
                for row in cursor.fetchall():
                    project_id = row['project_id']
                    file_size_mb = f"{row['file_size'] / 1024 / 1024:.1f} MB" if row['file_size'] else "Unknown"
                    
                    projects_dict[project_id]['files'].append({
                        'id': row['id'],
                        'name': row['file_name'],
                        'type': row['file_type'],
                        'size': file_size_mb,
                        'blobPath': row['blob_path']
                    })
            
            results = list(projects_dict.values())
            logger.info(f"Search returned {len(results)} projects")
            
            return results
            
        except Exception as e:
            logger.error(f"Database search error: {str(e)}")
            raise
        finally:
            conn.close()
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        Get file metadata by ID.
        
        Args:
            file_id: File ID
        
        Returns:
            File metadata dict or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    f.id,
                    f.file_name,
                    f.file_type,
                    f.file_size,
                    f.blob_path,
                    p.project_code
                FROM files f
                INNER JOIN projects p ON f.project_id = p.id
                WHERE f.id = ?
            """, (file_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            file_size_mb = f"{row['file_size'] / 1024 / 1024:.1f} MB" if row['file_size'] else "Unknown"
            
            return {
                'id': row['id'],
                'name': row['file_name'],
                'type': row['file_type'],
                'size': file_size_mb,
                'blobPath': row['blob_path'],
                'projectCode': row['project_code']
            }
            
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {str(e)}")
            raise
        finally:
            conn.close()


# Global instance
db_helper = DatabaseHelper()


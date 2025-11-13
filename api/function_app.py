"""
EPAR Data Portal - Azure Functions API
Backend API for searching and downloading EPAR documents.
"""

import azure.functions as func
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from datetime import timedelta

# Add parent directory to path to import config
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import config
try:
    from config import config
    USE_AZURE_STORAGE = config.use_azure_storage
    logger = logging.getLogger(__name__)
    if USE_AZURE_STORAGE:
        logger.info("Azure Storage mode: ENABLED (will generate real SAS URLs)")
    else:
        logger.info("Azure Storage mode: DISABLED (using mock data)")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not load config: {e}. Using mock mode.")
    USE_AZURE_STORAGE = False

# Import database helper
try:
    # Try importing from api subdirectory first (when running from parent)
    try:
        from api.db_helper import db_helper
    except ImportError:
        # If that fails, try importing directly (when running from api/)
        from db_helper import db_helper
    USE_DATABASE = True
    logger.info("Database helper loaded successfully")
except Exception as e:
    logger.warning(f"Could not load database helper: {e}. Using mock data.")
    USE_DATABASE = False

# Import Azure Storage SDK only if needed
if USE_AZURE_STORAGE:
    try:
        from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
        logger.info("Azure Storage SDK loaded successfully")
    except ImportError:
        logger.warning("Azure Storage SDK not available. Falling back to mock mode.")
        USE_AZURE_STORAGE = False

app = func.FunctionApp()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# MOCK DATA (Temporary - will be replaced with database in Step 5)
# ============================================================================

MOCK_PROJECTS = [
    {
        "id": 1,
        "projectCode": "EPAR-2024-015",
        "title": "Agricultural Market Systems in Kenya",
        "researchAreas": ["Agricultural Economics", "Market Systems"],
        "dateInitialRequest": "2024-01",
        "dateCompletion": "2024-08",
        "poContact": "Sarah Johnson",
        "otherPos": ["Michael Chen"],
        "agdevPartner": "Kenya Agricultural Research Institute",
        "outputType": "Final Report",
        "geographies": ["Kenya"],
        "files": [
            {"id": 1, "name": "Final_Report.pdf", "type": "pdf", "size": "2.4 MB", "blobPath": "epar-2024-015/Final_Report.pdf"},
            {"id": 2, "name": "Data_Analysis.xlsx", "type": "xlsx", "size": "1.1 MB", "blobPath": "epar-2024-015/Data_Analysis.xlsx"},
        ]
    },
    {
        "id": 2,
        "projectCode": "EPAR-2024-012",
        "title": "Smallholder Farmer Productivity in Tanzania",
        "researchAreas": ["Agricultural Economics", "Rural Development"],
        "dateInitialRequest": "2024-02",
        "dateCompletion": "2024-07",
        "poContact": "Michael Chen",
        "otherPos": [],
        "agdevPartner": "Tanzania Agricultural Development Bank",
        "outputType": "Research Brief",
        "geographies": ["Tanzania"],
        "files": [
            {"id": 3, "name": "Research_Brief.pdf", "type": "pdf", "size": "1.8 MB", "blobPath": "epar-2024-012/Research_Brief.pdf"},
        ]
    },
    {
        "id": 3,
        "projectCode": "EPAR-2023-089",
        "title": "Gender and Agricultural Extension Services",
        "researchAreas": ["Gender Studies", "Agricultural Extension"],
        "dateInitialRequest": "2023-05",
        "dateCompletion": "2023-12",
        "poContact": "Sarah Johnson",
        "otherPos": ["Emily Rodriguez"],
        "agdevPartner": "International Food Policy Research Institute",
        "outputType": "Final Report",
        "geographies": ["Kenya", "Tanzania", "Uganda"],
        "files": [
            {"id": 4, "name": "Final_Report.pdf", "type": "pdf", "size": "3.2 MB", "blobPath": "epar-2023-089/Final_Report.pdf"},
            {"id": 5, "name": "Survey_Data.xlsx", "type": "xlsx", "size": "2.5 MB", "blobPath": "epar-2023-089/Survey_Data.xlsx"},
        ]
    },
]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route(route="search", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def search(req: func.HttpRequest) -> func.HttpResponse:
    """
    Search for EPAR projects.

    Query Parameters:
    - q: Search query (searches across title, project code, research areas, etc.)
    - researchAreas: Comma-separated list of research areas
    - geographies: Comma-separated list of geographies
    - outputTypes: Comma-separated list of output types
    - poContacts: Comma-separated list of PO contacts
    - dateFrom: Start date (YYYY-MM format)
    - dateTo: End date (YYYY-MM format)

    Returns:
    - JSON with results array and total count
    """
    logger.info('Search API called')

    try:
        # Get query parameters
        search_query = req.params.get('q', '')
        research_areas = req.params.get('researchAreas', '').split(',') if req.params.get('researchAreas') else []
        geographies = req.params.get('geographies', '').split(',') if req.params.get('geographies') else []
        output_types = req.params.get('outputTypes', '').split(',') if req.params.get('outputTypes') else []
        po_contacts = req.params.get('poContacts', '').split(',') if req.params.get('poContacts') else []

        # Clean up filter lists (remove empty strings)
        research_areas = [ra.strip() for ra in research_areas if ra.strip()]
        geographies = [g.strip() for g in geographies if g.strip()]
        output_types = [ot.strip() for ot in output_types if ot.strip()]
        po_contacts = [pc.strip() for pc in po_contacts if pc.strip()]

        # Use database if available, otherwise fall back to mock data
        if USE_DATABASE:
            # Query database
            results = db_helper.search_files(
                query=search_query if search_query else None,
                research_areas=research_areas if research_areas else None,
                geographies=geographies if geographies else None,
                output_types=output_types if output_types else None,
                po_contacts=po_contacts if po_contacts else None
            )
        else:
            # Fall back to mock data
            results = MOCK_PROJECTS

            # Apply search query
            if search_query:
                search_lower = search_query.lower()
                results = [
                    p for p in results
                    if (search_lower in p['title'].lower() or
                        search_lower in p['projectCode'].lower() or
                        any(search_lower in area.lower() for area in p['researchAreas']) or
                        any(search_lower in geo.lower() for geo in p['geographies']) or
                        search_lower in p['poContact'].lower())
                ]

            # Apply filters (OR within category, AND between categories)
            if research_areas:
                results = [p for p in results if any(ra in p['researchAreas'] for ra in research_areas)]

            if geographies:
                results = [p for p in results if any(g in p['geographies'] for g in geographies)]

            if output_types:
                results = [p for p in results if p['outputType'] in output_types]

            if po_contacts:
                results = [p for p in results if p['poContact'] in po_contacts]

        # Return results
        response_data = {
            "results": results,
            "total": len(results),
            "query": {
                "q": search_query,
                "researchAreas": research_areas,
                "geographies": geographies,
                "outputTypes": output_types,
                "poContacts": po_contacts
            }
        }

        logger.info(f'Search returned {len(results)} results')

        return func.HttpResponse(
            body=json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",  # CORS for frontend
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    except Exception as e:
        logger.error(f'Search error: {str(e)}')
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="download", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def download(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate a temporary download URL for a file.

    Query Parameters:
    - fileId: ID of the file to download

    Returns:
    - JSON with download URL and file metadata
    """
    logger.info('Download API called')

    try:
        file_id = req.params.get('fileId')

        if not file_id:
            return func.HttpResponse(
                body=json.dumps({"error": "fileId parameter is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Get file from database or mock data
        file_id = int(file_id)

        if USE_DATABASE:
            # Query database
            file_info = db_helper.get_file_by_id(file_id)
        else:
            # Fall back to mock data
            file_info = None
            for project in MOCK_PROJECTS:
                for file in project['files']:
                    if file['id'] == file_id:
                        file_info = file
                        break
                if file_info:
                    break

        if not file_info:
            return func.HttpResponse(
                body=json.dumps({"error": "File not found"}),
                mimetype="application/json",
                status_code=404
            )

        # Generate download URL based on configuration
        if USE_AZURE_STORAGE:
            # REAL AZURE STORAGE MODE: Generate SAS URL
            try:
                blob_service_client = BlobServiceClient.from_connection_string(
                    config.blob_connection_string
                )

                # Get blob client
                blob_client = blob_service_client.get_blob_client(
                    container=config.blob_container,
                    blob=file_info['blobPath']
                )

                # Extract account key from connection string
                conn_str = config.blob_connection_string
                account_key = None
                for part in conn_str.split(';'):
                    if part.startswith('AccountKey='):
                        account_key = part.split('=', 1)[1]
                        break

                if not account_key:
                    raise ValueError("Could not extract AccountKey from connection string")

                # Generate SAS token (valid for 1 hour)
                sas_token = generate_blob_sas(
                    account_name=blob_client.account_name,
                    container_name=config.blob_container,
                    blob_name=file_info['blobPath'],
                    account_key=account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.datetime.utcnow() + timedelta(hours=1)
                )

                download_url = f"{blob_client.url}?{sas_token}"
                logger.info(f'Generated real SAS URL for file {file_id}')

            except Exception as e:
                logger.error(f'Error generating SAS URL: {str(e)}')
                return func.HttpResponse(
                    body=json.dumps({"error": f"Failed to generate download URL: {str(e)}"}),
                    mimetype="application/json",
                    status_code=500
                )
        else:
            # MOCK MODE: Return mock URL with explanation
            download_url = f"#mock-download-{file_id}"
            logger.info(f'Generated mock download URL for file {file_id} (Azure Storage not configured)')

        response_data = {
            "download_url": download_url,
            "filename": file_info['name'],
            "size": file_info['size'],
            "type": file_info['type'],
            "expires_in": 3600,  # 1 hour
            "mode": "azure" if USE_AZURE_STORAGE else "mock"  # Tell frontend which mode
        }

        logger.info(f'Generated download URL for file {file_id}')

        return func.HttpResponse(
            body=json.dumps(response_data),
            mimetype="application/json",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",  # CORS for frontend
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    except ValueError:
        return func.HttpResponse(
            body=json.dumps({"error": "Invalid fileId"}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logger.error(f'Download error: {str(e)}')
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="upload", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def upload(req: func.HttpRequest) -> func.HttpResponse:
    """
    Upload project files and metadata.

    Form Data:
    - projectCode: Project code (required)
    - title: Project title (required)
    - researchAreas: JSON array of research areas
    - geographies: JSON array of geographies
    - outputType: Type of output (required)
    - poContact: Primary contact (required)
    - otherPos: JSON array of other contacts
    - agdevPartner: AgDev partner organization
    - dateInitialRequest: Date of initial request (YYYY-MM format)
    - dateCompletion: Date of completion (YYYY-MM format, required)
    - file_0, file_1, ...: Files to upload

    Returns:
    - JSON with project ID and uploaded file information
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    try:
        # Parse form data
        form_data = req.form
        files = req.files

        logger.info(f"Upload request received with {len(files)} files")

        # Extract and validate required fields
        project_code = form_data.get('projectCode')
        title = form_data.get('title')
        output_type = form_data.get('outputType')
        po_contact = form_data.get('poContact')
        date_completion = form_data.get('dateCompletion')

        if not all([project_code, title, output_type, po_contact, date_completion]):
            return func.HttpResponse(
                body=json.dumps({"error": "Missing required fields"}),
                mimetype="application/json",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "http://localhost:5173"
                }
            )

        # Extract optional fields
        research_areas = json.loads(form_data.get('researchAreas', '[]'))
        geographies = json.loads(form_data.get('geographies', '[]'))
        other_pos = json.loads(form_data.get('otherPos', '[]'))
        agdev_partner = form_data.get('agdevPartner', '')
        date_initial_request = form_data.get('dateInitialRequest', '')

        # Validate files
        if len(files) == 0:
            return func.HttpResponse(
                body=json.dumps({"error": "No files uploaded"}),
                mimetype="application/json",
                status_code=400,
                headers={
                    "Access-Control-Allow-Origin": "http://localhost:5173"
                }
            )

        # Process files and save to database
        if USE_DATABASE:
            # Insert project into database
            import sqlite3
            conn = db_helper.get_connection()
            cursor = conn.cursor()

            try:
                # Insert project
                cursor.execute("""
                    INSERT INTO projects (
                        project_code, title, research_areas, date_initial_request,
                        date_completion, po_contact, other_pos, agdev_partner,
                        output_type, geographies
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_code,
                    title,
                    json.dumps(research_areas),
                    date_initial_request,
                    date_completion,
                    po_contact,
                    json.dumps(other_pos),
                    agdev_partner,
                    output_type,
                    json.dumps(geographies)
                ))

                project_id = cursor.lastrowid
                uploaded_files = []

                # Process each file
                for file_key in files:
                    file = files[file_key]
                    file_name = file.filename
                    file_content = file.read()
                    file_size = len(file_content)
                    file_type = file_name.split('.')[-1].lower() if '.' in file_name else 'unknown'

                    # Generate blob path
                    blob_path = f"{project_code}/{file_name}"

                    # Upload to Azure Storage if configured
                    if USE_AZURE_STORAGE:
                        try:
                            from azure.storage.blob import BlobServiceClient
                            blob_service_client = BlobServiceClient.from_connection_string(config.blob_connection_string)
                            container_client = blob_service_client.get_container_client(config.blob_container)

                            # Upload file
                            blob_client = container_client.get_blob_client(blob_path)
                            blob_client.upload_blob(file_content, overwrite=True)

                            logger.info(f"Uploaded {file_name} to Azure Storage: {blob_path}")
                        except Exception as e:
                            logger.error(f"Azure upload error: {str(e)}")
                            # Continue anyway - file metadata will be saved

                    # Insert file metadata into database
                    cursor.execute("""
                        INSERT INTO files (
                            project_id, file_name, file_type, file_size, blob_path
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (project_id, file_name, file_type, file_size, blob_path))

                    file_id = cursor.lastrowid

                    uploaded_files.append({
                        'id': file_id,
                        'name': file_name,
                        'type': file_type,
                        'size': file_size,
                        'blobPath': blob_path
                    })

                conn.commit()

                logger.info(f"Project {project_code} uploaded successfully with {len(uploaded_files)} files")

                return func.HttpResponse(
                    body=json.dumps({
                        "success": True,
                        "projectId": project_id,
                        "projectCode": project_code,
                        "filesUploaded": len(uploaded_files),
                        "files": uploaded_files,
                        "mode": "azure" if USE_AZURE_STORAGE else "local"
                    }),
                    mimetype="application/json",
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": "http://localhost:5173",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type"
                    }
                )

            except Exception as e:
                conn.rollback()
                raise
            finally:
                conn.close()
        else:
            # Mock mode - just return success
            return func.HttpResponse(
                body=json.dumps({
                    "success": True,
                    "projectCode": project_code,
                    "filesUploaded": len(files),
                    "mode": "mock",
                    "message": "Upload simulated (database not configured)"
                }),
                mimetype="application/json",
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "http://localhost:5173",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )

    except Exception as e:
        logger.error(f'Upload error: {str(e)}')
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173"
            }
        )
# EPAR Data Portal - System Constants
# Define once, use everywhere

# Resource naming
RESOURCE_PREFIX = "epar-ar"  # Replace with your initials, e.g., "epar-js"
BLOB_CONTAINER = "docs"

# Database
LOCAL_DB_PATH = "./db/docs.sqlite"

# Content processing limits
MAX_TEXT_BYTES_PER_DOC = 3000  # For search indexing (privacy + performance)

# Supported file types (initial set)
SUPPORTED_FILETYPES = [".pdf", ".txt", ".md", ".docx", ".xlsx"]

# Security
REQUIRE_AUTH_FOR_DOWNLOADS = True

# Rate limiting (requests per minute)
DOWNLOAD_RATE_LIMIT = 30
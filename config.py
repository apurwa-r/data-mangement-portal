"""
EPAR Data Portal - Configuration Loader
Loads configuration from environment variables with fallback to .env files
"""

import os
from pathlib import Path
from typing import List


def str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ('true', '1', 'yes', 'on')


def load_env_file(env_file: str = '.env.dev') -> None:
    """
    Load environment variables from a file.
    Simple implementation without external dependencies.
    """
    # Try current directory first
    env_path = Path(env_file)

    # If not found, try parent directory (for when running from api/ subdirectory)
    if not env_path.exists():
        env_path = Path(__file__).parent / env_file

    if not env_path.exists():
        print(f"Warning: {env_file} not found. Using environment variables only.")
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value


class Config:
    """Configuration class that loads from environment variables."""
    
    def __init__(self, env_file: str = '.env.dev'):
        """Initialize configuration by loading from env file."""
        load_env_file(env_file)
    
    @property
    def db_path(self) -> str:
        """Database file path."""
        db_path = os.getenv('DB_PATH', './db/docs.sqlite')
        # Convert to absolute path relative to config.py location
        if not Path(db_path).is_absolute():
            db_path = str(Path(__file__).parent / db_path)
        return db_path
    
    @property
    def require_auth(self) -> bool:
        """Whether authentication is required for downloads."""
        return str_to_bool(os.getenv('REQUIRE_AUTH', 'true'))
    
    @property
    def max_abstract_bytes(self) -> int:
        """Maximum bytes to extract for search indexing."""
        return int(os.getenv('MAX_ABSTRACT_BYTES', '3000'))
    
    @property
    def supported_extensions(self) -> List[str]:
        """List of supported file extensions."""
        ext_str = os.getenv('SUPPORTED_EXT', '.pdf,.txt,.md,.docx,.xlsx')
        return [ext.strip() for ext in ext_str.split(',')]
    
    @property
    def blob_container(self) -> str:
        """Azure Blob Storage container name."""
        return os.getenv('BLOB_CONTAINER', 'docs')
    
    @property
    def blob_connection_string(self) -> str:
        """Azure Blob Storage connection string."""
        conn_str = os.getenv('BLOB_CONN', '')
        if not conn_str or 'YOUR_ACCOUNT' in conn_str:
            raise ValueError(
                "BLOB_CONN not configured. "
                "Please set your Azure Storage connection string in .env.dev"
            )
        return conn_str

    @property
    def use_azure_storage(self) -> bool:
        """Check if Azure Storage is configured (vs mock mode)."""
        conn_str = os.getenv('BLOB_CONN', '')
        # If BLOB_CONN is empty, "MOCK", or contains placeholder text, use mock mode
        if not conn_str or conn_str.upper() == 'MOCK' or 'YOUR_ACCOUNT' in conn_str:
            return False
        # If it looks like a real connection string, use Azure
        if 'AccountName=' in conn_str and 'AccountKey=' in conn_str:
            return True
        return False
    
    @property
    def download_rate_limit(self) -> int:
        """Download rate limit (requests per minute)."""
        return int(os.getenv('DOWNLOAD_RATE_LIMIT', '30'))
    
    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv('LOG_LEVEL', 'INFO')


# Global config instance
config = Config()


if __name__ == '__main__':
    # Test configuration loading
    print("Configuration loaded successfully:")
    print(f"  DB Path: {config.db_path}")
    print(f"  Require Auth: {config.require_auth}")
    print(f"  Max Abstract Bytes: {config.max_abstract_bytes}")
    print(f"  Supported Extensions: {config.supported_extensions}")
    print(f"  Blob Container: {config.blob_container}")
    print(f"  Download Rate Limit: {config.download_rate_limit}")
    print(f"  Log Level: {config.log_level}")
    
    try:
        conn_str = config.blob_connection_string
        # Mask the connection string for security
        if 'AccountKey=' in conn_str:
            masked = conn_str.split('AccountKey=')[0] + 'AccountKey=***'
            print(f"  Blob Connection: {masked}")
        else:
            print(f"  Blob Connection: {conn_str[:50]}...")
    except ValueError as e:
        print(f"  Blob Connection: Not configured - {e}")


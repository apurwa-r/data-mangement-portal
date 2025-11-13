"""
Test Azure Storage connection and basic operations.
This script verifies that we can upload and download files from Azure Blob Storage.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def test_connection():
    """Test basic connection to Azure Storage."""
    print("=" * 60)
    print("Testing Azure Storage Connection")
    print("=" * 60)
    
    try:
        # Create BlobServiceClient
        print(f"\n1. Connecting to Azure Storage...")
        print(f"   Container: {config.blob_container}")
        
        blob_service_client = BlobServiceClient.from_connection_string(
            config.blob_connection_string
        )
        
        # Get container client
        container_client = blob_service_client.get_container_client(config.blob_container)
        
        # Check if container exists
        print(f"\n2. Checking if container '{config.blob_container}' exists...")
        if not container_client.exists():
            print(f"   ❌ Container '{config.blob_container}' does not exist!")
            print(f"   Creating container...")
            container_client.create_container()
            print(f"   ✅ Container created successfully!")
        else:
            print(f"   ✅ Container exists!")
        
        # Create a test file
        print(f"\n3. Creating test file...")
        test_content = "Hello from EPAR Data Portal! This is a test file."
        test_filename = "test_upload.txt"
        
        # Upload test file
        print(f"\n4. Uploading test file '{test_filename}'...")
        blob_client = blob_service_client.get_blob_client(
            container=config.blob_container,
            blob=test_filename
        )
        blob_client.upload_blob(test_content, overwrite=True)
        print(f"   ✅ File uploaded successfully!")
        
        # Download test file
        print(f"\n5. Downloading test file...")
        download_data = blob_client.download_blob().readall()
        downloaded_content = download_data.decode('utf-8')
        print(f"   Downloaded content: '{downloaded_content}'")
        
        # Verify content matches
        if downloaded_content == test_content:
            print(f"   ✅ Content matches! Upload/Download working correctly!")
        else:
            print(f"   ❌ Content mismatch!")
            return False
        
        # List blobs in container
        print(f"\n6. Listing blobs in container...")
        blob_list = container_client.list_blobs()
        blob_count = 0
        for blob in blob_list:
            blob_count += 1
            print(f"   - {blob.name} ({blob.size} bytes)")
        print(f"   Total blobs: {blob_count}")
        
        # Clean up test file
        print(f"\n7. Cleaning up test file...")
        blob_client.delete_blob()
        print(f"   ✅ Test file deleted!")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Azure Storage is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that your BLOB_CONN in .env.dev is correct")
        print("2. Verify the storage account exists in Azure Portal")
        print("3. Make sure the container name matches BLOB_CONTAINER")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)


"""
Storage Engine for DOX Core Store Service.

Handles file storage operations across different storage backends.
"""

import os
import hashlib
import shutil
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, BinaryIO
from abc import ABC, abstractmethod

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from .config import Config


class StorageEngine(ABC):
    """Abstract base class for storage engines."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize storage engine."""
        self.config = config
        self._initialize()

    @abstractmethod
    def _initialize(self):
        """Initialize storage backend."""
        pass

    @abstractmethod
    def store_file(self, file_content: BinaryIO, filename: str,
                     file_hash: str, metadata: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Store file and return storage location and metadata."""
        pass

    @abstractmethod
    def retrieve_file(self, file_path: str) -> Tuple[BinaryIO, Dict[str, Any]]:
        """Retrieve file content and metadata."""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information (size, modified time, etc.)."""
        pass

    def calculate_file_hash(self, file_content: BinaryIO) -> str:
        """Calculate SHA256 hash of file content."""
        sha256_hash = hashlib.sha256()
        file_content.seek(0)
        for chunk in iter(lambda: file_content.read(4096), b""):
            sha256_hash.update(chunk)
        file_content.seek(0)
        return f"sha256:{sha256_hash.hexdigest()}"

    def generate_file_path(self, filename: str, document_id: str = None) -> str:
        """Generate unique file path for storage."""
        # Create date-based directory structure
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")

        # Use document_id if provided, otherwise generate unique ID
        unique_id = document_id or str(uuid.uuid4())

        # Generate file path
        name, ext = os.path.splitext(filename)
        safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_')).rstrip()

        return f"{date_path}/{unique_id}/{safe_name}{ext}"

    def validate_file(self, file_content: BinaryIO, filename: str) -> Tuple[bool, str]:
        """Validate file before storage."""
        # Check file size
        file_content.seek(0, 2)  # Seek to end
        file_size = file_content.tell()
        file_content.seek(0)

        max_size = self.config["max_file_size_mb"] * 1024 * 1024
        if file_size > max_size:
            return False, f"File size {file_size} exceeds maximum {max_size} bytes"

        # Check file extension
        _, ext = os.path.splitext(filename.lower())
        allowed_extensions = self.config.get("allowed_extensions", [])
        if ext and ext not in allowed_extensions:
            return False, f"File extension {ext} not allowed"

        return True, "File validation passed"


class LocalStorageEngine(StorageEngine):
    """Local filesystem storage engine."""

    def _initialize(self):
        """Initialize local storage."""
        storage_path = self.config["path"]
        os.makedirs(storage_path, exist_ok=True)

        # Create subdirectories
        os.makedirs(os.path.join(storage_path, "documents"), exist_ok=True)
        os.makedirs(os.path.join(storage_path, "quarantine"), exist_ok=True)
        os.makedirs(os.path.join(storage_path, "temp"), exist_ok=True)

    def store_file(self, file_content: BinaryIO, filename: str,
                     file_hash: str, metadata: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Store file in local filesystem."""
        # Validate file
        is_valid, validation_message = self.validate_file(file_content, filename)
        if not is_valid:
            raise ValueError(validation_message)

        # Generate unique file path
        file_path = self.generate_file_path(filename, metadata.get("document_id") if metadata else None)
        full_path = os.path.join(self.config["path"], file_path)

        # Create directory
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Store file
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_content, f)

        # Store metadata
        metadata_path = full_path + ".metadata.json"
        full_metadata = {
            "filename": filename,
            "file_path": file_path,
            "file_hash": file_hash,
            "file_size": os.path.getsize(full_path),
            "content_type": metadata.get("content_type", "application/octet-stream"),
            "uploaded_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        with open(metadata_path, 'w') as f:
            import json
            json.dump(full_metadata, f, indent=2)

        return file_path, full_metadata

    def retrieve_file(self, file_path: str) -> Tuple[BinaryIO, Dict[str, Any]]:
        """Retrieve file from local filesystem."""
        full_path = os.path.join(self.config["path"], file_path)
        metadata_path = full_path + ".metadata.json"

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read metadata
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {"filename": os.path.basename(file_path)}

        # Read file content
        file_obj = open(full_path, 'rb')
        return file_obj, metadata

    def delete_file(self, file_path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = os.path.join(self.config["path"], file_path)
        metadata_path = full_path + ".metadata.json"

        deleted = False

        # Delete file
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted = True

        # Delete metadata
        if os.path.exists(metadata_path):
            os.remove(metadata_path)

        return deleted

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local storage."""
        full_path = os.path.join(self.config["path"], file_path)
        return os.path.exists(full_path)

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information from local storage."""
        full_path = os.path.join(self.config["path"], file_path)

        if not os.path.exists(full_path):
            return None

        stat = os.stat(full_path)
        metadata_path = full_path + ".metadata.json"

        # Load metadata if available
        metadata = {}
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

        return {
            "file_path": file_path,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_at": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "metadata": metadata
        }


class S3StorageEngine(StorageEngine):
    """Amazon S3 storage engine."""

    def _initialize(self):
        """Initialize S3 storage."""
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage")

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.config["aws_access_key_id"],
            aws_secret_access_key=self.config["aws_secret_access_key"],
            region_name=self.config["aws_region"]
        )

        self.bucket_name = self.config["s3_bucket"]

        # Ensure bucket exists
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': {
                            'LocationConstraint': self.config["aws_region"]
                        }
                    }
                )
                print(f"✅ Created S3 bucket: {self.bucket_name}")
            except ClientError as e:
                raise RuntimeError(f"Failed to create S3 bucket: {e}")

    def store_file(self, file_content: BinaryIO, filename: str,
                     file_hash: str, metadata: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Store file in S3."""
        # Validate file
        is_valid, validation_message = self.validate_file(file_content, filename)
        if not is_valid:
            raise ValueError(validation_message)

        # Generate unique file path
        file_path = self.generate_file_path(filename, metadata.get("document_id") if metadata else None)

        # Prepare S3 metadata
        s3_metadata = {
            "Content-Type": metadata.get("content_type", "application/octet-stream"),
            "x-amz-meta-filename": filename,
            "x-amz-meta-file-hash": file_hash,
            "x-amz-meta-uploaded-at": datetime.utcnow().isoformat(),
            "x-amz-meta-document-id": metadata.get("document_id", ""),
        }

        # Add custom metadata
        if metadata:
            for key, value in metadata.items():
                if key != "content_type":
                    s3_metadata[f"x-amz-meta-{key}"] = str(value)

        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                Metadata=s3_metadata,
                ServerSideEncryption=self.config.get("s3_encryption", "AES256")
            )
        except Exception as e:
            raise RuntimeError(f"Failed to upload to S3: {e}")

        full_metadata = {
            "filename": filename,
            "file_path": file_path,
            "file_hash": file_hash,
            "content_type": metadata.get("content_type", "application/octet-stream"),
            "uploaded_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "storage_type": "s3",
            "bucket": self.bucket_name
        }

        return f"s3://{self.bucket_name}/{file_path}", full_metadata

    def retrieve_file(self, file_path: str) -> Tuple[BinaryIO, Dict[str, Any]]:
        """Retrieve file from S3."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve from S3: {e}")

        file_content = response['Body']

        # Extract metadata
        metadata = {
            "filename": response.get("Metadata", {}).get("x-amz-meta-filename", ""),
            "file_hash": response.get("Metadata", {}).get("x-amz-meta-file-hash", ""),
            "uploaded_at": response.get("Metadata", {}).get("x-amz-meta-uploaded-at", ""),
            "document_id": response.get("Metadata", {}).get("x-amz-meta-document-id", ""),
            "storage_type": "s3",
            "bucket": self.bucket_name
        }

        # Add custom metadata
        custom_metadata = {key[12:]: value for key, value in response.get("Metadata", {}).items() if key.startswith("x-amz-meta-")}
        metadata["metadata"] = custom_metadata

        file_obj = response['Body']
        return file_obj, metadata

    def delete_file(self, file_path: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except Exception as e:
            print(f"Failed to delete from S3: {e}")
            return False

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
        except:
            return False

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information from S3."""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
        except:
            return None

        return {
            "file_path": file_path,
            "size": response.get("ContentLength", 0),
            "last_modified": response.get("LastModified", ""),
            "storage_type": "s3",
            "bucket": self.bucket_name,
            "etag": response.get("ETag", "")
        }


class StorageEngineFactory:
    """Factory for creating storage engines."""

    @staticmethod
    def create_engine(storage_type: str, config: Dict[str, Any]) -> StorageEngine:
        """Create storage engine based on type."""
        engines = {
            "local": LocalStorageEngine,
            "s3": S3StorageEngine,
            "azure": None,  # TODO: Implement AzureStorageEngine
            "gcs": None  # TODO: Implement GCSStorageEngine
        }

        engine_class = engines.get(storage_type.lower())
        if engine_class is None:
            raise ValueError(f"Unsupported storage type: {storage_type}")

        return engine_class(config)


class StorageManager:
    """High-level storage manager."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize storage manager."""
        if config is None:
            from .config import Config
            config = Config.get_storage_config()

        self.config = config
        self.engine = StorageEngineFactory.create_engine(config["type"], config)

    def store_document(self, file_content: BinaryIO, filename: str,
                        document_id: str = None, metadata: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Store document with metadata."""
        # Calculate file hash
        file_hash = self.engine.calculate_file_hash(file_content)

        # Add document_id to metadata
        if metadata is None:
            metadata = {}
        if document_id:
            metadata["document_id"] = document_id

        return self.engine.store_file(file_content, filename, file_hash, metadata)

    def retrieve_document(self, file_path: str) -> Tuple[BinaryIO, Dict[str, Any]]:
        """Retrieve document."""
        return self.engine.retrieve_file(file_path)

    def delete_document(self, file_path: str) -> bool:
        """Delete document."""
        return self.engine.delete_file(file_path)

    def document_exists(self, file_path: str) -> bool:
        """Check if document exists."""
        return self.engine.file_exists(file_path)

    def get_document_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get document information."""
        return self.engine.get_file_info(file_path)
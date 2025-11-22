"""
Configuration for DOX Core Store Service.
"""

import os
from datetime import timedelta


class Config:
    """Configuration class for core store service."""

    # Service Configuration
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "dox-core-store")
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 5000))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Database Configuration
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "dox_core_store")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "dox_user")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "dox_password")
    POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Storage Configuration
    STORAGE_TYPE = os.environ.get("STORAGE_TYPE", "local")  # local, s3, azure, gcs
    STORAGE_PATH = os.environ.get("STORAGE_PATH", "/opt/dox/storage")
    STORAGE_MAX_SIZE_GB = int(os.environ.get("STORAGE_MAX_SIZE_GB", 1000))

    # S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    S3_BUCKET = os.environ.get("S3_BUCKET", "dox-documents")
    S3_ENCRYPTION = os.environ.get("S3_ENCRYPTION", "AES256")

    # Azure Blob Configuration
    AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT")
    AZURE_STORAGE_KEY = os.environ.get("AZURE_STORAGE_KEY")
    AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER", "documents")

    # GCS Configuration
    GCS_PROJECT_ID = os.environ.get("GCS_PROJECT_ID")
    GCS_BUCKET = os.environ.get("GCS_BUCKET", "dox-documents")
    GCS_CREDENTIALS_PATH = os.environ.get("GCS_CREDENTIALS_PATH", "/opt/dox/gcs-credentials.json")

    # File Validation
    MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", 100))
    ALLOWED_EXTENSIONS = os.environ.get("ALLOWED_EXTENSIONS", "pdf,doc,docx,png,jpg,jpeg,tiff,tif").split(",")
    QUARANTINE_ENABLED = os.environ.get("QUARANTINE_ENABLED", "true").lower() == "true"
    QUARANTINE_PATH = os.environ.get("QUARANTINE_PATH", "/opt/dox/quarantine")

    # Metadata Configuration
    METADATA_RETENTION_DAYS = int(os.environ.get("METADATA_RETENTION_DAYS", 365))
    VERSIONING_ENABLED = os.environ.get("VERSIONING_ENABLED", "true").lower() == "true"
    MAX_VERSIONS_PER_DOCUMENT = int(os.environ.get("MAX_VERSIONS_PER_DOCUMENT", 10))

    # Caching Configuration
    CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", 3600))
    CACHE_MAX_SIZE_MB = int(os.environ.get("CACHE_MAX_SIZE_MB", 100))

    # Security Configuration
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://dox-core-auth:5001")
    REQUIRE_AUTH = os.environ.get("REQUIRE_AUTH", "true").lower() == "true"
    API_KEY = os.environ.get("API_KEY", None)
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", None)

    # Monitoring Configuration
    METRICS_ENABLED = os.environ.get("METRICS_ENABLED", "true").lower() == "true"
    HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", 30))

    # Performance Configuration
    MAX_CONCURRENT_UPLOADS = int(os.environ.get("MAX_CONCURRENT_UPLOADS", 50))
    UPLOAD_TIMEOUT_SECONDS = int(os.environ.get("UPLOAD_TIMEOUT_SECONDS", 300))
    THUMBNAIL_ENABLED = os.environ.get("THUMBNAIL_ENABLED", "true").lower() == "true"

    # Backup Configuration
    BACKUP_ENABLED = os.environ.get("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_SCHEDULE = os.environ.get("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", 30))
    BACKUP_S3_BUCKET = os.environ.get("BACKUP_S3_BUCKET", "dox-backups")

    # Notification Configuration
    NOTIFICATION_ENABLED = os.environ.get("NOTIFICATION_ENABLED", "false").lower() == "true"
    NOTIFICATION_WEBHOOK_URL = os.environ.get("NOTIFICATION_WEBHOOK_URL", None)
    NOTIFICATION_EMAIL_SMTP_HOST = os.environ.get("NOTIFICATION_EMAIL_SMTP_HOST")
    NOTIFICATION_EMAIL_SMTP_PORT = int(os.environ.get("NOTIFICATION_EMAIL_SMTP_PORT", 587))
    NOTIFICATION_EMAIL_USERNAME = os.environ.get("NOTIFICATION_EMAIL_USERNAME")
    NOTIFICATION_EMAIL_PASSWORD = os.environ.get("NOTIFICATION_EMAIL_PASSWORD")

    @classmethod
    def validate(cls):
        """Validate configuration values."""
        errors = []

        if cls.STORAGE_TYPE not in ["local", "s3", "azure", "gcs"]:
            errors.append(f"Invalid STORAGE_TYPE: {cls.STORAGE_TYPE}")

        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")

        if cls.POSTGRES_PORT <= 0 or cls.POSTGRES_PORT > 65535:
            errors.append("POSTGRES_PORT must be between 1 and 65535")

        if cls.STORAGE_MAX_SIZE_GB <= 0:
            errors.append("STORAGE_MAX_SIZE_GB must be positive")

        if cls.STORAGE_TYPE == "s3":
            if not cls.AWS_ACCESS_KEY_ID or not cls.AWS_SECRET_ACCESS_KEY:
                errors.append("AWS credentials required for S3 storage")
            if not cls.S3_BUCKET:
                errors.append("S3_BUCKET is required for S3 storage")

        if cls.STORAGE_TYPE == "azure":
            if not cls.AZURE_STORAGE_ACCOUNT or not cls.AZURE_STORAGE_KEY:
                errors.append("Azure credentials required for Azure storage")
            if not cls.AZURE_CONTAINER:
                errors.append("AZURE_CONTAINER is required for Azure storage")

        if cls.STORAGE_TYPE == "gcs":
            if not cls.GCS_PROJECT_ID:
                errors.append("GCS_PROJECT_ID is required for GCS storage")
            if not cls.GCS_BUCKET:
                errors.append("GCS_BUCKET is required for GCS storage")

        if cls.ENCRYPTION_KEY and len(cls.ENCRYPTION_KEY) < 32:
            errors.append("ENCRYPTION_KEY must be at least 32 characters")

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

        return True

    @classmethod
    def get_storage_config(cls):
        """Get storage configuration as dictionary."""
        config = {
            "type": cls.STORAGE_TYPE,
            "path": cls.STORAGE_PATH,
            "max_size_gb": cls.STORAGE_MAX_SIZE_GB,
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "allowed_extensions": cls.ALLOWED_EXTENSIONS,
            "quarantine_enabled": cls.QUARANTINE_ENABLED,
            "quarantine_path": cls.QUARANTINE_PATH
        }

        if cls.STORAGE_TYPE == "s3":
            config.update({
                "aws_access_key_id": cls.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": cls.AWS_SECRET_ACCESS_KEY,
                "aws_region": cls.AWS_REGION,
                "s3_bucket": cls.S3_BUCKET,
                "s3_encryption": cls.S3_ENCRYPTION
            })
        elif cls.STORAGE_TYPE == "azure":
            config.update({
                "azure_storage_account": cls.AZURE_STORAGE_ACCOUNT,
                "azure_storage_key": cls.AZURE_STORAGE_KEY,
                "azure_container": cls.AZURE_CONTAINER
            })
        elif cls.STORAGE_TYPE == "gcs":
            config.update({
                "gcs_project_id": cls.GCS_PROJECT_ID,
                "gcs_bucket": cls.GCS_BUCKET,
                "gcs_credentials_path": cls.GCS_CREDENTIALS_PATH
            })

        return config

    @classmethod
    def get_database_config(cls):
        """Get database configuration as dictionary."""
        return {
            "host": cls.POSTGRES_HOST,
            "port": cls.POSTGRES_PORT,
            "database": cls.POSTGRES_DB,
            "user": cls.POSTGRES_USER,
            "password": cls.POSTGRES_PASSWORD,
            "url": cls.POSTGRES_URL
        }

    @classmethod
    def get_performance_config(cls):
        """Get performance configuration as dictionary."""
        return {
            "max_concurrent_uploads": cls.MAX_CONCURRENT_UPLOADS,
            "upload_timeout_seconds": cls.UPLOAD_TIMEOUT_SECONDS,
            "cache_ttl_seconds": cls.CACHE_TTL_SECONDS,
            "cache_max_size_mb": cls.CACHE_MAX_SIZE_MB,
            "thumbnail_enabled": cls.THUMBNAIL_ENABLED
        }

    @classmethod
    def get_security_config(cls):
        """Get security configuration as dictionary."""
        return {
            "require_auth": cls.REQUIRE_AUTH,
            "auth_service_url": cls.AUTH_SERVICE_URL,
            "encryption_key": cls.ENCRYPTION_KEY,
            "quarantine_enabled": cls.QUARANTINE_ENABLED
        }
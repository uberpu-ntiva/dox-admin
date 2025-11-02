"""
Configuration for DOX Validation Service.
"""

import os
from datetime import timedelta


class Config:
    """Configuration class for validation service."""

    # Service Configuration
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "dox-validation-service")
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 5007))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Redis Configuration
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # PostgreSQL Configuration
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "dox_validation")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "dox_user")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "dox_password")

    # File Validation Configuration
    MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", 50))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = os.environ.get("ALLOWED_EXTENSIONS", "pdf,png,jpg,jpeg,tiff,tif").split(",")
    ALLOWED_MIMETYPES = os.environ.get("ALLOWED_MIMETYPES",
        "application/pdf,image/png,image/jpeg,image/tiff").split(",")

    # Image Validation
    IMAGE_MAX_WIDTH = int(os.environ.get("IMAGE_MAX_WIDTH", 4000))
    IMAGE_MAX_HEIGHT = int(os.environ.get("IMAGE_MAX_HEIGHT", 4000))

    # ClamAV Configuration
    CLAMAV_ENABLED = os.environ.get("CLAMAV_ENABLED", "true").lower() == "true"
    CLAMAV_HOST = os.environ.get("CLAMAV_HOST", "localhost")
    CLAMAV_PORT = int(os.environ.get("CLAMAV_PORT", 3310))
    CLAMAV_TIMEOUT = int(os.environ.get("CLAMAV_TIMEOUT", 30))
    CLAMAV_MAX_FILE_SIZE = int(os.environ.get("CLAMAV_MAX_FILE_SIZE_MB", 100)) * 1024 * 1024

    # Rate Limiting Configuration
    RATE_LIMIT_PER_USER_PER_DAY = int(os.environ.get("RATE_LIMIT_PER_USER_PER_DAY", 100))
    RATE_LIMIT_PER_ACCOUNT_PER_DAY = int(os.environ.get("RATE_LIMIT_PER_ACCOUNT_PER_DAY", 500))
    RATE_LIMIT_WINDOW_HOURS = int(os.environ.get("RATE_LIMIT_WINDOW_HOURS", 24))
    RATE_LIMIT_BYPASS_TOKEN = os.environ.get("RATE_LIMIT_BYPASS_TOKEN", None)

    # Cache Configuration
    SCAN_CACHE_TTL = int(os.environ.get("SCAN_CACHE_TTL", 3600))  # 1 hour
    RATE_LIMIT_CACHE_TTL = int(os.environ.get("RATE_LIMIT_CACHE_TTL", 86400))  # 24 hours

    # Security Configuration
    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://dox-core-auth:5001")
    REQUIRE_AUTH = os.environ.get("REQUIRE_AUTH", "true").lower() == "true"
    API_KEY = os.environ.get("API_KEY", None)

    # Monitoring Configuration
    METRICS_ENABLED = os.environ.get("METRICS_ENABLED", "true").lower() == "true"
    HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", 30))

    # Quarantine Configuration
    QUARANTINE_ENABLED = os.environ.get("QUARANTINE_ENABLED", "true").lower() == "true"
    QUARANTINE_PATH = os.environ.get("QUARANTINE_PATH", "/tmp/quarantine")
    QUARANTINE_RETENTION_DAYS = int(os.environ.get("QUARANTINE_RETENTION_DAYS", 30))

    # Notification Configuration
    NOTIFICATION_ENABLED = os.environ.get("NOTIFICATION_ENABLED", "false").lower() == "true"
    NOTIFICATION_WEBHOOK_URL = os.environ.get("NOTIFICATION_WEBHOOK_URL", None)
    VIRUS_DETECTION_NOTIFY_EMAILS = os.environ.get("VIRUS_DETECTION_NOTIFY_EMAILS", "").split(",") if os.environ.get("VIRUS_DETECTION_NOTIFY_EMAILS") else []

    # Performance Configuration
    MAX_CONCURRENT_SCANS = int(os.environ.get("MAX_CONCURRENT_SCANS", 10))
    SCAN_QUEUE_SIZE = int(os.environ.get("SCAN_QUEUE_SIZE", 100))
    ASYNC_SCAN_ENABLED = os.environ.get("ASYNC_SCAN_ENABLED", "false").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate configuration values."""
        errors = []

        if cls.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")

        if cls.CLAMAV_ENABLED and not cls.CLAMAV_HOST:
            errors.append("CLAMAV_HOST is required when CLAMAV_ENABLED is true")

        if cls.RATE_LIMIT_PER_USER_PER_DAY <= 0:
            errors.append("RATE_LIMIT_PER_USER_PER_DAY must be positive")

        if cls.RATE_LIMIT_PER_ACCOUNT_PER_DAY <= 0:
            errors.append("RATE_LIMIT_PER_ACCOUNT_PER_DAY must be positive")

        if cls.IMAGE_MAX_WIDTH <= 0 or cls.IMAGE_MAX_HEIGHT <= 0:
            errors.append("Image dimensions must be positive")

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

        return True

    @classmethod
    def get_rate_limit_config(cls):
        """Get rate limiting configuration as dictionary."""
        return {
            "per_user_per_day": cls.RATE_LIMIT_PER_USER_PER_DAY,
            "per_account_per_day": cls.RATE_LIMIT_PER_ACCOUNT_PER_DAY,
            "window_hours": cls.RATE_LIMIT_WINDOW_HOURS,
            "cache_ttl": cls.RATE_LIMIT_CACHE_TTL
        }

    @classmethod
    def get_clamav_config(cls):
        """Get ClamAV configuration as dictionary."""
        return {
            "enabled": cls.CLAMAV_ENABLED,
            "host": cls.CLAMAV_HOST,
            "port": cls.CLAMAV_PORT,
            "timeout": cls.CLAMAV_TIMEOUT,
            "max_file_size": cls.CLAMAV_MAX_FILE_SIZE
        }

    @classmethod
    def get_validation_config(cls):
        """Get validation configuration as dictionary."""
        return {
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "max_file_size_bytes": cls.MAX_FILE_SIZE_BYTES,
            "allowed_extensions": cls.ALLOWED_EXTENSIONS,
            "allowed_mimetypes": cls.ALLOWED_MIMETYPES,
            "image_max_width": cls.IMAGE_MAX_WIDTH,
            "image_max_height": cls.IMAGE_MAX_HEIGHT
        }
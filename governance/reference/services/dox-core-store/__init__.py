"""
DOX Core Store Service

Centralized document storage and retrieval service for the DOX platform.
Handles file storage, metadata management, and document lifecycle operations.
"""

from .app import create_app
from .storage_engine import StorageEngine
from .metadata_manager import MetadataManager
from .config import Config

__version__ = "1.0.0"
__author__ = "DOX Infrastructure Team"

__all__ = [
    "create_app",
    "StorageEngine",
    "MetadataManager",
    "Config"
]
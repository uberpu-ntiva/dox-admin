"""
DOX Validation Service

Centralized file validation service providing virus scanning, rate limiting,
and security validation for all DOX platform uploads.
"""

from .app import create_app
from .validators import FileValidator, VirusScanner, RateLimiter
from .config import Config

__version__ = "1.0.0"
__author__ = "DOX Infrastructure Team"

__all__ = [
    "create_app",
    "FileValidator",
    "VirusScanner",
    "RateLimiter",
    "Config"
]
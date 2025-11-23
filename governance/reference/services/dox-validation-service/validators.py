"""
Validation components for DOX Validation Service.

Provides file validation, virus scanning, and rate limiting functionality.
"""

import hashlib
import redis
import logging
import socket
import struct
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    import pyclamd
    CLAMD_AVAILABLE = True
except ImportError:
    CLAMD_AVAILABLE = False

from .config import Config


logger = logging.getLogger(__name__)


class VirusScanner:
    """Virus scanning using ClamAV."""

    def __init__(self):
        """Initialize virus scanner."""
        self.config = Config.get_clamav_config()
        self.clamd_conn = None
        self._initialize_clamav()

    def _initialize_clamav(self):
        """Initialize ClamAV connection."""
        if not self.config["enabled"]:
            logger.info("ClamAV scanning disabled by configuration")
            return

        if not CLAMD_AVAILABLE:
            logger.warning("pyclamd not available, virus scanning disabled")
            return

        try:
            # Try to connect to ClamAV daemon
            self.clamd_conn = pyclamd.ClamdUnixSocket()
            test = self.clamd_conn.ping()
            if test.lower() != 'ok':
                raise Exception("ClamAV ping failed")

            logger.info(f"✅ ClamAV connection established (Unix socket)")

        except Exception:
            try:
                # Fallback to TCP connection
                self.clamd_conn = pyclamd.ClamdNetworkSocket(
                    host=self.config["host"],
                    port=self.config["port"]
                )
                test = self.clamd_conn.ping()
                if test.lower() != 'ok':
                    raise Exception("ClamAV ping failed")

                logger.info(f"✅ ClamAV connection established (TCP: {self.config['host']}:{self.config['port']})")

            except Exception as e:
                logger.error(f"❌ Failed to connect to ClamAV: {e}")
                self.clamd_conn = None

    def scan_file(self, file_path: str, file_hash: str, file_size: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Scan file for viruses.

        Args:
            file_path: Path to file to scan
            file_hash: SHA256 hash of file
            file_size: File size in bytes

        Returns:
            Tuple of (is_clean, scan_result)
        """
        if not self.clamd_conn:
            return True, {
                "scan_result": "clean",
                "scan_time": 0,
                "scanner": "none",
                "message": "ClamAV not available, file assumed clean"
            }

        if file_size > self.config["max_file_size"]:
            logger.warning(f"File too large for virus scan: {file_size} bytes")
            return False, {
                "scan_result": "error",
                "scan_time": 0,
                "scanner": "clamav",
                "message": f"File too large for virus scan (max: {self.config['max_file_size']} bytes)"
            }

        start_time = time.time()

        try:
            # Perform scan
            scan_result = self.clamd_conn.scan_file(file_path)
            scan_time = time.time() - start_time

            if scan_result is None:
                # No threats found
                logger.info(f"✅ Virus scan passed: {file_hash} ({scan_time:.2f}s)")
                return True, {
                    "scan_result": "clean",
                    "scan_time": scan_time,
                    "scanner": "clamav",
                    "file_hash": file_hash,
                    "file_size": file_size,
                    "timestamp": datetime.utcnow().isoformat()
                }

            else:
                # Threat detected
                file_path_result = scan_result.get(file_path, "UNKNOWN")
                threat_name = file_path_result.split('FOUND')[0].strip() if 'FOUND' in file_path_result else file_path_result

                logger.warning(f"🚨 Virus detected: {file_hash} - {threat_name}")
                return False, {
                    "scan_result": "infected",
                    "scan_time": scan_time,
                    "scanner": "clamav",
                    "file_hash": file_hash,
                    "file_size": file_size,
                    "threat_name": threat_name,
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            scan_time = time.time() - start_time
            logger.error(f"❌ Virus scan failed for {file_hash}: {e}")
            return False, {
                "scan_result": "error",
                "scan_time": scan_time,
                "scanner": "clamav",
                "file_hash": file_hash,
                "file_size": file_size,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def health_check(self) -> Dict[str, Any]:
        """Check virus scanner health."""
        if not self.config["enabled"]:
            return {"status": "disabled", "message": "ClamAV scanning disabled"}

        if not self.clamd_conn:
            return {"status": "unhealthy", "message": "ClamAV connection failed"}

        try:
            ping_result = self.clamd_conn.ping()
            version = self.clamd_conn.version()
            return {
                "status": "healthy",
                "ping": ping_result,
                "version": version,
                "connection_type": "tcp" if ":" in str(self.clamd_conn) else "unix_socket"
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class RateLimiter:
    """Rate limiting using Redis."""

    def __init__(self, redis_client):
        """Initialize rate limiter."""
        self.redis_client = redis_client
        self.config = Config.get_rate_limit_config()

    def check_rate_limit(self, user_id: str, account_id: str,
                        window_hours: int = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if user/account is within rate limits.

        Args:
            user_id: User identifier
            account_id: Account identifier
            window_hours: Time window (defaults to config)

        Returns:
            Tuple of (within_limit, limit_info)
        """
        if not self.redis_client:
            return True, {
                "within_limit": True,
                "message": "Rate limiting disabled (Redis not available)",
                "user_count": 0,
                "account_count": 0
            }

        window_hours = window_hours or self.config["window_hours"]
        window_seconds = window_hours * 3600
        current_time = int(time.time())
        window_start = current_time - window_seconds

        try:
            # Check user rate limit
            user_key = f"rate_limit:user:{user_id}"
            user_count = self._count_requests(user_key, window_start, current_time)

            # Check account rate limit
            account_key = f"rate_limit:account:{account_id}"
            account_count = self._count_requests(account_key, window_start, current_time)

            # Check against limits
            user_limit = self.config["per_user_per_day"]
            account_limit = self.config["per_account_per_day"]

            within_user_limit = user_count < user_limit
            within_account_limit = account_count < account_limit
            within_limit = within_user_limit and within_account_limit

            result = {
                "within_limit": within_limit,
                "window_hours": window_hours,
                "user_count": user_count,
                "user_limit": user_limit,
                "account_count": account_count,
                "account_limit": account_limit,
                "timestamp": datetime.utcnow().isoformat()
            }

            if not within_limit:
                if not within_user_limit:
                    result["violation"] = "user_limit_exceeded"
                else:
                    result["violation"] = "account_limit_exceeded"

            return within_limit, result

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, {
                "within_limit": True,
                "message": "Rate limit check failed, allowing request",
                "error": str(e)
            }

    def record_request(self, user_id: str, account_id: str):
        """Record a request for rate limiting."""
        if not self.redis_client:
            return

        try:
            current_time = int(time.time())
            ttl = self.config["cache_ttl"]

            # Record user request
            user_key = f"rate_limit:user:{user_id}"
            self.redis_client.zadd(user_key, {str(current_time): current_time})
            self.redis_client.expire(user_key, ttl)

            # Record account request
            account_key = f"rate_limit:account:{account_id}"
            self.redis_client.zadd(account_key, {str(current_time): current_time})
            self.redis_client.expire(account_key, ttl)

        except Exception as e:
            logger.error(f"Failed to record rate limit request: {e}")

    def _count_requests(self, key: str, window_start: int, window_end: int) -> int:
        """Count requests in time window."""
        try:
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            # Count current entries
            return self.redis_client.zcount(key, window_start, window_end)
        except Exception as e:
            logger.error(f"Failed to count requests for {key}: {e}")
            return 0

    def health_check(self) -> Dict[str, Any]:
        """Check rate limiter health."""
        if not self.redis_client:
            return {"status": "unhealthy", "message": "Redis not available"}

        try:
            # Test Redis connection
            self.redis_client.ping()
            return {"status": "healthy", "redis_available": True}
        except Exception as e:
            return {"status": "unhealthy", "redis_available": False, "error": str(e)}


class FileValidator:
    """Main file validation coordinator."""

    def __init__(self, redis_client=None):
        """Initialize file validator."""
        self.config = Config.get_validation_config()
        self.redis_client = redis_client
        self.virus_scanner = VirusScanner()
        self.rate_limiter = RateLimiter(redis_client) if redis_client else None

    def validate_file(self, file_path: str, original_filename: str,
                     user_id: str = None, account_id: str = None,
                     skip_rate_limit: bool = False) -> Dict[str, Any]:
        """
        Perform complete file validation.

        Args:
            file_path: Path to file to validate
            original_filename: Original filename
            user_id: User ID for rate limiting
            account_id: Account ID for rate limiting
            skip_rate_limit: Skip rate limiting check

        Returns:
            Validation result dictionary
        """
        validation_start = time.time()
        file_hash = self._calculate_file_hash(file_path)

        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            file_ext = Path(original_filename).suffix.lower().lstrip('.')

            # Initialize result
            result = {
                "file_path": file_path,
                "original_filename": original_filename,
                "file_hash": file_hash,
                "file_size": file_size,
                "file_extension": file_ext,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "steps_completed": [],
                "steps_failed": [],
                "final_status": "pending",
                "errors": [],
                "warnings": []
            }

            # Step 1: Check rate limiting
            if not skip_rate_limit and user_id and account_id and self.rate_limiter:
                within_limit, rate_info = self.rate_limiter.check_rate_limit(user_id, account_id)
                if not within_limit:
                    result["steps_failed"].append("rate_limit")
                    result["errors"].append({
                        "step": "rate_limit",
                        "error": "Rate limit exceeded",
                        "details": rate_info
                    })
                    result["final_status"] = "rate_limited"
                    return result

                result["steps_completed"].append("rate_limit")
                result["rate_limit_info"] = rate_info

                # Record this request
                self.rate_limiter.record_request(user_id, account_id)

            # Step 2: File size validation
            if file_size > self.config["max_file_size_bytes"]:
                result["steps_failed"].append("file_size")
                result["errors"].append({
                    "step": "file_size",
                    "error": f"File size {file_size} exceeds maximum {self.config['max_file_size_bytes']}",
                    "provided_size": file_size,
                    "max_allowed": self.config["max_file_size_bytes"]
                })
                result["final_status"] = "size_exceeded"
                return result

            result["steps_completed"].append("file_size")

            # Step 3: File extension validation
            if file_ext not in self.config["allowed_extensions"]:
                result["steps_failed"].append("file_extension")
                result["errors"].append({
                    "step": "file_extension",
                    "error": f"File extension '{file_ext}' not allowed",
                    "provided_extension": file_ext,
                    "allowed_extensions": self.config["allowed_extensions"]
                })
                result["final_status"] = "extension_not_allowed"
                return result

            result["steps_completed"].append("file_extension")

            # Step 4: MIME type validation
            mime_type = self._get_mime_type(file_path)
            if mime_type not in self.config["allowed_mimetypes"]:
                result["steps_failed"].append("mime_type")
                result["errors"].append({
                    "step": "mime_type",
                    "error": f"MIME type '{mime_type}' not allowed",
                    "provided_mime_type": mime_type,
                    "allowed_mime_types": self.config["allowed_mimetypes"]
                })
                result["final_status"] = "mime_type_not_allowed"
                return result

            result["steps_completed"].append("mime_type")
            result["mime_type"] = mime_type

            # Step 5: Virus scanning
            is_clean, scan_result = self.virus_scanner.scan_file(file_path, file_hash, file_size)
            if not is_clean:
                result["steps_failed"].append("virus_scan")
                result["errors"].append({
                    "step": "virus_scan",
                    "error": "Virus detected or scan failed",
                    "details": scan_result
                })
                result["final_status"] = scan_result.get("scan_result", "infected")
                return result

            result["steps_completed"].append("virus_scan")
            result["virus_scan_result"] = scan_result

            # Step 6: Format-specific validation
            format_valid, format_result = self._validate_format_specific(file_path, file_ext)
            if not format_valid:
                result["steps_failed"].append("format_validation")
                result["errors"].append({
                    "step": "format_validation",
                    "error": "Format validation failed",
                    "details": format_result
                })
                result["final_status"] = "format_invalid"
                return result

            result["steps_completed"].append("format_validation")
            result["format_validation_result"] = format_result

            # All validations passed
            result["final_status"] = "valid"
            result["validation_duration"] = time.time() - validation_start

            return result

        except Exception as e:
            result["final_status"] = "error"
            result["errors"].append({
                "step": "general",
                "error": str(e),
                "error_type": "validation_exception"
            })
            return result

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file."""
        if MAGIC_AVAILABLE:
            try:
                return magic.from_file(file_path, mime=True)
            except:
                pass

        # Fallback to extension-based detection
        ext = Path(file_path).suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        return mime_map.get(ext, 'application/octet-stream')

    def _validate_format_specific(self, file_path: str, file_ext: str) -> Tuple[bool, Dict[str, Any]]:
        """Perform format-specific validation."""
        try:
            if file_ext == 'pdf':
                return self._validate_pdf(file_path)
            elif file_ext in ['png', 'jpg', 'jpeg', 'tiff', 'tif']:
                return self._validate_image(file_path)
            else:
                return True, {"message": "No format-specific validation for this extension"}

        except Exception as e:
            return False, {"error": str(e)}

    def _validate_pdf(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate PDF file structure."""
        try:
            # Simple PDF validation - check file signature
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    return False, {"error": "Invalid PDF signature"}

            return True, {"message": "PDF signature valid"}

        except Exception as e:
            return False, {"error": f"PDF validation failed: {e}"}

    def _validate_image(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate image file."""
        try:
            # Check image dimensions if PIL is available
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    width, height = img.size
                    max_width = self.config["image_max_width"]
                    max_height = self.config["image_max_height"]

                    if width > max_width or height > max_height:
                        return False, {
                            "error": f"Image dimensions {width}x{height} exceed maximum {max_width}x{max_height}",
                            "provided_width": width,
                            "provided_height": height,
                            "max_width": max_width,
                            "max_height": max_height
                        }

                    return True, {
                        "message": "Image dimensions valid",
                        "width": width,
                        "height": height,
                        "format": img.format
                    }

            except ImportError:
                return True, {"message": "Image validation skipped (PIL not available)"}

        except Exception as e:
            return False, {"error": f"Image validation failed: {e}"}

    def health_check(self) -> Dict[str, Any]:
        """Check validator health."""
        virus_health = self.virus_scanner.health_check()
        rate_limiter_health = self.rate_limiter.health_check() if self.rate_limiter else {"status": "disabled"}

        return {
            "status": "healthy" if virus_health["status"] == "healthy" else "degraded",
            "components": {
                "virus_scanner": virus_health,
                "rate_limiter": rate_limiter_health,
                "file_validation": {"status": "healthy"}
            },
            "config": {
                "max_file_size_mb": self.config["max_file_size_mb"],
                "allowed_extensions": self.config["allowed_extensions"],
                "image_max_dimensions": f"{self.config['image_max_width']}x{self.config['image_max_height']}"
            }
        }
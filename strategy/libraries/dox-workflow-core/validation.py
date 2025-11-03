"""
File validation utilities.

Provides file validation functions for the 5-step validation workflow.
"""

import os
import hashlib
import mimetypes
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path
import magic  # python-magic for accurate MIME type detection

try:
    import PyPDF2
    from PIL import Image
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

from .exceptions import ValidationError


class FileValidator:
    """File validation with 5-step validation workflow."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize validator with configuration."""
        self.config = config or self._default_config()
        self._validate_dependencies()

    def _default_config(self) -> Dict[str, Any]:
        """Default validation configuration."""
        return {
            "max_file_size_mb": 50,
            "max_file_size_bytes": 50 * 1024 * 1024,  # 50MB
            "allowed_extensions": ["pdf", "png", "jpg", "jpeg", "tiff", "tif"],
            "allowed_mimetypes": [
                "application/pdf",
                "image/png",
                "image/jpeg",
                "image/tiff"
            ],
            "image_max_width": 4000,
            "image_max_height": 4000,
            "enable_pdf_validation": True,
            "enable_image_validation": True,
            "enable_mime_validation": True
        }

    def _validate_dependencies(self):
        """Validate that required dependencies are available."""
        if not DEPENDENCIES_AVAILABLE:
            print("Warning: Some validation dependencies not available. Install with: pip install PyPDF2 Pillow python-magic")

    def validate_file(self, file_path: str, original_filename: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform complete 5-step file validation.

        Returns:
            Tuple of (is_valid, validation_result)
        """
        validation_result = {
            "file_path": file_path,
            "original_filename": original_filename,
            "file_hash": self._calculate_file_hash(file_path),
            "validation_timestamp": None,
            "steps_completed": [],
            "steps_failed": [],
            "final_status": "pending",
            "errors": []
        }

        try:
            # Step 1: Size validation
            if not self._validate_file_size(file_path, validation_result):
                return False, validation_result

            # Step 2: MIME type validation
            if self.config.get("enable_mime_validation", True):
                if not self._validate_mime_type(file_path, original_filename, validation_result):
                    return False, validation_result

            # Step 3: Format-specific validation
            extension = self._get_file_extension(original_filename)
            if extension == "pdf" and self.config.get("enable_pdf_validation", True):
                if not self._validate_pdf_structure(file_path, validation_result):
                    return False, validation_result
            elif extension in ["png", "jpg", "jpeg", "tiff", "tif"] and self.config.get("enable_image_validation", True):
                if not self._validate_image_dimensions(file_path, validation_result):
                    return False, validation_result

            # All validations passed
            validation_result["final_status"] = "passed"
            return True, validation_result

        except Exception as e:
            validation_result["final_status"] = "error"
            validation_result["errors"].append({
                "step": "general",
                "error": str(e),
                "error_type": "validation_exception"
            })
            return False, validation_result

    def _validate_file_size(self, file_path: str, validation_result: Dict[str, Any]) -> bool:
        """Step 1: Validate file size."""
        try:
            file_size = os.path.getsize(file_path)
            max_size = self.config["max_file_size_bytes"]

            if file_size > max_size:
                validation_result["steps_failed"].append("file_size")
                validation_result["errors"].append({
                    "step": "file_size",
                    "error": f"File size {file_size} exceeds maximum {max_size}",
                    "error_type": "size_exceeded",
                    "provided_size": file_size,
                    "max_allowed": max_size
                })
                return False
            else:
                validation_result["steps_completed"].append("file_size")
                validation_result["file_size"] = file_size
                return True

        except OSError as e:
            validation_result["steps_failed"].append("file_size")
            validation_result["errors"].append({
                "step": "file_size",
                "error": f"Cannot read file size: {e}",
                "error_type": "file_access_error"
            })
            return False

    def _validate_mime_type(self, file_path: str, original_filename: str, validation_result: Dict[str, Any]) -> bool:
        """Step 2: Validate MIME type."""
        try:
            # Check file extension
            extension = self._get_file_extension(original_filename)
            if extension not in self.config["allowed_extensions"]:
                validation_result["steps_failed"].append("mime_type")
                validation_result["errors"].append({
                    "step": "mime_type",
                    "error": f"File extension '{extension}' not allowed",
                    "error_type": "extension_not_allowed",
                    "provided_extension": extension,
                    "allowed_extensions": self.config["allowed_extensions"]
                })
                return False

            # Check actual MIME type
            try:
                mime_type = magic.from_file(file_path, mime=True)
            except:
                # Fallback to mimetypes if python-magic not available
                mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type not in self.config["allowed_mimetypes"]:
                validation_result["steps_failed"].append("mime_type")
                validation_result["errors"].append({
                    "step": "mime_type",
                    "error": f"MIME type '{mime_type}' not allowed",
                    "error_type": "mime_type_not_allowed",
                    "provided_mime_type": mime_type,
                    "allowed_mime_types": self.config["allowed_mimetypes"]
                })
                return False

            validation_result["steps_completed"].append("mime_type")
            validation_result["mime_type"] = mime_type
            validation_result["file_extension"] = extension
            return True

        except Exception as e:
            validation_result["steps_failed"].append("mime_type")
            validation_result["errors"].append({
                "step": "mime_type",
                "error": f"MIME type validation failed: {e}",
                "error_type": "mime_validation_error"
            })
            return False

    def _validate_pdf_structure(self, file_path: str, validation_result: Dict[str, Any]) -> bool:
        """Step 3a: Validate PDF structure."""
        if not DEPENDENCIES_AVAILABLE:
            validation_result["steps_completed"].append("pdf_structure")
            validation_result["warnings"].append("PDF validation skipped - dependencies not available")
            return True

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Basic PDF checks
                if len(pdf_reader.pages) == 0:
                    raise ValueError("PDF has no pages")

                # Try to read first page content
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()

                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    raise ValueError("PDF is encrypted/password protected")

            validation_result["steps_completed"].append("pdf_structure")
            validation_result["pdf_info"] = {
                "pages": len(pdf_reader.pages),
                "encrypted": pdf_reader.is_encrypted,
                "has_text": bool(text.strip())
            }
            return True

        except Exception as e:
            validation_result["steps_failed"].append("pdf_structure")
            validation_result["errors"].append({
                "step": "pdf_structure",
                "error": f"PDF validation failed: {e}",
                "error_type": "pdf_invalid_or_corrupted"
            })
            return False

    def _validate_image_dimensions(self, file_path: str, validation_result: Dict[str, Any]) -> bool:
        """Step 3b: Validate image dimensions."""
        if not DEPENDENCIES_AVAILABLE:
            validation_result["steps_completed"].append("image_dimensions")
            validation_result["warnings"].append("Image validation skipped - dependencies not available")
            return True

        try:
            with Image.open(file_path) as img:
                width, height = img.size
                max_width = self.config["image_max_width"]
                max_height = self.config["image_max_height"]

                if width > max_width or height > max_height:
                    validation_result["steps_failed"].append("image_dimensions")
                    validation_result["errors"].append({
                        "step": "image_dimensions",
                        "error": f"Image dimensions {width}x{height} exceed maximum {max_width}x{max_height}",
                        "error_type": "image_dimensions_exceeded",
                        "provided_width": width,
                        "provided_height": height,
                        "max_width": max_width,
                        "max_height": max_height
                    })
                    return False

            validation_result["steps_completed"].append("image_dimensions")
            validation_result["image_info"] = {
                "width": width,
                "height": height,
                "format": img.format,
                "mode": img.mode
            }
            return True

        except Exception as e:
            validation_result["steps_failed"].append("image_dimensions")
            validation_result["errors"].append({
                "step": "image_dimensions",
                "error": f"Image validation failed: {e}",
                "error_type": "image_invalid_or_corrupted"
            })
            return False

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase."""
        return Path(filename).suffix.lower().lstrip('.')

    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Get human-readable validation summary."""
        if validation_result["final_status"] == "passed":
            return f"✅ Validation passed for {validation_result['original_filename']}"

        failed_steps = ", ".join(validation_result["steps_failed"])
        error_messages = [error["error"] for error in validation_result["errors"]]
        return f"❌ Validation failed for {validation_result['original_filename']}. Failed steps: {failed_steps}. Errors: {'; '.join(error_messages)}"
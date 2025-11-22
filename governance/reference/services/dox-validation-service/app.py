"""
Flask application for DOX Validation Service.

Provides REST API for file validation, virus scanning, and rate limiting.
"""

import os
import tempfile
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import werkzeug.utils

from .config import Config
from .validators import FileValidator


def create_app(config_name: str = "default"):
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Setup logging
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Validate configuration
    try:
        Config.validate()
        logger.info("✅ Configuration validation passed")
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        raise

    # Initialize Redis connection
    redis_client = None
    try:
        redis_client = redis.Redis(
            host=app.config["REDIS_HOST"],
            port=app.config["REDIS_PORT"],
            db=app.config["REDIS_DB"],
            password=app.config["REDIS_PASSWORD"],
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test connection
        redis_client.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        redis_client = None

    # Initialize file validator
    file_validator = FileValidator(redis_client)

    # Authentication decorator
    def require_auth(f):
        """Decorator to require authentication."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not app.config["REQUIRE_AUTH"]:
                return f(*args, **kwargs)

            # Check API key
            api_key = request.headers.get('X-API-Key')
            if api_key and api_key == app.config["API_KEY"]:
                return f(*args, **kwargs)

            # Check Bearer token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                # TODO: Validate JWT with dox-core-auth
                return f(*args, **kwargs)

            return jsonify({
                "error": "Authentication required",
                "message": "Missing or invalid authentication",
                "timestamp": datetime.utcnow().isoformat()
            }), 401

        return decorated_function

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad request",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({
            "error": "Payload too large",
            "message": "File size exceeds maximum allowed",
            "max_size_mb": app.config["MAX_FILE_SIZE_MB"],
            "timestamp": datetime.utcnow().isoformat()
        }), 413

    @app.errorhandler(415)
    def unsupported_media_type(error):
        return jsonify({
            "error": "Unsupported media type",
            "message": "File type not allowed",
            "allowed_types": app.config["ALLOWED_EXTENSIONS"],
            "timestamp": datetime.utcnow().isoformat()
        }), 415

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Too many requests, please try again later",
            "timestamp": datetime.utcnow().isoformat()
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

    # Routes
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            validator_health = file_validator.health_check()
            redis_status = "connected" if redis_client else "disconnected"

            return jsonify({
                "status": "healthy" if validator_health["status"] == "healthy" else "degraded",
                "service": app.config["SERVICE_NAME"],
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "file_validator": validator_health,
                    "redis": {"status": redis_status},
                    "clamav": validator_health["components"]["virus_scanner"],
                    "rate_limiter": validator_health["components"]["rate_limiter"]
                }
            }), 200

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "service": app.config["SERVICE_NAME"],
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 503

    @app.route('/api/v1/validate/scan', methods=['POST'])
    @require_auth
    def scan_file():
        """
        Scan file for viruses.

        Request body:
        {
            "file_path": "/path/to/file",
            "file_hash": "sha256:...",
            "file_size": 12345
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "error": "Request body is required",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            file_path = data.get("file_path")
            file_hash = data.get("file_hash")
            file_size = data.get("file_size")

            if not all([file_path, file_hash, file_size]):
                return jsonify({
                    "error": "file_path, file_hash, and file_size are required",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            # Check if file exists
            if not os.path.exists(file_path):
                return jsonify({
                    "error": "File not found",
                    "file_path": file_path,
                    "timestamp": datetime.utcnow().isoformat()
                }), 404

            # Perform virus scan
            is_clean, scan_result = file_validator.virus_scanner.scan_file(file_path, file_hash, file_size)

            response = {
                "success": is_clean,
                "scan_result": scan_result,
                "timestamp": datetime.utcnow().isoformat()
            }

            status_code = 200 if is_clean else 419
            return jsonify(response), status_code

        except Exception as e:
            logger.error(f"File scan failed: {e}")
            return jsonify({
                "error": "File scan failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/validate/rate-check', methods=['POST'])
    @require_auth
    def check_rate_limit():
        """
        Check rate limit for user/account.

        Request body:
        {
            "user_id": "user123",
            "account_id": "account456",
            "time_window": "24h"
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    "error": "Request body is required",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            user_id = data.get("user_id")
            account_id = data.get("account_id")
            time_window = data.get("time_window", "24h")

            if not all([user_id, account_id]):
                return jsonify({
                    "error": "user_id and account_id are required",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            # Parse time window
            try:
                window_hours = int(time_window.rstrip('h'))
            except ValueError:
                window_hours = 24

            # Check rate limit
            within_limit, rate_info = file_validator.rate_limiter.check_rate_limit(
                user_id, account_id, window_hours
            )

            response = {
                "within_limit": within_limit,
                "rate_limit_info": rate_info,
                "timestamp": datetime.utcnow().isoformat()
            }

            status_code = 200 if within_limit else 429
            return jsonify(response), status_code

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return jsonify({
                "error": "Rate limit check failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/validate/file', methods=['POST'])
    @require_auth
    def validate_file():
        """
        Complete file validation (multipart file upload).

        Form data:
        - file: The file to validate
        - user_id: User ID (optional)
        - account_id: Account ID (optional)
        - skip_rate_limit: Skip rate limiting (optional)
        """
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({
                    "error": "No file provided",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    "error": "No file selected",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400

            # Get form data
            user_id = request.form.get('user_id')
            account_id = request.form.get('account_id')
            skip_rate_limit = request.form.get('skip_rate_limit', 'false').lower() == 'true'

            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name

            try:
                # Perform complete validation
                validation_result = file_validator.validate_file(
                    tmp_path, file.filename, user_id, account_id, skip_rate_limit
                )

                # Clean up temporary file
                os.unlink(tmp_path)

                # Return validation result
                status_code = 200 if validation_result["final_status"] == "valid" else 400
                return jsonify({
                    "success": validation_result["final_status"] == "valid",
                    "validation_result": validation_result,
                    "timestamp": datetime.utcnow().isoformat()
                }), status_code

            except Exception as e:
                # Clean up temporary file on error
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise

        except Exception as e:
            logger.error(f"File validation failed: {e}")
            return jsonify({
                "error": "File validation failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/validate/config', methods=['GET'])
    def get_validation_config():
        """Get validation configuration."""
        try:
            config = {
                "validation": Config.get_validation_config(),
                "clamav": Config.get_clamav_config(),
                "rate_limiting": Config.get_rate_limit_config(),
                "service": {
                    "name": app.config["SERVICE_NAME"],
                    "version": "1.0.0",
                    "max_file_size_mb": app.config["MAX_FILE_SIZE_MB"]
                }
            }

            return jsonify({
                "success": True,
                "config": config,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Failed to get validation config: {e}")
            return jsonify({
                "error": "Failed to get configuration",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/v1/metrics', methods=['GET'])
    def get_metrics():
        """Get service metrics."""
        try:
            # Basic metrics
            metrics = {
                "service": app.config["SERVICE_NAME"],
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": 0,  # Would track actual uptime
                "components": {
                    "clamav": file_validator.virus_scanner.health_check(),
                    "rate_limiter": file_validator.rate_limiter.health_check() if file_validator.rate_limiter else {"status": "disabled"}
                }
            }

            # Redis metrics
            if redis_client:
                try:
                    redis_info = redis_client.info()
                    metrics["redis"] = {
                        "connected_clients": redis_info.get("connected_clients", 0),
                        "used_memory_human": redis_info.get("used_memory_human", "unknown"),
                        "total_commands_processed": redis_info.get("total_commands_processed", 0)
                    }
                except Exception as e:
                    metrics["redis"] = {"error": str(e)}

            return jsonify({
                "success": True,
                "metrics": metrics
            })

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return jsonify({
                "error": "Failed to get metrics",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 500

    @app.route('/', methods=['GET'])
    def index():
        """Service information."""
        return jsonify({
            "service": app.config["SERVICE_NAME"],
            "version": "1.0.0",
            "description": "DOX Validation Service - File validation, virus scanning, and rate limiting",
            "endpoints": {
                "health": "/health",
                "validate_file": "/api/v1/validate/file",
                "scan_file": "/api/v1/validate/scan",
                "check_rate_limit": "/api/v1/validate/rate-check",
                "config": "/api/v1/validate/config",
                "metrics": "/api/v1/metrics"
            },
            "documentation": "/docs",
            "timestamp": datetime.utcnow().isoformat()
        })

    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config.get("SERVICE_PORT", 5007)
    debug = app.config.get("DEBUG", False)

    print(f"Starting DOX Validation Service on port {port}")
    print(f"Debug mode: {debug}")

    app.run(host="0.0.0.0", port=port, debug=debug)
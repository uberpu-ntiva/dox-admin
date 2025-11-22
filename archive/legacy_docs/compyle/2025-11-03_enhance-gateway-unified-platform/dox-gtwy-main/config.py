"""
Configuration for DOX API Gateway.
"""

import os
from typing import List, Dict, Any


class GatewayConfig:
    """Configuration class for API Gateway."""

    # Service Configuration
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "dox-api-gateway")
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8080))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Redis Configuration
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

    # Downstream Service URLs - Core Services
    CORE_AUTH_URL = os.environ.get("CORE_AUTH_URL", "http://dox-core-auth:5001")
    CORE_STORE_URL = os.environ.get("CORE_STORE_URL", "http://dox-core-store:5000")

    # Downstream Service URLs - Workflow & Automation
    WORKFLOW_ORCHESTRATOR_URL = os.environ.get("WORKFLOW_ORCHESTRATOR_URL", "http://dox-workflow-orchestrator:5002")
    VALIDATION_SERVICE_URL = os.environ.get("VALIDATION_SERVICE_URL", "http://dox-validation-service:5003")
    ACTIVATION_SERVICE_URL = os.environ.get("ACTIVATION_SERVICE_URL", "http://dox-actv-service:5010")
    ACTIVATION_LISTENER_URL = os.environ.get("ACTIVATION_LISTENER_URL", "http://dox-actv-listener:5011")
    LIFECYCLE_SERVICE_URL = os.environ.get("LIFECYCLE_SERVICE_URL", "http://dox-auto-lifecycle-service:5012")
    WORKFLOW_ENGINE_URL = os.environ.get("WORKFLOW_ENGINE_URL", "http://dox-auto-workflow-engine:5013")

    # Downstream Service URLs - Template & Document Services
    TEMPLATE_SERVICE_URL = os.environ.get("TEMPLATE_SERVICE_URL", "http://dox-tmpl-service:5004")
    FIELD_MAPPER_URL = os.environ.get("FIELD_MAPPER_URL", "http://dox-tmpl-field-mapper:5014")
    PDF_UPLOAD_URL = os.environ.get("PDF_UPLOAD_URL", "http://dox-tmpl-pdf-upload:5015")
    BARCODE_MATCHER_URL = os.environ.get("BARCODE_MATCHER_URL", "http://dox-rtns-barcode-matcher:5016")

    # Downstream Service URLs - Document Processing
    BATCH_ASSEMBLY_URL = os.environ.get("BATCH_ASSEMBLY_URL", "http://dox-batch-assembly:5017")
    PACT_UPLOAD_URL = os.environ.get("PACT_UPLOAD_URL", "http://dox-pact-manual-upload:5018")
    RTNS_UPLOAD_URL = os.environ.get("RTNS_UPLOAD_URL", "http://dox-rtns-manual-upload:5019")

    # Downstream Service URLs - E-Signature
    ESIG_SERVICE_URL = os.environ.get("ESIG_SERVICE_URL", "http://dox-esig-service:5005")
    ESIG_WEBHOOK_LISTENER_URL = os.environ.get("ESIG_WEBHOOK_LISTENER_URL", "http://dox-esig-webhook-listener:5020")

    # Downstream Service URLs - Data Platform
    DATA_ETL_URL = os.environ.get("DATA_ETL_URL", "http://dox-data-etl-service:5021")
    DATA_DISTRIB_URL = os.environ.get("DATA_DISTRIB_URL", "http://dox-data-distrib-service:5022")
    DATA_AGGREGATION_URL = os.environ.get("DATA_AGGREGATION_URL", "http://dox-data-aggregation-service:5023")

    # Rate Limiting Configuration
    ENABLE_RATE_LIMITING = os.environ.get("ENABLE_RATE_LIMITING", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))
    RATE_LIMIT_BURST = int(os.environ.get("RATE_LIMIT_BURST", 200))

    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_THRESHOLD = int(os.environ.get("CIRCUIT_BREAKER_THRESHOLD", 5))
    CIRCUIT_BREAKER_TIMEOUT = int(os.environ.get("CIRCUIT_BREAKER_TIMEOUT", 60))
    CIRCUIT_BREAKER_RESET_TIMEOUT = int(os.environ.get("CIRCUIT_BREAKER_RESET_TIMEOUT", 300))

    # CORS Configuration
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    ALLOWED_HEADERS = os.environ.get("ALLOWED_HEADERS", "Content-Type,Authorization,X-Requested-With,X-Correlation-ID").split(",")

    # Security Configuration
    ENABLE_REQUEST_VALIDATION = os.environ.get("ENABLE_REQUEST_VALIDATION", "true").lower() == "true"
    MAX_REQUEST_SIZE_MB = int(os.environ.get("MAX_REQUEST_SIZE_MB", 100))
    ENABLE_REQUEST_LOGGING = os.environ.get("ENABLE_REQUEST_LOGGING", "true").lower() == "true"

    # Metrics Configuration
    ENABLE_METRICS = os.environ.get("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT = int(os.environ.get("METRICS_PORT", 9090))
    METRICS_PATH = os.environ.get("METRICS_PATH", "/metrics")

    # Timeout Configuration
    DEFAULT_TIMEOUT = int(os.environ.get("DEFAULT_TIMEOUT", 30))
    UPLOAD_TIMEOUT = int(os.environ.get("UPLOAD_TIMEOUT", 300))

    # Cache Configuration
    ENABLE_RESPONSE_CACHING = os.environ.get("ENABLE_RESPONSE_CACHING", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", 300))
    CACHE_MAX_SIZE_MB = int(os.environ.get("CACHE_MAX_SIZE_MB", 100))

    # API Versioning
    SUPPORTED_VERSIONS = os.environ.get("SUPPORTED_VERSIONS", "v1,v2").split(",")
    DEFAULT_API_VERSION = os.environ.get("DEFAULT_API_VERSION", "v1")

    # Webhook Configuration
    WEBHOOK_ENABLED = os.environ.get("WEBHOOK_ENABLED", "false").lower() == "true"
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

    # Service Discovery
    SERVICE_DISCOVERY_ENABLED = os.environ.get("SERVICE_DISCOVERY_ENABLED", "false").lower() == "true"
    CONSUL_HOST = os.environ.get("CONSUL_HOST", "localhost")
    CONSUL_PORT = int(os.environ.get("CONSUL_PORT", 8500))

    # Load Balancing
    LOAD_BALANCING_STRATEGY = os.environ.get("LOAD_BALANCING_STRATEGY", "round_robin")  # round_robin, least_connections, ip_hash

    # Request/Response Limits
    MAX_HEADER_SIZE = int(os.environ.get("MAX_HEADER_SIZE", 8192))
    MAX_URI_LENGTH = int(os.environ.get("MAX_URI_LENGTH", 4096))

    # Health Check Configuration
    HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", 30))
    HEALTH_CHECK_TIMEOUT = int(os.environ.get("HEALTH_CHECK_TIMEOUT", 5))

    @classmethod
    def get_service_config(cls, service_name: str) -> Dict[str, Any]:
        """Get configuration for specific service."""
        service_configs = {
            # Core Services
            'core-auth': {
                'url': cls.CORE_AUTH_URL,
                'timeout': 30,
                'auth_required': False,
                'rate_limit': (100, 60),
                'retry_attempts': 3,
                'retry_delay': 1
            },
            'core-store': {
                'url': cls.CORE_STORE_URL,
                'timeout': 60,
                'auth_required': True,
                'rate_limit': (200, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            # Workflow & Automation
            'workflow-orchestrator': {
                'url': cls.WORKFLOW_ORCHESTRATOR_URL,
                'timeout': 45,
                'auth_required': True,
                'rate_limit': (150, 60),
                'retry_attempts': 3,
                'retry_delay': 1
            },
            'validation-service': {
                'url': cls.VALIDATION_SERVICE_URL,
                'timeout': 120,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 1,
                'retry_delay': 5
            },
            'activation-service': {
                'url': cls.ACTIVATION_SERVICE_URL,
                'timeout': 60,
                'auth_required': True,
                'rate_limit': (100, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            'activation-listener': {
                'url': cls.ACTIVATION_LISTENER_URL,
                'timeout': 30,
                'auth_required': True,
                'rate_limit': (200, 60),
                'retry_attempts': 2,
                'retry_delay': 1
            },
            'lifecycle-service': {
                'url': cls.LIFECYCLE_SERVICE_URL,
                'timeout': 45,
                'auth_required': True,
                'rate_limit': (100, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            'workflow-engine': {
                'url': cls.WORKFLOW_ENGINE_URL,
                'timeout': 60,
                'auth_required': True,
                'rate_limit': (80, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            # Template & Document Services
            'template-service': {
                'url': cls.TEMPLATE_SERVICE_URL,
                'timeout': 30,
                'auth_required': True,
                'rate_limit': (100, 60),
                'retry_attempts': 3,
                'retry_delay': 1
            },
            'field-mapper': {
                'url': cls.FIELD_MAPPER_URL,
                'timeout': 45,
                'auth_required': True,
                'rate_limit': (100, 60),
                'retry_attempts': 2,
                'retry_delay': 1
            },
            'pdf-upload': {
                'url': cls.PDF_UPLOAD_URL,
                'timeout': 300,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 1,
                'retry_delay': 5
            },
            'barcode-matcher': {
                'url': cls.BARCODE_MATCHER_URL,
                'timeout': 60,
                'auth_required': True,
                'rate_limit': (80, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            # Document Processing
            'batch-assembly': {
                'url': cls.BATCH_ASSEMBLY_URL,
                'timeout': 120,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            'pact-upload': {
                'url': cls.PACT_UPLOAD_URL,
                'timeout': 300,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 1,
                'retry_delay': 5
            },
            'rtns-upload': {
                'url': cls.RTNS_UPLOAD_URL,
                'timeout': 300,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 1,
                'retry_delay': 5
            },
            # E-Signature
            'esig-service': {
                'url': cls.ESIG_SERVICE_URL,
                'timeout': 60,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            'esig-webhook-listener': {
                'url': cls.ESIG_WEBHOOK_LISTENER_URL,
                'timeout': 30,
                'auth_required': True,
                'rate_limit': (200, 60),
                'retry_attempts': 2,
                'retry_delay': 1
            },
            # Data Platform
            'data-etl': {
                'url': cls.DATA_ETL_URL,
                'timeout': 180,
                'auth_required': True,
                'rate_limit': (30, 60),
                'retry_attempts': 1,
                'retry_delay': 5
            },
            'data-distrib': {
                'url': cls.DATA_DISTRIB_URL,
                'timeout': 120,
                'auth_required': True,
                'rate_limit': (100, 60),
                'retry_attempts': 2,
                'retry_delay': 2
            },
            'data-aggregation': {
                'url': cls.DATA_AGGREGATION_URL,
                'timeout': 60,
                'auth_required': True,
                'rate_limit': (50, 60),
                'retry_attempts': 2,
                'retry_delay': 1
            }
        }
        return service_configs.get(service_name, {})

    @classmethod
    def validate(cls):
        """Validate configuration values."""
        errors = []

        if cls.SERVICE_PORT <= 0 or cls.SERVICE_PORT > 65535:
            errors.append("SERVICE_PORT must be between 1 and 65535")

        if cls.REDIS_PORT <= 0 or cls.REDIS_PORT > 65535:
            errors.append("REDIS_PORT must be between 1 and 65535")

        if cls.RATE_LIMIT_REQUESTS <= 0:
            errors.append("RATE_LIMIT_REQUESTS must be positive")

        if cls.CIRCUIT_BREAKER_THRESHOLD <= 0:
            errors.append("CIRCUIT_BREAKER_THRESHOLD must be positive")

        if cls.MAX_REQUEST_SIZE_MB <= 0:
            errors.append("MAX_REQUEST_SIZE_MB must be positive")

        if cls.CACHE_TTL_SECONDS < 0:
            errors.append("CACHE_TTL_SECONDS must be non-negative")

        if cls.DEFAULT_TIMEOUT <= 0:
            errors.append("DEFAULT_TIMEOUT must be positive")

        # Validate service URLs (all services now part of gateway)
        all_service_attrs = [attr for attr in dir(cls) if attr.endswith('_URL') and not attr.startswith('_')]

        # Note: Some URLs can be optional in development (use defaults)
        # Only enforce validation for critical services
        critical_services = [
            'CORE_AUTH_URL', 'CORE_STORE_URL'
        ]

        for service_attr in critical_services:
            if hasattr(cls, service_attr):
                url = getattr(cls, service_attr)
                if not url or not url.startswith(('http://', 'https://')):
                    errors.append(f"{service_attr} must be a valid HTTP/HTTPS URL")

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

        return True

    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration as dictionary."""
        config = {
            'host': cls.REDIS_HOST,
            'port': cls.REDIS_PORT,
            'db': cls.REDIS_DB,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True
        }

        if cls.REDIS_PASSWORD:
            config['password'] = cls.REDIS_PASSWORD

        return config

    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration as dictionary."""
        return {
            'enabled': cls.ENABLE_RATE_LIMITING,
            'requests': cls.RATE_LIMIT_REQUESTS,
            'window': cls.RATE_LIMIT_WINDOW,
            'burst': cls.RATE_LIMIT_BURST
        }

    @classmethod
    def get_circuit_breaker_config(cls) -> Dict[str, Any]:
        """Get circuit breaker configuration as dictionary."""
        return {
            'threshold': cls.CIRCUIT_BREAKER_THRESHOLD,
            'timeout': cls.CIRCUIT_BREAKER_TIMEOUT,
            'reset_timeout': cls.CIRCUIT_BREAKER_RESET_TIMEOUT
        }

    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Get CORS configuration as dictionary."""
        return {
            'origins': cls.CORS_ORIGINS,
            'allowed_headers': cls.ALLOWED_HEADERS
        }

    @classmethod
    def get_metrics_config(cls) -> Dict[str, Any]:
        """Get metrics configuration as dictionary."""
        return {
            'enabled': cls.ENABLE_METRICS,
            'port': cls.METRICS_PORT,
            'path': cls.METRICS_PATH
        }
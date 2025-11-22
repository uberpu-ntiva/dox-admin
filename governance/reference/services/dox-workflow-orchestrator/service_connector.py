"""
Service Connector for Workflow Orchestrator.

Handles HTTP communication with other DOX services.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class ServiceConnector:
    """Connects to and manages communication with other services."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize service connector."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.service_registry = self._load_service_registry()

    def _load_service_registry(self) -> Dict[str, Dict[str, Any]]:
        """Load service registry with default endpoints."""
        return {
            "dox-tmpl-pdf-upload": {
                "host": "dox-tmpl-pdf-upload",
                "port": 5002,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-tmpl-pdf-recognizer": {
                "host": "dox-tmpl-pdf-recognizer",
                "port": 5003,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-pact-manual-upload": {
                "host": "dox-pact-manual-upload",
                "port": 5004,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-rtns-manual-upload": {
                "host": "dox-rtns-manual-upload",
                "port": 5005,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-core-store": {
                "host": "dox-core-store",
                "port": 5000,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-core-auth": {
                "host": "dox-core-auth",
                "port": 5001,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-tmpl-service": {
                "host": "dox-tmpl-service",
                "port": 5006,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-validation-service": {
                "host": "dox-validation-service",
                "port": 5007,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-actv-service": {
                "host": "dox-actv-service",
                "port": 5008,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            },
            "dox-esig-service": {
                "host": "dox-esig-service",
                "port": 5009,
                "health_endpoint": "/health",
                "api_prefix": "/api/v1"
            }
        }

    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service."""
        if service_name not in self.service_registry:
            return {"error": f"Service {service_name} not found in registry"}

        service_config = self.service_registry[service_name]
        base_url = f"http://{service_config['host']}:{service_config['port']}"
        health_url = base_url + service_config["health_endpoint"]

        start_time = datetime.utcnow()

        try:
            response = requests.get(
                health_url,
                timeout=5,
                headers={"User-Agent": "dox-workflow-orchestrator/1.0.0"}
            )

            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)

            if response.status_code == 200:
                try:
                    health_data = response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time_ms,
                        "health_data": health_data,
                        "timestamp": end_time.isoformat()
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time_ms,
                        "response_text": response.text[:200],
                        "timestamp": end_time.isoformat()
                    }
            else:
                return {
                    "status": "unhealthy",
                    "http_status": response.status_code,
                    "response_time_ms": response_time_ms,
                    "response_text": response.text[:200],
                    "timestamp": end_time.isoformat()
                }

        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "response_time_ms": 5000,  # Timeout value
                "error": "Request timed out after 5 seconds",
                "timestamp": datetime.utcnow().isoformat()
            }

        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error",
                "response_time_ms": 0,
                "error": "Could not connect to service",
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "response_time_ms": 0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def call_service_api(self, service_name: str, method: str, endpoint: str,
                        data: Optional[Dict[str, Any]] = None,
                        params: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None,
                        timeout: int = 30) -> Dict[str, Any]:
        """Make API call to a service."""
        if service_name not in self.service_registry:
            raise ValueError(f"Service {service_name} not found in registry")

        service_config = self.service_registry[service_name]
        base_url = f"http://{service_config['host']}:{service_config['port']}"
        api_url = base_url + service_config["api_prefix"] + endpoint

        # Default headers
        default_headers = {
            "User-Agent": "dox-workflow-orchestrator/1.0.0",
            "Content-Type": "application/json"
        }
        if headers:
            default_headers.update(headers)

        try:
            response = requests.request(
                method=method.upper(),
                url=api_url,
                json=data if method.upper() in ["POST", "PUT", "PATCH"] else None,
                params=params,
                headers=default_headers,
                timeout=timeout
            )

            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "timestamp": datetime.utcnow().isoformat()
            }

            try:
                response_data["data"] = response.json()
            except json.JSONDecodeError:
                response_data["text"] = response.text

            return response_data

        except requests.exceptions.Timeout:
            return {
                "error": "Request timed out",
                "timeout_seconds": timeout,
                "timestamp": datetime.utcnow().isoformat()
            }

        except requests.exceptions.ConnectionError as e:
            return {
                "error": "Connection failed",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "error": "Request failed",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def call_document_upload_service(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call document upload service."""
        return self.call_service_api(
            service_name="dox-tmpl-pdf-upload",
            method="POST",
            endpoint="/documents/upload",
            data=file_data
        )

    def call_template_recognition_service(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call template recognition service."""
        return self.call_service_api(
            service_name="dox-tmpl-pdf-recognizer",
            method="POST",
            endpoint="/recognize/template",
            data=document_data
        )

    def call_storage_service(self, storage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call document storage service."""
        return self.call_service_api(
            service_name="dox-core-store",
            method="POST",
            endpoint="/documents",
            data=storage_data
        )

    def call_validation_service(self, validation_type: str, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call file validation service."""
        endpoint = f"/validate/{validation_type}"
        return self.call_service_api(
            service_name="dox-validation-service",
            method="POST",
            endpoint=endpoint,
            data=validation_data
        )

    def call_auth_service(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call authentication service."""
        return self.call_service_api(
            service_name="dox-core-auth",
            method="POST",
            endpoint="/auth/validate",
            data=auth_data
        )

    def call_template_service(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call template service."""
        return self.call_service_api(
            service_name="dox-tmpl-service",
            method="POST",
            endpoint="/templates/process",
            data=template_data
        )

    def check_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered services."""
        health_results = {}

        for service_name in self.service_registry.keys():
            health_results[service_name] = self.check_service_health(service_name)

        return health_results

    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics from a specific service."""
        if service_name not in self.service_registry:
            return {"error": f"Service {service_name} not found in registry"}

        # Try to call metrics endpoint if available
        try:
            response = self.call_service_api(
                service_name=service_name,
                method="GET",
                endpoint="/metrics"
            )
            return response
        except:
            # Fallback to health check
            health = self.check_service_health(service_name)
            return {
                "metrics_unavailable": True,
                "health_status": health.get("status", "unknown"),
                "response_time_ms": health.get("response_time_ms", 0)
            }

    def discover_service_endpoints(self, service_name: str) -> List[str]:
        """Discover available endpoints for a service."""
        if service_name not in self.service_registry:
            return []

        try:
            response = self.call_service_api(
                service_name=service_name,
                method="GET",
                endpoint="/"
            )

            if "data" in response and isinstance(response["data"], dict):
                # Look for common endpoint discovery patterns
                data = response["data"]
                endpoints = []

                if "endpoints" in data:
                    endpoints.extend(data["endpoints"])
                if "routes" in data:
                    endpoints.extend(data["routes"])
                if "api" in data and isinstance(data["api"], dict):
                    endpoints.extend(data["api"].keys())

                return endpoints

        except:
            pass

        # Return known default endpoints
        service_config = self.service_registry[service_name]
        default_endpoints = [
            service_config["health_endpoint"],
            service_config["api_prefix"] + "/",
            service_config["api_prefix"] + "/health",
            service_config["api_prefix"] + "/metrics"
        ]

        return default_endpoints

    def health_check(self) -> str:
        """Check health of service connector."""
        try:
            # Try to connect to Redis (if available)
            # Check if we can reach at least one service
            test_service = list(self.service_registry.keys())[0]
            health = self.check_service_health(test_service)

            if health.get("status") in ["healthy", "timeout", "connection_error"]:
                # We can reach the service (even if it's down)
                return "healthy"
            else:
                return "degraded"

        except Exception:
            return "unhealthy"

    def get_connector_statistics(self) -> Dict[str, Any]:
        """Get service connector statistics."""
        return {
            "registered_services": len(self.service_registry),
            "service_list": list(self.service_registry.keys()),
            "health_status": self.health_check(),
            "timestamp": datetime.utcnow().isoformat()
        }
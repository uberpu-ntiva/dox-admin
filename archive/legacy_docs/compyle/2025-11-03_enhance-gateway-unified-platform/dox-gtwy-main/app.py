"""
DOX API Gateway - Main Gateway Service
Central entry point for all DOX platform APIs with routing, authentication, rate limiting, and monitoring.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import redis
import jwt
import requests
import logging
import time
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GatewayConfig
from auth_service import AuthService
from rate_limiter import RateLimiter
from request_logger import RequestLogger
from circuit_breaker import CircuitBreaker
from metrics_collector import MetricsCollector

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = GatewayConfig()

# Setup CORS
CORS(app, origins=config.CORS_ORIGINS, allow_headers=config.ALLOWED_HEADERS)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/api-gateway.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize services
try:
    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

auth_service = AuthService(redis_client)
rate_limiter = RateLimiter(redis_client, config)
request_logger = RequestLogger(redis_client, config)
metrics_collector = MetricsCollector(config)

# Circuit breakers for downstream services
circuit_breakers = {
    # Core Services
    'core-auth': CircuitBreaker('core-auth', config.CIRCUIT_BREAKER_THRESHOLD),
    'core-store': CircuitBreaker('core-store', config.CIRCUIT_BREAKER_THRESHOLD),
    # Workflow & Automation
    'workflow-orchestrator': CircuitBreaker('workflow-orchestrator', config.CIRCUIT_BREAKER_THRESHOLD),
    'validation-service': CircuitBreaker('validation-service', config.CIRCUIT_BREAKER_THRESHOLD),
    'activation-service': CircuitBreaker('activation-service', config.CIRCUIT_BREAKER_THRESHOLD),
    'activation-listener': CircuitBreaker('activation-listener', config.CIRCUIT_BREAKER_THRESHOLD),
    'lifecycle-service': CircuitBreaker('lifecycle-service', config.CIRCUIT_BREAKER_THRESHOLD),
    'workflow-engine': CircuitBreaker('workflow-engine', config.CIRCUIT_BREAKER_THRESHOLD),
    # Template & Document Services
    'template-service': CircuitBreaker('template-service', config.CIRCUIT_BREAKER_THRESHOLD),
    'field-mapper': CircuitBreaker('field-mapper', config.CIRCUIT_BREAKER_THRESHOLD),
    'pdf-upload': CircuitBreaker('pdf-upload', config.CIRCUIT_BREAKER_THRESHOLD),
    'barcode-matcher': CircuitBreaker('barcode-matcher', config.CIRCUIT_BREAKER_THRESHOLD),
    # Document Processing
    'batch-assembly': CircuitBreaker('batch-assembly', config.CIRCUIT_BREAKER_THRESHOLD),
    'pact-upload': CircuitBreaker('pact-upload', config.CIRCUIT_BREAKER_THRESHOLD),
    'rtns-upload': CircuitBreaker('rtns-upload', config.CIRCUIT_BREAKER_THRESHOLD),
    # E-Signature
    'esig-service': CircuitBreaker('esig-service', config.CIRCUIT_BREAKER_THRESHOLD),
    'esig-webhook-listener': CircuitBreaker('esig-webhook-listener', config.CIRCUIT_BREAKER_THRESHOLD),
    # Data Platform
    'data-etl': CircuitBreaker('data-etl', config.CIRCUIT_BREAKER_THRESHOLD),
    'data-distrib': CircuitBreaker('data-distrib', config.CIRCUIT_BREAKER_THRESHOLD),
    'data-aggregation': CircuitBreaker('data-aggregation', config.CIRCUIT_BREAKER_THRESHOLD)
}

# Service configuration - populated from config
SERVICE_NAMES = [
    # Core Services
    'core-auth', 'core-store',
    # Workflow & Automation
    'workflow-orchestrator', 'validation-service', 'activation-service',
    'activation-listener', 'lifecycle-service', 'workflow-engine',
    # Template & Document Services
    'template-service', 'field-mapper', 'pdf-upload', 'barcode-matcher',
    # Document Processing
    'batch-assembly', 'pact-upload', 'rtns-upload',
    # E-Signature
    'esig-service', 'esig-webhook-listener',
    # Data Platform
    'data-etl', 'data-distrib', 'data-aggregation'
]

SERVICES = {}
for service_name in SERVICE_NAMES:
    service_config = config.get_service_config(service_name)
    if service_config:
        SERVICES[service_name] = service_config


def get_client_info():
    """Extract client information from request."""
    return {
        'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', ''),
        'method': request.method,
        'path': request.path,
        'query_string': request.query_string.decode('utf-8'),
        'content_length': request.content_length
    }


def requires_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return jsonify({
                'success': False,
                'error': 'Authorization header required',
                'error_code': 'MISSING_TOKEN'
            }), 401

        # Validate token with auth service
        try:
            user_info = auth_service.validate_token(token)
            if not user_info:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token',
                    'error_code': 'INVALID_TOKEN'
                }), 401

            # Add user info to request context
            g.current_user = user_info
            g.auth_token = token

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'error_code': 'AUTH_ERROR'
            }), 401

        return f(*args, **kwargs)
    return decorated_function


def rate_limit(service_name):
    """Apply rate limiting for specific service."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_info = get_client_info()
            rate_limit_config = SERVICES.get(service_name, {}).get('rate_limit', (100, 60))

            if not rate_limiter.is_allowed(client_info['ip_address'], rate_limit_config):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': rate_limit_config[1]
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def proxy_request(service_name, path, method=None, data=None, headers=None, params=None):
    """Proxy request to downstream service."""
    service_config = SERVICES.get(service_name)
    if not service_config:
        return None, {'success': False, 'error': 'Service not found'}, 404

    # Use circuit breaker for fault tolerance
    circuit_breaker = circuit_breakers.get(service_name)
    if circuit_breaker and circuit_breaker.is_open():
        return None, {
            'success': False,
            'error': 'Service temporarily unavailable',
            'error_code': 'CIRCUIT_BREAKER_OPEN'
        }, 503

    try:
        service_url = service_config['url'].rstrip('/')
        full_url = f"{service_url}/{path.lstrip('/')}"

        # Prepare request
        proxy_method = method or request.method
        proxy_headers = headers or {}
        proxy_data = data or (request.get_json() if request.is_json else None)
        proxy_params = params or request.args

        # Add correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or \
                        f"gw_{int(time.time())}_{hash(full_url)}"
        proxy_headers['X-Correlation-ID'] = correlation_id

        # Add user context if authenticated
        if hasattr(g, 'current_user'):
            proxy_headers['X-User-ID'] = g.current_user.get('sub')
            proxy_headers['X-User-Email'] = g.current_user.get('email')
            proxy_headers['X-User-Roles'] = ','.join(g.current_user.get('roles', []))

        # Make request with timeout
        response = requests.request(
            method=proxy_method,
            url=full_url,
            headers=proxy_headers,
            json=proxy_data if proxy_data and proxy_method in ['POST', 'PUT', 'PATCH'] else None,
            data=request.get_data() if not proxy_data and proxy_method in ['POST', 'PUT', 'PATCH'] else None,
            params=proxy_params,
            timeout=service_config['timeout'],
            stream=True
        )

        # Record success for circuit breaker
        if circuit_breaker:
            circuit_breaker.record_success()

        # Read response content
        try:
            content = response.json()
        except ValueError:
            content = response.text

        # Log request/response
        request_logger.log_request(
            correlation_id,
            client_info=get_client_info(),
            service=service_name,
            method=proxy_method,
            path=full_url,
            status_code=response.status_code,
            response_time=response.elapsed.total_seconds()
        )

        # Collect metrics
        metrics_collector.record_request(
            service=service_name,
            method=proxy_method,
            status_code=response.status_code,
            response_time=response.elapsed.total_seconds()
        )

        return response, content, response.status_code

    except requests.exceptions.Timeout:
        # Record timeout for circuit breaker
        if circuit_breaker:
            circuit_breaker.record_failure()

        logger.error(f"Timeout for service {service_name}")
        return None, {
            'success': False,
            'error': 'Service request timeout',
            'error_code': 'SERVICE_TIMEOUT'
        }, 504

    except requests.exceptions.ConnectionError:
        # Record connection error for circuit breaker
        if circuit_breaker:
            circuit_breaker.record_failure()

        logger.error(f"Connection error for service {service_name}")
        return None, {
            'success': False,
            'error': 'Service unavailable',
            'error_code': 'SERVICE_UNAVAILABLE'
        }, 503

    except Exception as e:
        # Record general error for circuit breaker
        if circuit_breaker:
            circuit_breaker.record_failure()

        logger.error(f"Error proxying request to {service_name}: {e}")
        return None, {
            'success': False,
            'error': 'Internal gateway error',
            'error_code': 'GATEWAY_ERROR'
        }, 500


def handle_service_request(service_name, path):
    """Handle request to specific service."""
    service_config = SERVICES.get(service_name)
    if not service_config:
        return jsonify({
            'success': False,
            'error': 'Service not found',
            'error_code': 'SERVICE_NOT_FOUND'
        }), 404

    # Check if authentication is required
    if service_config.get('auth_required') and not hasattr(g, 'current_user'):
        return jsonify({
            'success': False,
            'error': 'Authentication required',
            'error_code': 'AUTH_REQUIRED'
        }), 401

    # Proxy the request
    response, content, status_code = proxy_request(service_name, path)

    if response is None:
        # Error occurred during proxy
        return jsonify(content), status_code

    # Return response with proper headers
    response_headers = {}
    for header, value in response.headers.items():
        if header.lower() in ['content-type', 'content-length', 'cache-control', 'etag']:
            response_headers[header] = value

    # Convert content to proper response
    if isinstance(content, dict):
        return jsonify(content), status_code, response_headers
    else:
        return content, status_code, response_headers


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Gateway health check."""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0',
        'services': {}
    }

    # Check downstream services
    for service_name, service_config in SERVICES.items():
        try:
            response = requests.get(
                f"{service_config['url']}/health",
                timeout=5
            )
            health_status['services'][service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            health_status['services'][service_name] = {
                'status': 'unhealthy',
                'error': str(e)
            }

    # Check Redis connection
    if redis_client:
        try:
            redis_client.ping()
            health_status['redis'] = {'status': 'healthy'}
        except Exception as e:
            health_status['redis'] = {'status': 'unhealthy', 'error': str(e)}
    else:
        health_status['redis'] = {'status': 'unhealthy', 'error': 'No connection'}

    # Determine overall health
    unhealthy_services = [s for s, status in health_status['services'].items()
                          if status['status'] != 'healthy']

    if unhealthy_services:
        health_status['status'] = 'degraded'
        if len(unhealthy_services) > len(SERVICES) / 2:
            health_status['status'] = 'unhealthy'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code


# Metrics endpoint
@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint."""
    return metrics_collector.get_metrics(), 200, {'Content-Type': 'text/plain'}


# API Routes
@app.route('/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('core-auth')
def auth_routes(path):
    """Route authentication requests."""
    return handle_service_request('core-auth', f'auth/{path}')


@app.route('/storage/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('core-store')
@requires_auth
def storage_routes(path):
    """Route storage requests."""
    return handle_service_request('core-store', f'storage/{path}')


@app.route('/workflows/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('workflow-orchestrator')
@requires_auth
def workflow_routes(path):
    """Route workflow requests."""
    return handle_service_request('workflow-orchestrator', f'workflows/{path}')


@app.route('/validation/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('validation-service')
@requires_auth
def validation_routes(path):
    """Route validation requests."""
    return handle_service_request('validation-service', f'validation/{path}')


@app.route('/templates/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('template-service')
@requires_auth
def template_routes(path):
    """Route template requests."""
    return handle_service_request('template-service', f'templates/{path}')


@app.route('/esig/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('esig-service')
@requires_auth
def esig_routes(path):
    """Route e-signature requests."""
    return handle_service_request('esig-service', f'esig/{path}')


# Activation Service Routes
@app.route('/activation/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('activation-service')
@requires_auth
def activation_routes(path):
    """Route activation service requests."""
    return handle_service_request('activation-service', f'activation/{path}')


@app.route('/activation-events/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('activation-listener')
@requires_auth
def activation_listener_routes(path):
    """Route activation listener requests."""
    return handle_service_request('activation-listener', f'events/{path}')


# Lifecycle Service Routes
@app.route('/lifecycle/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('lifecycle-service')
@requires_auth
def lifecycle_routes(path):
    """Route lifecycle management requests."""
    return handle_service_request('lifecycle-service', f'lifecycle/{path}')


# Workflow Engine Routes
@app.route('/workflows-engine/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('workflow-engine')
@requires_auth
def workflow_engine_routes(path):
    """Route workflow engine requests."""
    return handle_service_request('workflow-engine', f'api/workflows/{path}')


# Field Mapper Routes
@app.route('/field-mapping/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('field-mapper')
@requires_auth
def field_mapper_routes(path):
    """Route field mapping requests."""
    return handle_service_request('field-mapper', f'mapping/{path}')


# PDF Upload Routes
@app.route('/pdf-upload/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('pdf-upload')
@requires_auth
def pdf_upload_routes(path):
    """Route PDF upload requests."""
    return handle_service_request('pdf-upload', f'api/documents/{path}')


# Barcode Matcher Routes
@app.route('/barcode/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('barcode-matcher')
@requires_auth
def barcode_matcher_routes(path):
    """Route barcode matching requests."""
    return handle_service_request('barcode-matcher', f'barcode/{path}')


# Batch Assembly Routes
@app.route('/batch/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('batch-assembly')
@requires_auth
def batch_assembly_routes(path):
    """Route batch assembly requests."""
    return handle_service_request('batch-assembly', f'batch/{path}')


# PACT Upload Routes
@app.route('/pact-upload/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('pact-upload')
@requires_auth
def pact_upload_routes(path):
    """Route PACT upload requests."""
    return handle_service_request('pact-upload', f'api/documents/{path}')


# RTNS Upload Routes
@app.route('/rtns-upload/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('rtns-upload')
@requires_auth
def rtns_upload_routes(path):
    """Route RTNS upload requests."""
    return handle_service_request('rtns-upload', f'api/documents/{path}')


# E-Signature Webhook Listener Routes
@app.route('/esig-webhooks/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('esig-webhook-listener')
@requires_auth
def esig_webhook_routes(path):
    """Route e-signature webhook requests."""
    return handle_service_request('esig-webhook-listener', f'webhooks/{path}')


# Data ETL Routes
@app.route('/data-etl/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('data-etl')
@requires_auth
def data_etl_routes(path):
    """Route data ETL requests."""
    return handle_service_request('data-etl', f'api/etl/{path}')


# Data Distribution Routes
@app.route('/data-distrib/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('data-distrib')
@requires_auth
def data_distrib_routes(path):
    """Route data distribution requests."""
    return handle_service_request('data-distrib', f'distribute/{path}')


# Data Aggregation Routes
@app.route('/data-aggregation/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@rate_limit('data-aggregation')
@requires_auth
def data_aggregation_routes(path):
    """Route data aggregation requests."""
    return handle_service_request('data-aggregation', f'api/aggregation/{path}')


# API Gateway specific endpoints
@app.route('/api/v1/gateway/status', methods=['GET'])
def gateway_status():
    """Get detailed gateway status."""
    status = {
        'gateway': {
            'status': 'healthy',
            'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0,
            'version': '1.0.0'
        },
        'rate_limiting': {
            'enabled': config.ENABLE_RATE_LIMITING,
            'active_limits': rate_limiter.get_active_limits() if redis_client else {}
        },
        'circuit_breakers': {
            name: {
                'state': cb.state,
                'failure_count': cb.failure_count,
                'last_failure_time': cb.last_failure_time.isoformat() if cb.last_failure_time else None
            }
            for name, cb in circuit_breakers.items()
        }
    }

    return jsonify(status)


@app.route('/api/v1/gateway/routes', methods=['GET'])
def list_routes():
    """List all available routes."""
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'path': str(rule),
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'endpoint': rule.endpoint
            })

    return jsonify({
        'routes': routes,
        'total': len(routes)
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'error_code': 'NOT_FOUND'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'error_code': 'METHOD_NOT_ALLOWED'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'error_code': 'INTERNAL_ERROR'
    }), 500


# Middleware for request timing
@app.before_request
def before_request():
    g.start_time = time.time()


@app.after_request
def after_request(response):
    # Add timing headers
    if hasattr(g, 'start_time'):
        response.headers['X-Response-Time'] = f"{(time.time() - g.start_time):.3f}s"

    # Add gateway version
    response.headers['X-Gateway-Version'] = '1.0.0'

    # Add correlation ID
    correlation_id = request.headers.get('X-Correlation-ID')
    if correlation_id:
        response.headers['X-Correlation-ID'] = correlation_id

    return response


if __name__ == '__main__':
    app.start_time = time.time()

    logger.info(f"Starting DOX API Gateway on port {config.SERVICE_PORT}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Rate limiting: {config.ENABLE_RATE_LIMITING}")

    app.run(
        host='0.0.0.0',
        port=config.SERVICE_PORT,
        debug=config.DEBUG
    )
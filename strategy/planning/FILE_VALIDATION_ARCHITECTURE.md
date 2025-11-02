# File Validation Infrastructure Architecture

## Overview

This document outlines the file validation infrastructure design for the Pact Platform, providing centralized validation capabilities that can be integrated across all file upload services.

## Architecture Decision: Embedded Validation

After evaluating the requirements and constraints, we've chosen to implement file validation as **shared modules** embedded within existing services rather than creating a separate `dox-validation-service`. This approach:

- Reduces service complexity and inter-service dependencies
- Eliminates network latency for file validation
- Provides better resilience (no single point of failure)
- Allows validation rules to be customized per service context
- Maintains the existing 20-service architecture

## Core Validation Components

### 1. Validation Library (`validation_engine.py`)

**Location**: Shared module available to all services
**Purpose**: Centralized validation logic and rule engine

```python
class ValidationEngine:
    """Centralized file validation engine for all Pact Platform services"""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.virus_scanner = ClamAVScanner(config.clamd_socket)
        self.rate_limiter = RedisRateLimiter(config.redis_url)

    async def validate_file(self, file_data, user_id: str, context: str) -> ValidationResult:
        """Comprehensive file validation pipeline"""
        pass

    async def validate_size(self, file_data) -> ValidationResult:
        """File size validation"""
        pass

    async def validate_mime_type(self, file_data) -> ValidationResult:
        """MIME type validation using file magic bytes"""
        pass

    async def scan_for_malware(self, file_data) -> ValidationResult:
        """Virus scanning using ClamAV"""
        pass

    async def check_rate_limit(self, user_id: str, operation: str) -> ValidationResult:
        """Rate limiting per user"""
        pass
```

### 2. Configuration Management

**Location**: Environment-based configuration per service
**Purpose**: Service-specific validation rules

```python
@dataclass
class ValidationConfig:
    # File size limits (in MB)
    max_file_size: int = 50
    max_pdf_size: int = 50
    max_image_size: int = 10

    # Allowed MIME types
    allowed_mime_types: List[str] = field(default_factory=lambda: [
        'application/pdf',
        'image/jpeg',
        'image/png'
    ])

    # Rate limiting
    upload_rate_limit: int = 10  # per hour per user
    download_rate_limit: int = 100  # per hour per user

    # Security
    enable_virus_scan: bool = True
    clamd_socket: str = "/var/run/clamav/clamd.sock"

    # Redis for rate limiting
    redis_url: str = "redis://localhost:6379/0"

    # Context-specific rules
    context_specific_rules: Dict[str, Dict] = field(default_factory=dict)
```

### 3. Middleware Integration

**Location**: Flask middleware for all services
**Purpose**: Automatic validation on file upload endpoints

```python
class FileValidationMiddleware:
    """Flask middleware for automatic file validation"""

    def __init__(self, app: Flask, validation_engine: ValidationEngine):
        self.app = app
        self.validation_engine = validation_engine

    def validate_upload(self, endpoint_rules: Dict = None):
        """Decorator for upload endpoints"""
        def decorator(f):
            @wraps(f)
            async def decorated_function(*args, **kwargs):
                # Extract file from request
                # Run validation pipeline
                # Return early if validation fails
                pass
            return decorated_function
        return decorator
```

## Implementation Plan

### Phase 1: Core Library (Week 2)
- [ ] Create `validation_engine.py` shared module
- [ ] Implement size and MIME type validation
- [ ] Add configuration management
- [ ] Create error handling and response formats

### Phase 2: Security Integration (Week 3)
- [ ] Integrate ClamAV for virus scanning
- [ ] Implement Redis-based rate limiting
- [ ] Add audit logging
- [ ] Create security monitoring

### Phase 3: Service Integration (Weeks 4-5)
- [ ] Integrate validation in `dox-tmpl-pdf-recognizer`
- [ ] Integrate validation in `dox-tmpl-pdf-upload`
- [ ] Create middleware for all future services
- [ ] Add validation to service templates

### Phase 4: Monitoring & Maintenance (Week 6)
- [ ] Add validation metrics and monitoring
- [ ] Create validation health checks
- [ ] Document maintenance procedures
- [ ] Create runbooks for validation failures

## API Integration Pattern

### Existing Service Integration

Services with existing file upload endpoints will add validation as middleware:

```python
# Example: dox-tmpl-pdf-recognizer/app.py
from validation_engine import ValidationEngine, ValidationConfig

app = Flask(__name__)
validation_config = ValidationConfig.from_env()
validation_engine = ValidationEngine(validation_config)

@app.route('/api/templates', methods=['POST'])
@validation_engine.validate_upload({
    'max_size': 50,  # MB
    'allowed_types': ['application/pdf'],
    'require_virus_scan': True
})
async def upload_template():
    # Existing logic - validation already performed
    pass
```

### New Service Integration

New services will include validation from the start:

```python
# Template for new services
from validation_engine import ValidationEngine, ValidationMiddleware

def create_app():
    app = Flask(__name__)

    # Initialize validation
    validation_config = ValidationConfig.from_env()
    validation_engine = ValidationEngine(validation_config)
    ValidationMiddleware(app, validation_engine)

    # Routes with automatic validation
    @app.route('/api/upload', methods=['POST'])
    @validation_engine.validate_upload()
    async def upload_file():
        # File already validated
        pass
```

## Error Handling

### Validation Error Format

All validation errors follow the platform standard:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "File validation failed",
    "details": {
      "failed_checks": [
        {
          "check": "file_size",
          "message": "File size exceeds maximum limit of 50MB",
          "actual": 75.5,
          "limit": 50
        }
      ],
      "file_info": {
        "name": "document.pdf",
        "size": 75847293,
        "mime_type": "application/pdf"
      }
    },
    "timestamp": "2025-11-02T15:30:00Z"
  }
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `FILE_TOO_LARGE` | File exceeds size limit | 413 |
| `INVALID_MIME_TYPE` | File type not allowed | 415 |
| `MALWARE_DETECTED` | Virus scan failed | 422 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `CORRUPTED_FILE` | File structure invalid | 422 |
| `VALIDATION_FAILED` | Multiple validation failures | 400 |

## Security Considerations

### Multi-Layer Validation

1. **Size Validation**: Prevents resource exhaustion
2. **MIME Type Validation**: Uses file magic bytes, not headers
3. **Virus Scanning**: ClamAV integration with quarantine
4. **Rate Limiting**: Redis-based per-user limits
5. **Audit Logging**: All validation attempts logged
6. **Circuit Breaker**: Fail-safe for validation service issues

### Performance Optimization

- **Streaming**: Validate files during upload, not after
- **Async Processing**: Virus scanning in background where possible
- **Caching**: Cache MIME type detection results
- **Batch Processing**: Bulk validation for batch uploads

## Monitoring & Alerting

### Metrics to Track

- Validation success/failure rates per service
- Common validation failure reasons
- Rate limiting hit rates
- Virus scan results
- Validation latency and throughput
- Storage usage for quarantined files

### Alerting Conditions

- Virus detection (immediate alert)
- Validation failure rate > 5% (service degradation)
- Rate limiting hit rate > 80% (potential abuse)
- Validation latency > 5 seconds (performance issue)

## Dependencies & Requirements

### External Dependencies

- **ClamAV**: Virus scanning (must be installed on all servers)
- **Redis**: Rate limiting state management
- **python-magic**: MIME type detection from file content

### Python Libraries

```
python-magic>=0.4.27  # MIME type detection
clamd>=1.0.2          # ClamAV client
redis>=5.0.1          # Rate limiting
pydantic>=2.0.0       # Configuration validation
structlog>=23.0.0     # Structured logging
```

### Infrastructure Requirements

- **ClamAV Daemon**: Running on all application servers
- **Redis Cluster**: For distributed rate limiting
- **File Storage**: Quarantine area for suspicious files
- **Monitoring**: Prometheus metrics for validation performance

## Deployment Strategy

### Phase 1: Foundation (Immediate)
- Implement core validation library
- Add to existing services (pdf-recognizer, pdf-upload)
- Basic size and MIME validation
- Configuration via environment variables

### Phase 2: Security (Week 2-3)
- Deploy ClamAV infrastructure
- Implement Redis rate limiting
- Add virus scanning to all services
- Enable audit logging

### Phase 3: Integration (Week 4-5)
- Add validation to service templates
- Integrate with all new services
- Implement monitoring and alerting
- Create validation health checks

### Phase 4: Optimization (Week 6+)
- Performance tuning and optimization
- Advanced validation rules per service
- Machine learning for anomaly detection
- Automated quarantine management

## Testing Strategy

### Unit Tests
- All validation components
- Error handling scenarios
- Configuration validation
- Mock external dependencies

### Integration Tests
- End-to-end validation flows
- ClamAV integration
- Redis rate limiting
- Service middleware integration

### Security Tests
- Malware detection
- File type spoofing attempts
- Rate limit bypass attempts
- Large file handling

### Performance Tests
- Validation latency under load
- Concurrent validation requests
- Memory usage with large files
- Rate limiting effectiveness

## Documentation & Training

### Developer Documentation
- Validation library API reference
- Integration patterns and examples
- Configuration guide
- Troubleshooting common issues

### Operations Documentation
- ClamAV setup and maintenance
- Redis cluster management
- Monitoring dashboards
- Incident response procedures

### Team Training
- Security awareness training
- Validation best practices
- Incident response drills
- Performance tuning workshops

---

## Success Criteria

### Technical Success
- [ ] All file uploads validated consistently
- [ ] Zero malware infections in production
- [ ] Rate limiting prevents abuse effectively
- [ ] Validation adds <500ms latency
- [ ] 99.9% validation uptime

### Business Success
- [ ] Improved security posture
- [ ] Reduced support incidents from bad files
- [ ] Better compliance with security standards
- [ ] Easier onboarding of new services
- [ ] Consistent user experience across services

---

**Document Status**: ✅ COMPLETE
**Implementation Ready**: Phase 1 (Core Library)
**Next Steps**: Begin implementation in existing services
**Owner**: Infrastructure Team
**Review Date**: 2025-11-02

**Generated with Compyle**
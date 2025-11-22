# dox-tmpl-pdf-upload with FastAPI and MCP Integration Implementation Plan

## Overview

Convert the planned Flask-based dox-tmpl-pdf-upload service to FastAPI and implement a complementary MCP (Model Context Protocol) server for AI-powered PDF template management. This implementation will provide both REST API and MCP protocol access to PDF template upload, validation, storage, and management capabilities.

## Current State Analysis

**Existing State:**
- dox-tmpl-pdf-upload repository contains only documentation/blueprints (PLANNED status)
- OpenAPI 3.0 specification exists for Flask-based REST API
- Architecture designed for multi-layer PDF validation (size, MIME, virus, structure)
- Planned integration with dox-core-store (MSSQL), dox-core-auth (JWT), Azure Blob Storage
- dox-mcp-server repository exists but is empty (only placeholder README)

**Key Gaps to Address:**
- No actual implementation exists - only documentation
- Flask-based architecture needs conversion to FastAPI
- MCP server integration is completely missing
- No AI-powered template management capabilities

## Desired End State

**dox-tmpl-pdf-upload Service:**
- FastAPI-based REST API for PDF template management
- Async file upload with multi-layer validation
- Integration with existing services (dox-core-store, dox-core-auth, Azure Blob Storage)
- Comprehensive error handling and logging
- Health checks and monitoring endpoints

**dox-mcp-server Service:**
- MCP server exposing PDF template management as AI tools
- Tools for upload, search, validation, and metadata extraction
- Prompts for template analysis and field detection
- Seamless integration with dox-tmpl-pdf-upload service

**Integration Benefits:**
- AI assistants can manage PDF templates through MCP protocol
- REST API maintains compatibility with existing systems
- Enhanced template processing with AI-powered capabilities
- Unified template management across different access patterns

---

## Repository: dox-tmpl-pdf-upload

### FastAPI Service Implementation

**Purpose:** Convert Flask-based architecture to FastAPI with async support

**Technology Stack Changes:**
- **Framework:** Flask → FastAPI (for async support and automatic OpenAPI)
- **File Handling:** Werkzeug → FastAPI UploadFile with async support
- **Validation:** Custom Flask validation → Pydantic models + FastAPI dependencies
- **Authentication:** Flask-JWT → FastAPI JWT dependencies
- **Rate Limiting:** Flask-Limiter → slowapi (FastAPI rate limiting)

**File Structure:**
```
dox-tmpl-pdf-upload/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── templates.py    # Template CRUD endpoints
│   │   │   │   ├── upload.py       # File upload endpoints
│   │   │   │   └── health.py       # Health check endpoints
│   │   │   └── api.py         # API router assembly
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration management
│   │   ├── security.py       # JWT authentication
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── exceptions.py     # Custom exceptions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py       # Database models
│   │   └── schemas.py        # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── validation.py     # Multi-layer file validation
│   │   ├── storage.py        # Azure Blob Storage integration
│   │   ├── auth.py           # JWT validation service
│   │   └── templates.py      # Template business logic
│   └── utils/
│       ├── __init__.py
│       ├── logging.py        # Logging configuration
│       └── rate_limit.py     # Rate limiting utilities
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

**Key Implementation Details:**

**File: app/main.py**
- FastAPI application factory with CORS middleware
- OpenAPI configuration for automatic documentation
- Exception handlers for consistent error responses
- Startup/shutdown events for resource management

**File: app/api/v1/endpoints/upload.py**
- Async file upload endpoint with FastAPI UploadFile
- Multi-layer validation pipeline (size, MIME, virus, PDF structure)
- Progress tracking for large uploads
- Integration with validation service and storage service

**File: app/services/validation.py**
- Async validation pipeline using existing patterns from dox-tmpl-pdf-recognizer
- File size validation (configurable, default 50MB)
- MIME type validation with python-magic
- Virus scanning integration (ClamAV)
- PDF structure validation
- Validation results logging and reporting

**File: app/models/schemas.py**
- Pydantic models for request/response validation
- Template creation, update, and response schemas
- File upload response schemas
- Error response schemas with detailed validation messages

**File: app/core/dependencies.py**
- JWT authentication dependency
- Rate limiting dependency
- User context extraction from JWT
- Database session dependency
- File upload size limit dependency

**File: app/core/security.py**
- JWT token validation (integration with dox-core-auth)
- User permission checking
- Secure filename generation
- SAS token generation for blob storage access

**API Endpoints (FastAPI Implementation):**

**POST /api/v1/templates/upload**
- Async multipart file upload
- Real-time validation feedback
- Progress tracking via WebSocket or polling
- Returns template metadata with upload progress

**GET /api/v1/templates**
- Async paginated template listing
- Advanced filtering (category, date range, file size)
- Search functionality with full-text search
- Sorting options

**GET /api/v1/templates/{template_id}**
- Template metadata retrieval
- Include validation results and scan reports
- Related templates suggestions

**GET /api/v1/templates/{template_id}/download**
- Streaming PDF download
- SAS token generation for secure blob access
- Download tracking and audit logging

**DELETE /api/v1/templates/{template_id}**
- Soft delete with audit trail
- Cascade deletion of dependent records
- Blob storage cleanup

**POST /api/v1/templates/{template_id}/validate**
- Re-validate existing template against current rules
- Detailed validation report
- Recommendations for improvement

**Authentication & Security:**
- JWT validation via dox-core-auth integration
- Role-based access control (upload, read, admin)
- Rate limiting per user and endpoint
- Request logging with correlation IDs
- Input validation and sanitization

**File Storage Integration:**
- Azure Blob Storage async client
- Container management (pact-templates)
- Blob naming convention: {template_id}/original.pdf
- SAS token generation for secure access
- Storage redundancy and backup policies

**Database Integration:**
- Async database connections (asyncpg for MSSQL)
- Connection pooling and retry logic
- Stored procedure calls for complex operations
- Transaction management for data consistency
- Database health monitoring

---

## Repository: dox-mcp-server

### MCP Server Implementation

**Purpose:** Provide AI-native access to PDF template management through Model Context Protocol

**Technology Stack:**
- **Framework:** FastMCP (Python MCP SDK)
- **Transport:** HTTP + WebSocket (for streaming operations)
- **Authentication:** API key + JWT token validation
- **Integration:** HTTP client for dox-tmpl-pdf-upload service

**File Structure:**
```
dox-mcp-server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # MCP server setup
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── template_upload.py  # Template upload tool
│   │   ├── template_search.py  # Template search tool
│   │   ├── template_validate.py# Template validation tool
│   │   └── template_info.py    # Template information tool
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── analyze_template.py # Template analysis prompt
│   │   ├── field_detection.py  # Field detection prompt
│   │   └── template_comparison.py # Template comparison prompt
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── template_list.py    # Template listing resource
│   │   └── validation_report.py # Validation report resource
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py       # HTTP client for FastAPI service
│   │   ├── auth.py             # MCP authentication
│   │   └── utils.py            # Utility functions
│   └── models/
│       ├── __init__.py
│       ├── schemas.py          # MCP data models
│       └── enums.py            # Enums and constants
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

**MCP Tools Implementation:**

**File: app/tools/template_upload.py**
```python
@mcp.tool()
async def upload_pdf_template(
    file_path: str,
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    validation_level: str = "standard"
) -> Dict[str, Any]:
    """
    Upload a PDF template with AI-powered validation and metadata extraction.

    Args:
        file_path: Local path to PDF file
        name: Template name
        description: Optional template description
        category: Optional template category
        validation_level: Validation strictness (basic/standard/comprehensive)

    Returns:
        Template metadata with validation results and AI-generated insights
    """
```

**File: app/tools/template_search.py**
```python
@mcp.tool()
async def search_templates(
    query: Optional[str] = None,
    category: Optional[str] = None,
    date_range: Optional[str] = None,
    file_size_range: Optional[str] = None,
    validation_status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search PDF templates with intelligent filtering and semantic search.

    Args:
        query: Natural language search query
        category: Filter by template category
        date_range: Date range filter (e.g., "last_30_days", "2024-01-01:2024-12-31")
        file_size_range: File size range filter (e.g., "1MB-10MB", ">5MB")
        validation_status: Filter by validation status

    Returns:
        List of matching templates with relevance scores and metadata
    """
```

**File: app/tools/template_validate.py**
```python
@mcp.tool()
async def validate_template_with_ai(
    template_id: str,
    validation_type: str = "comprehensive",
    include_field_detection: bool = True,
    generate_suggestions: bool = True
) -> Dict[str, Any]:
    """
    Perform AI-powered template validation with field detection and improvement suggestions.

    Args:
        template_id: Template ID to validate
        validation_type: Type of validation (basic/standard/comprehensive)
        include_field_detection: Whether to detect form fields
        generate_suggestions: Whether to generate improvement suggestions

    Returns:
        Detailed validation report with AI insights and recommendations
    """
```

**File: app/tools/template_info.py**
```python
@mcp.tool()
async def get_template_insights(
    template_id: str,
    include_usage_stats: bool = True,
    include_comparison: bool = False,
    analysis_depth: str = "standard"
) -> Dict[str, Any]:
    """
    Get comprehensive template information with AI-generated insights.

    Args:
        template_id: Template ID
        include_usage_stats: Include usage statistics
        include_comparison: Compare with similar templates
        analysis_depth: Depth of AI analysis (basic/standard/deep)

    Returns:
        Comprehensive template information with AI insights
    """
```

**MCP Prompts Implementation:**

**File: app/prompts/analyze_template.py**
```python
@mcp.prompt()
async def analyze_template_structure(template_id: str) -> str:
    """
    Generate a comprehensive analysis prompt for template structure and content.

    Args:
        template_id: Template ID to analyze

    Returns:
        Analysis prompt with context and instructions
    """
```

**File: app/prompts/field_detection.py**
```python
@mcp.prompt()
async def detect_form_fields(
    template_id: str,
    field_types: Optional[List[str]] = None
) -> str:
    """
    Generate a prompt for detecting and analyzing form fields in a PDF template.

    Args:
        template_id: Template ID to analyze
        field_types: Specific field types to focus on

    Returns:
        Field detection prompt with examples and context
    """
```

**MCP Resources Implementation:**

**File: app/resources/template_list.py**
```python
@mcp.resource("templates://list")
async def list_all_templates() -> str:
    """
    Resource providing a comprehensive list of all available templates.

    Returns:
        JSON-structured list of templates with metadata
    """
```

**File: app/resources/validation_report.py**
```python
@mcp.resource("templates://{template_id}/validation-report")
async def get_validation_report(template_id: str) -> str:
    """
    Resource providing detailed validation report for a specific template.

    Args:
        template_id: Template ID

    Returns:
        Detailed validation report in JSON format
    """
```

**Authentication & Security:**
- API key validation for MCP server access
- JWT token forwarding to FastAPI service
- Request rate limiting per API key
- Audit logging for all MCP operations
- Secure file handling for uploads

**Integration Service:**

**File: app/services/api_client.py**
- Async HTTP client for FastAPI service communication
- Retry logic and circuit breaker patterns
- Response caching for frequently accessed data
- Error handling and translation for MCP protocol
- Streaming support for large file operations

---

## Cross-Repository Integration

### Service Communication Architecture

**Communication Flow:**
1. **MCP Server** receives tool/prompt requests from AI clients
2. **MCP Server** validates requests and forwards to **FastAPI Service**
3. **FastAPI Service** processes business logic and data operations
4. **FastAPI Service** integrates with **dox-core-store**, **dox-core-auth**, **Azure Blob Storage**
5. **Results flow back** through MCP Server to AI client

**Authentication Flow:**
1. AI client provides API key to MCP Server
2. MCP Server validates API key and obtains JWT token
3. MCP Server forwards JWT token to FastAPI Service
4. FastAPI Service validates JWT with dox-core-auth
5. User context established for all operations

**Data Flow Patterns:**
- **Upload Flow:** AI Client → MCP Server → FastAPI Service → Validation → Storage → Database
- **Search Flow:** AI Client → MCP Server → FastAPI Service → Database Query → AI-enhanced Results
- **Validation Flow:** AI Client → MCP Server → FastAPI Service → File Retrieval → Validation → AI Analysis

### Shared Configuration

**Environment Variables:**
```bash
# FastAPI Service
DOX_PDF_UPLOAD_PORT=8080
DOX_PDF_UPLOAD_HOST=0.0.0.0
DOX_CORE_STORE_URL=mssql://user:pass@host:port/db
DOX_CORE_AUTH_URL=http://dox-core-auth:8080
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=...
BLOB_CONTAINER_NAME=pact-templates
MAX_FILE_SIZE=52428800  # 50MB
RATE_LIMIT_UPLOADS=10_per_hour
RATE_LIMIT_REQUESTS=100_per_hour

# MCP Server
DOX_MCP_SERVER_PORT=8081
DOX_MCP_SERVER_HOST=0.0.0.0
DOX_PDF_UPLOAD_API_URL=http://dox-tmpl-pdf-upload:8080
MCP_API_KEY=your-secret-api-key
MCP_JWT_SECRET=your-jwt-secret
```

### Deployment Architecture

**Docker Compose Configuration:**
```yaml
version: '3.8'
services:
  dox-tmpl-pdf-upload:
    build: ./dox-tmpl-pdf-upload
    ports:
      - "8080:8080"
    environment:
      - DOX_CORE_STORE_URL=${DOX_CORE_STORE_URL}
      - DOX_CORE_AUTH_URL=${DOX_CORE_AUTH_URL}
      - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
    depends_on:
      - dox-core-store
      - dox-core-auth

  dox-mcp-server:
    build: ./dox-mcp-server
    ports:
      - "8081:8081"
    environment:
      - DOX_PDF_UPLOAD_API_URL=http://dox-tmpl-pdf-upload:8080
      - MCP_API_KEY=${MCP_API_KEY}
    depends_on:
      - dox-tmpl-pdf-upload
```

---

## Implementation Phases

### Phase 1: FastAPI Service Foundation (Week 1-2)

**Week 1: Core Infrastructure**
- Set up FastAPI project structure
- Implement basic configuration and dependencies
- Create database models and schemas
- Set up authentication and security
- Implement health check endpoints

**Week 2: File Upload & Validation**
- Implement async file upload endpoint
- Create multi-layer validation pipeline
- Integrate with Azure Blob Storage
- Add error handling and logging
- Implement rate limiting

### Phase 2: Template Management (Week 3-4)

**Week 3: CRUD Operations**
- Implement template CRUD endpoints
- Add search and filtering capabilities
- Implement pagination and sorting
- Add metadata management
- Create audit logging

**Week 4: Advanced Features**
- Implement template validation endpoint
- Add download functionality with SAS tokens
- Create template versioning support
- Add usage analytics
- Implement soft delete with cleanup

### Phase 3: MCP Server Implementation (Week 5-6)

**Week 5: MCP Foundation**
- Set up FastMCP server structure
- Implement authentication and API client
- Create basic tools (upload, search, info)
- Add error handling and logging
- Set up resource providers

**Week 6: Advanced MCP Features**
- Implement AI-powered tools and prompts
- Add field detection capabilities
- Create template analysis prompts
- Implement comparison features
- Add caching and optimization

### Phase 4: Integration & Testing (Week 7-8)

**Week 7: Integration Testing**
- End-to-end testing of both services
- Performance testing and optimization
- Security testing and validation
- Documentation completion
- CI/CD pipeline setup

**Week 8: Deployment & Monitoring**
- Production deployment preparation
- Monitoring and alerting setup
- Load testing and scaling validation
- User acceptance testing
- Production release

---

## Testing Strategy

### Unit Testing
- **FastAPI Service:** pytest with async support
- **MCP Server:** MCP client testing framework
- **Validation Pipeline:** Mock file testing
- **Database Operations:** In-memory database testing

### Integration Testing
- **Service Communication:** HTTP client mocking
- **Authentication Flow:** JWT token testing
- **File Storage:** Azure Storage emulator
- **Database Integration:** Test container databases

### End-to-End Testing
- **Upload Flow:** Complete file upload pipeline
- **MCP Operations:** AI client simulation
- **Error Scenarios:** Failure testing and recovery
- **Performance Testing:** Load and stress testing

### Security Testing
- **Authentication:** JWT token validation
- **Authorization:** Role-based access testing
- **File Security:** Malicious file testing
- **API Security:** Rate limiting and DDoS testing

---

## Monitoring & Observability

### Metrics Collection
- **FastAPI Service:** Prometheus metrics for request/response
- **MCP Server:** MCP operation metrics and AI interactions
- **File Operations:** Upload/download performance metrics
- **Validation Pipeline:** Validation success/failure rates

### Logging Strategy
- **Structured Logging:** JSON format with correlation IDs
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Security Logging:** Authentication/authorization events
- **Audit Logging:** All template operations and changes

### Health Monitoring
- **Service Health:** Application and dependency health checks
- **Database Health:** Connection pool and query performance
- **Storage Health:** Azure Blob Storage connectivity
- **MCP Health:** Server availability and response times

### Alerting
- **Service Downtime:** Immediate alerts for service failures
- **Performance Degradation:** Alerts for slow responses
- **Security Events:** Alerts for suspicious activities
- **Resource Exhaustion:** Alerts for high resource usage

---

## Security Considerations

### Authentication & Authorization
- **JWT Validation:** Integration with dox-core-auth
- **API Key Security:** Secure key management for MCP server
- **Role-Based Access:** Different permissions for different operations
- **Token Expiration:** Proper token lifecycle management

### File Security
- **File Type Validation:** Strict PDF-only enforcement
- **Virus Scanning:** ClamAV integration for malware detection
- **File Size Limits:** Configurable size restrictions
- **Secure Storage:** Encrypted storage at rest

### API Security
- **Rate Limiting:** Per-user and per-endpoint limits
- **Input Validation:** Comprehensive input sanitization
- **CORS Configuration:** Proper cross-origin resource sharing
- **HTTPS Enforcement:** TLS-only communication

### Data Protection
- **PII Protection:** No personal information in logs
- **Data Encryption:** Encryption in transit and at rest
- **Access Logging:** Complete audit trail
- **Data Retention:** Configurable retention policies

---

## Performance Optimization

### Async Operations
- **File Upload:** Streaming upload with progress tracking
- **Database Queries:** Async database operations
- **Validation Pipeline:** Parallel validation steps
- **API Calls:** Non-blocking HTTP client calls

### Caching Strategy
- **Metadata Caching:** Redis for frequently accessed templates
- **Validation Caching:** Cache validation results
- **API Response Caching**: Cache read-only operations
- **File Metadata**: Cache file information

### Database Optimization
- **Connection Pooling**: Async connection management
- **Query Optimization**: Indexed queries for performance
- **Batch Operations**: Bulk operations for efficiency
- **Read Replicas**: Read scaling for large deployments

### Storage Optimization
- **CDN Integration**: Content delivery for downloads
- **Blob Storage Tiers**: Hot/cold storage tiers
- **Compression**: File compression where applicable
- **Parallel Uploads**: Multipart upload for large files

---

## Migration & Deployment

### Migration Strategy
- **Blue-Green Deployment**: Zero-downtime deployment
- **Database Migrations**: Automated schema updates
- **Configuration Management**: Environment-specific configs
- **Rollback Planning**: Quick rollback procedures

### Container Deployment
- **Docker Images**: Optimized multi-stage builds
- **Kubernetes**: Container orchestration for scaling
- **Health Checks**: Proper container health monitoring
- **Resource Limits**: CPU and memory constraints

### CI/CD Pipeline
- **Automated Testing**: Test automation in pipeline
- **Security Scanning**: Container and code scanning
- **Deployment Automation**: Automated deployment to production
- **Monitoring Integration**: Automatic monitoring setup

---

## Success Criteria

### Functional Requirements
- ✅ FastAPI service with complete template management
- ✅ MCP server with AI-powered template operations
- ✅ Multi-layer file validation (size, MIME, virus, structure)
- ✅ Integration with existing services (dox-core-store, dox-core-auth)
- ✅ Azure Blob Storage integration
- ✅ Comprehensive error handling and logging

### Performance Requirements
- ✅ File upload: < 3 seconds for 5MB files
- ✅ Template search: < 200ms response time
- ✅ File download: < 2 seconds for 10MB files
- ✅ MCP tool responses: < 1 second for most operations
- ✅ 99.9% uptime for both services

### Security Requirements
- ✅ JWT authentication with role-based access
- ✅ File security validation and virus scanning
- ✅ Rate limiting and DDoS protection
- ✅ Audit logging for all operations
- ✅ Data encryption at rest and in transit

### Integration Requirements
- ✅ Seamless integration with existing dox services
- ✅ MCP protocol compliance for AI client compatibility
- ✅ OpenAPI documentation for REST API
- ✅ Comprehensive monitoring and alerting
- ✅ Scalable architecture for future growth

---

This comprehensive implementation plan provides a clear roadmap for converting the Flask-based dox-tmpl-pdf-upload service to FastAPI while adding MCP integration for AI-powered template management capabilities.

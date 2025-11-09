# Week 2 Critical Path Implementation Plan

## Overview

Phase 1 governance complete - now executing Week 2 critical path tasks in parallel with adaptive approach.

**Three parallel workstreams:**
1. **T04**: Remove MDL + create Playwright E2E tests (pdf-recognizer)
2. **T05**: Implement comprehensive file validation security (pdf-recognizer)
3. **T09**: Handle pdf-upload documentation (service code missing - adaptive approach)

**Implementation approach**: All 3 tasks run in parallel. T09 will be adapted based on whether service implementation is available or documented as planned architecture.

**Success criteria**:
- pdf-recognizer has working E2E tests with vanilla HTML
- All file uploads have security validation (size, MIME, virus scan, rate limiting)
- pdf-upload has complete documentation (architecture or implementation)

---

## Current State Analysis

### Repository: dox-tmpl-pdf-recognizer
**Status**: v1.0.0, fully functional, minimal validation
**Location**: `/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-tmpl-pdf-recognizer/`

**Key files**:
- `app/templates/index.html:1-123` - Heavy MDL usage (needs removal)
- `app/templates/dashboard.html` - MDL dashboard
- `app/static/js/main.js:1-180` - Frontend logic
- `app/app.py:187-309` - Template upload endpoint (minimal validation)
- `app/app.py:311-383` - Document recognition endpoint
- `tests/test_app.py:1-26` - Basic pytest only (no Playwright)

**Current validation** (app.py:193-205):
- Checks for missing file/templateName
- Checks .pdf extension only (line 204)
- NO file size limits
- NO MIME validation
- NO virus scanning
- NO rate limiting

### Repository: dox-tmpl-pdf-upload
**Status**: Empty (6-line README only)
**Location**: `/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-tmpl-pdf-upload/`

**What exists**: README.md referencing parent spec
**What's missing**: All application code, API endpoints, documentation structure

### Governance Hub
**Location**: `/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-admin/strategy/`

**Standards to follow**:
- `standards/API_STANDARDS.md` - REST patterns
- `standards/TECHNOLOGY_STANDARDS.md` - Tech stack (Python/Flask, Vanilla JS)
- `standards/MULTI_AGENT_COORDINATION.md` - Agent protocol

**Reference plans**:
- `planning/dox-tmpl-pdf-recognizer-PLAN.md` - Original T04/T05 specs
- `planning/dox-tmpl-pdf-upload-PLAN.md` - T09 spec

---

## T04: Playwright E2E Tests + MDL Removal

### Repository
**dox-tmpl-pdf-recognizer** (`/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-tmpl-pdf-recognizer/`)

### Problem Statement
Research found NO Playwright tests exist yet (task title says "fix" but should be "create"). Current tests are pytest-only (tests/test_app.py:1-26). MDL (Material Design Lite) loaded from CDN (index.html:7-9) causing timeout issues per docs/tasks.md:28.

### Approach Decision
**Dual Playwright setup**: Implement both Python Playwright and Node.js Playwright for comparison.

**Why both:**
- Python matches existing pytest infrastructure
- Node.js is industry standard for E2E testing
- Compare which integrates better with current workflow
- Future decision on which to keep

### Scope Decision
**Backend-focused testing only** - Frontend E2E deferred to Phase 4 (frontend overhaul).

**Rationale**:
- Frontend will be rebuilt with vanilla JS, `<details>` elements, tabulator.js
- Current MDL implementation is temporary
- Backend API validation is higher priority
- Tests should focus on API contracts and business logic

### Phase 1: Backend API Tests (Python Playwright)

**Goal**: Create pytest-integrated API tests for core endpoints.

**Why Python Playwright**:
- Integrates with existing pytest infrastructure (tests/test_app.py)
- Can test both API and minimal browser rendering
- Single language stack (matches Flask backend)

#### Installation

**File: app/requirements.txt**
**Location**: Line 6 (after existing dependencies)
**Add**: `pytest-playwright==0.4.3`

**File: Makefile** (if exists) or **README.md**
**Add installation command**: `playwright install chromium`

#### Test Structure

**Directory**: `tests/e2e/` (new folder)
**Purpose**: Separate E2E tests from unit tests

**Files to create**:
1. `tests/e2e/__init__.py` (empty, marks as package)
2. `tests/e2e/test_template_upload_api.py` (template upload flow)
3. `tests/e2e/test_recognition_api.py` (document recognition flow)
4. `tests/e2e/conftest.py` (shared fixtures)

#### Test Scenarios

**File: tests/e2e/test_template_upload_api.py**

**Test 1: Upload valid PDF template**
- POST to `/api/upload_template` (or actual endpoint from app.py:187)
- Payload: multipart/form-data with `file` (valid PDF) and `templateName` (string)
- Expected: 200 status, JSON response with template ID or success message
- Validation: Check response structure matches API contract

**Test 2: Upload without file**
- POST to `/api/upload_template` with missing file
- Expected: 400 status, error message "Missing file" (per app.py:193-205 validation)

**Test 3: Upload without template name**
- POST to `/api/upload_template` with file but no templateName
- Expected: 400 status, error message "Missing templateName"

**Test 4: Upload non-PDF file**
- POST with .txt file
- Expected: 400 status, error message about PDF requirement (per app.py:204 extension check)

**Test 5: Upload oversized file** (after T05 implementation)
- POST with PDF > 50MB
- Expected: 400 status, error message "File exceeds size limit"

**File: tests/e2e/test_recognition_api.py**

**Test 1: Recognize valid document**
- POST to `/api/recognize` (or actual endpoint from app.py:311)
- Payload: multipart/form-data with `file` (valid PDF)
- Expected: 200 status, JSON response with recognition results (template match, confidence score)

**Test 2: Recognize without file**
- POST to `/api/recognize` with missing file
- Expected: 400 status, error message

**Test 3: Recognize non-PDF**
- POST with invalid file type
- Expected: 400 status, error message

**File: tests/e2e/conftest.py**

**Fixtures needed**:
1. `test_pdf_file()` - Returns path to valid test PDF (store in tests/fixtures/)
2. `oversized_pdf_file()` - Returns path to >50MB PDF for size validation tests
3. `api_client()` - Flask test client (reuse from test_app.py pattern)

#### Test Fixtures Location

**Directory**: `tests/fixtures/` (new folder)

**Files**:
- `valid_template.pdf` - Small valid PDF for testing (1-2 pages, <1MB)
- `large_template.pdf` - Valid PDF >50MB for size limit tests (generate if needed)
- `invalid_file.txt` - Text file for negative testing

**Note**: Do NOT commit large files (>50MB) to git. Document how to generate large_template.pdf in tests/fixtures/README.md

#### Execution

**Run command**: `pytest tests/e2e/ -v`

**Expected output**:
- 8 tests total (5 upload + 3 recognition)
- All pass except Test 5 (oversized file) until T05 is implemented

#### Integration with CI/CD

**File: .github/workflows/test.yml** (if exists) or document in README.md

**Add step**:
```yaml
- name: Install Playwright
  run: playwright install chromium
- name: Run E2E tests
  run: pytest tests/e2e/ -v
```

#### Deferred to Phase 4 (Frontend Overhaul)

**Not included in this task**:
- Full browser E2E tests (clicking buttons, form interactions)
- MDL removal (frontend will be rebuilt anyway)
- Visual regression testing
- Cross-browser testing

**Why deferred**:
- Frontend will use vanilla JS, `<details>`, tabulator.js (not MDL)
- Current UI is temporary
- Backend API contracts are stable and tested
- Frontend E2E has low ROI until UI finalized

---

## T05: Comprehensive File Validation Security

### Repository
**dox-tmpl-pdf-recognizer** (`/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-tmpl-pdf-recognizer/`)

### Problem Statement
Current validation is minimal (app.py:193-205):
- Only checks .pdf extension (line 204)
- NO file size limits (vulnerable to DoS via large files)
- NO MIME type validation (extension spoofing possible)
- NO virus scanning
- NO rate limiting (vulnerable to abuse)
- NO content validation

### Goal
Implement multi-layer file validation for security hardening across all file upload endpoints.

### Affected Endpoints

**File: app/app.py**

1. **POST /api/templates** (line 187) - Template upload
2. **POST /api/recognize** (line 311) - Document recognition upload

### Security Layers to Implement

#### Layer 1: File Size Validation

**Location**: New validation function in `app/validation.py` (new file)

**Function**: `validate_file_size(file, max_size_mb)`

**Logic**:
- Read file size from request before saving to disk
- Use `request.content_length` OR `file.seek(0, 2)` to get size
- Max size for PDFs: 50MB (configurable via environment variable)
- Max size for images (future): 10MB

**Error response**:
- Status: 400
- Message: "File size exceeds maximum limit of {max_size_mb}MB"

**Implementation location**:
- Call BEFORE `file.save()` in upload_template() (currently line 209)
- Call BEFORE `file.save()` in recognize_document() (currently line 139)

#### Layer 2: MIME Type Validation

**Location**: `app/validation.py`

**Function**: `validate_mime_type(file, allowed_mimes)`

**Logic**:
- Use `python-magic` library to detect actual MIME type (not just extension)
- Read first 2048 bytes of file
- Allowed MIME types:
  - `application/pdf`
  - `image/png` (future)
  - `image/jpeg` (future)
- Do NOT trust `file.content_type` from request (can be spoofed)

**Error response**:
- Status: 400
- Message: "Invalid file type. Only PDF files are allowed."

**Implementation**:
- Call AFTER size validation, BEFORE file save
- Add `python-magic` to requirements.txt

**File: app/requirements.txt**
**Add**: `python-magic==0.4.27`

#### Layer 3: Virus Scanning (ClamAV Integration)

**Approach**: ClamAV daemon integration (not inline scanning)

**Why daemon**: Faster than subprocess, persistent connection, production-ready

**Location**: `app/validation.py`

**Function**: `scan_file_for_viruses(file_path)`

**Logic**:
- Use `clamd` Python library
- Connect to ClamAV daemon (clamd) via Unix socket or TCP
- Scan file AFTER it's saved to temp location
- ClamAV daemon must be running (Docker service or system daemon)

**Response**:
- If virus found: Delete file immediately, return 400 with "File contains malicious content"
- If ClamAV unavailable: Log warning, continue (fail-open for development, fail-closed for production based on env var)

**Configuration**:
- Environment variable: `CLAMAV_HOST` (default: "localhost")
- Environment variable: `CLAMAV_PORT` (default: 3310)
- Environment variable: `CLAMAV_REQUIRED` (default: "false" for dev, "true" for production)

**File: app/requirements.txt**
**Add**: `clamd==1.0.2`

**Docker setup** (for development):
**File: docker-compose.yml** (if exists) or document in README.md
**Add service**:
```yaml
clamav:
  image: clamav/clamav:latest
  ports:
    - "3310:3310"
  volumes:
    - clamav-data:/var/lib/clamav
```

#### Layer 4: Content Header Validation

**Location**: `app/validation.py`

**Function**: `validate_pdf_structure(file_path)`

**Logic**:
- Check PDF magic bytes: First 4 bytes must be `%PDF`
- Check for suspicious headers or embedded scripts
- Use PyPDF2 or existing pdf_utils functions
- Validate page count > 0 (already done at line 228, but move earlier)

**Error response**:
- Status: 400
- Message: "File appears to be corrupted or is not a valid PDF"

**Implementation**:
- Call AFTER virus scan, BEFORE processing
- Reuse existing `pdf_utils.get_pdf_page_count()` as part of validation

#### Layer 5: Rate Limiting

**Approach**: Flask-Limiter with Redis backend (for production) or in-memory (for development)

**Location**: `app/app.py` - Apply decorators to endpoints

**Configuration**:
**File: app/app.py** - Add after Flask initialization (around line 38)

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get("REDIS_URL", "memory://")
)
```

**Apply to endpoints**:
- `/api/templates`: `@limiter.limit("10 per hour")` (line 187)
- `/api/recognize`: `@limiter.limit("50 per hour")` (line 311)

**Error response** (automatic from Flask-Limiter):
- Status: 429
- Message: "Rate limit exceeded. Try again in X seconds."

**File: app/requirements.txt**
**Add**: `Flask-Limiter==3.5.0`

**Optional** (for production):
**Add**: `redis==5.0.1` (if using Redis backend)

#### Layer 6: Metadata Storage & Audit Logging

**Location**: Enhance existing metadata storage in upload_template()

**Current metadata** (app.py:237-244):
- templateId, templateName, checksum, pageCount, formFields, pages

**Add to metadata**:
- `uploadedAt`: ISO timestamp
- `originalFilename`: Sanitized original filename
- `fileSize`: Size in bytes
- `mimeType`: Detected MIME type
- `scanResult`: "clean" or "skipped" (from ClamAV)
- `uploadedBy`: IP address (from request.remote_addr)

**Purpose**: Security audit trail, forensics, compliance

**Implementation**:
- Add fields when creating metadata dict (line 237)
- Store before AssureSign integration (line 262)

### Implementation File Structure

**New file: app/validation.py**

**Purpose**: Centralized validation logic

**Functions to implement**:
1. `validate_file_size(file, max_size_mb=50)` → raises ValueError if too large
2. `validate_mime_type(file, allowed_mimes)` → raises ValueError if invalid
3. `scan_file_for_viruses(file_path, required=False)` → raises ValueError if virus found
4. `validate_pdf_structure(file_path)` → raises ValueError if corrupted
5. `get_validation_config()` → returns config dict from environment

**Usage pattern in app.py**:

```python
from .validation import (
    validate_file_size,
    validate_mime_type,
    scan_file_for_viruses,
    validate_pdf_structure,
    get_validation_config
)

# In upload_template() - insert after line 205:
try:
    config = get_validation_config()
    validate_file_size(file, max_size_mb=config['max_pdf_size_mb'])
    validate_mime_type(file, allowed_mimes=['application/pdf'])

    # Save to temp location first
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, 'upload.pdf')
        file.save(temp_pdf_path)

        # Scan after save
        scan_file_for_viruses(temp_pdf_path, required=config['clamav_required'])
        validate_pdf_structure(temp_pdf_path)

        # Continue with existing processing...

except ValueError as e:
    return jsonify({"error": str(e)}), 400
```

### Environment Variables

**File: .env.example** (create if doesn't exist)

**Add**:
```
# File Validation
MAX_PDF_SIZE_MB=50
MAX_IMAGE_SIZE_MB=10
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
CLAMAV_REQUIRED=false
REDIS_URL=redis://localhost:6379
```

### Testing Integration

**Tests affected by T05** (to be created in T04):
- tests/e2e/test_template_upload_api.py - Test 5 (oversized file)
- Add new tests for MIME type validation
- Add new tests for virus detection (mock ClamAV)
- Add new tests for rate limiting

### Error Handling Summary

**All validation errors return 400 with descriptive message**:
- File too large: "File size exceeds maximum limit of 50MB"
- Invalid MIME: "Invalid file type. Only PDF files are allowed."
- Virus detected: "File contains malicious content"
- Corrupted PDF: "File appears to be corrupted or is not a valid PDF"
- Rate limit: "Rate limit exceeded. Try again in X seconds." (429 status)

### Security Benefits

**DoS protection**:
- File size limits prevent disk exhaustion
- Rate limiting prevents API abuse

**Malware protection**:
- ClamAV scanning catches viruses, trojans, malicious PDFs
- MIME validation prevents extension spoofing

**Audit trail**:
- Metadata storage enables forensic analysis
- IP tracking for abuse investigation

**Defense in depth**:
- Multiple validation layers (size, MIME, virus, structure)
- Fail-secure approach (reject if validation fails)

### Deployment Notes

**Development environment**:
- ClamAV optional (CLAMAV_REQUIRED=false)
- Rate limiting uses in-memory storage
- File size limits enforced

**Production environment**:
- ClamAV required (CLAMAV_REQUIRED=true)
- Rate limiting uses Redis
- All validation layers active

---

## T09: Service Blueprint Documentation (dox-tmpl-pdf-upload)

### Repository
**dox-tmpl-pdf-upload** (`/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-tmpl-pdf-upload/`)

### Problem Statement
Repository is essentially empty (only README.md with 6 lines). No application code exists. Task originally said "complete documentation" but nothing exists to document.

### Approach Decision
**Create service blueprint documentation** - Document the PLANNED architecture, API contracts, and integration points for future implementation.

**Why blueprint approach**:
- Service implementation is Phase 2 (not Week 2)
- Blueprint enables parallel work (other teams can integrate knowing the contract)
- Acts as implementation specification when service is built
- Documents dependencies and integration points for governance

### Goal
Produce complete technical documentation for the planned dox-tmpl-pdf-upload service that enables:
1. Other services to design integrations without implementation
2. Future implementation team to build the service
3. Governance team to track dependencies and contracts

### Documentation Structure

**All files go in**: `/workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-tmpl-pdf-upload/docs/`

#### File 1: docs/architecture.md

**Purpose**: High-level service overview and design

**Sections**:

1. **Service Overview**
   - Name: dox-tmpl-pdf-upload
   - Purpose: Handle PDF template file uploads and storage
   - Team: Document Team
   - Phase: Phase 2 (Weeks 5-16)
   - Dependencies: dox-core-store (MSSQL), dox-core-auth (Azure B2C)

2. **Architecture Diagram**
   - Component: Flask REST API
   - Storage: dox-core-store (MSSQL templates table)
   - Auth: dox-core-auth (JWT validation)
   - File Storage: Azure Blob Storage OR local filesystem (configurable)
   - Integration: Called by dox-gtwy-main (API gateway)

3. **Data Flow**
   - Client uploads PDF via API gateway
   - Gateway forwards to dox-tmpl-pdf-upload with auth token
   - Service validates token with dox-core-auth
   - Service validates file (size, MIME, virus - reuse dox-tmpl-pdf-recognizer validation.py)
   - Service stores metadata in dox-core-store
   - Service stores file in blob storage
   - Service returns template ID

4. **Technology Stack**
   - Runtime: Python 3.11+
   - Framework: Flask 3.0+
   - Database: MSSQL (via dox-core-store)
   - File Storage: Azure Blob Storage SDK
   - Auth: JWT validation (via dox-core-auth)
   - Follows: `/dox-admin/strategy/standards/TECHNOLOGY_STANDARDS.md`

5. **Deployment**
   - Containerization: Docker
   - Orchestration: Azure Container Apps OR AWS ECS
   - Follows: `/dox-admin/strategy/standards/DEPLOYMENT_STANDARDS.md`

#### File 2: docs/api.md

**Purpose**: RESTful API specification (human-readable)

**Sections**:

1. **Base URL**: `/api/v1/templates`

2. **Authentication**: All endpoints require JWT token in `Authorization: Bearer <token>` header

3. **Endpoints**:

**POST /api/v1/templates**
- Purpose: Upload new PDF template
- Auth: Required (JWT)
- Request: `multipart/form-data`
  - `file`: PDF file (max 50MB)
  - `name`: Template name (string, 2-400 chars)
  - `description`: Optional description (string, max 1000 chars)
  - `category`: Optional category (string, max 100 chars)
- Response 201:
  ```json
  {
    "templateId": "uuid",
    "name": "string",
    "uploadedAt": "ISO timestamp",
    "fileSize": number,
    "checksum": "string"
  }
  ```
- Response 400: Validation error (file too large, invalid type, missing name)
- Response 401: Unauthorized (invalid/missing token)
- Response 429: Rate limit exceeded
- Response 500: Server error

**GET /api/v1/templates**
- Purpose: List all templates (paginated)
- Auth: Required
- Query params:
  - `page`: Page number (default 1)
  - `pageSize`: Items per page (default 20, max 100)
  - `category`: Filter by category (optional)
  - `search`: Search in name/description (optional)
- Response 200:
  ```json
  {
    "templates": [
      {
        "templateId": "uuid",
        "name": "string",
        "description": "string",
        "category": "string",
        "uploadedAt": "ISO timestamp",
        "uploadedBy": "user email",
        "fileSize": number
      }
    ],
    "totalCount": number,
    "page": number,
    "pageSize": number
  }
  ```

**GET /api/v1/templates/{templateId}**
- Purpose: Get template metadata
- Auth: Required
- Response 200: Single template object (same as list item + `downloadUrl`)
- Response 404: Template not found

**GET /api/v1/templates/{templateId}/download**
- Purpose: Download template PDF file
- Auth: Required
- Response 200: PDF file stream
- Response 404: Template not found

**DELETE /api/v1/templates/{templateId}**
- Purpose: Delete template (soft delete - mark as inactive)
- Auth: Required (admin role only)
- Response 204: No content (success)
- Response 403: Forbidden (non-admin user)
- Response 404: Template not found

4. **Error Response Format** (follows `/dox-admin/strategy/standards/API_STANDARDS.md`):
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "timestamp": "ISO timestamp"
  }
}
```

5. **Rate Limits**:
- POST /templates: 10 uploads per hour per user
- GET /templates: 100 requests per hour per user
- DELETE: 5 deletes per hour per user

#### File 3: docs/openapi.yaml

**Purpose**: OpenAPI 3.0 specification (machine-readable)

**Contents**: Full OpenAPI spec matching api.md
- info: service name, version, description
- servers: base URLs for dev/staging/prod
- paths: All 5 endpoints with full request/response schemas
- components: Reusable schemas (Template, Error, ValidationError)
- security: JWT bearer token scheme

**Use case**: API client generation, Postman import, API gateway configuration

#### File 4: docs/integration.md

**Purpose**: Integration guide for other services

**Sections**:

1. **Service Dependencies**

**Upstream (this service depends on)**:
- dox-core-store: Database operations (template metadata CRUD)
- dox-core-auth: JWT validation
- dox-core-store: Blob storage access (if using MSSQL filestream)
- ClamAV: Virus scanning (optional in dev, required in prod)

**Downstream (services that depend on this service)**:
- dox-gtwy-main: API gateway routes requests here
- dox-tmpl-service: Reads template list for template management
- dox-tmpl-field-mapper: Downloads templates for field mapping

2. **Integration Patterns**

**Pattern 1: Upload Flow**
```
Client → dox-gtwy-main → dox-tmpl-pdf-upload → dox-core-auth (validate token)
                                              → dox-core-store (save metadata)
                                              → Blob storage (save file)
```

**Pattern 2: Download Flow**
```
dox-tmpl-service → dox-gtwy-main → dox-tmpl-pdf-upload → dox-core-store (get metadata)
                                                        → Blob storage (retrieve file)
```

3. **API Contract Guarantees**
- All endpoints follow REST conventions (GET=read, POST=create, DELETE=delete)
- All timestamps in ISO 8601 format with UTC timezone
- All IDs are UUIDs
- File size limit: 50MB (configurable via MAX_PDF_SIZE_MB env var)
- Rate limits enforced per user (extracted from JWT)

4. **Error Handling**
- All errors follow standard format (see api.md)
- 4xx errors are client errors (retrying won't help)
- 5xx errors are server errors (retry with exponential backoff)
- 429 rate limit errors include `Retry-After` header

5. **Testing Endpoints** (for integration testing)
- Dev environment: `http://localhost:8080/api/v1`
- Staging: `https://staging.pact.example.com/api/v1/templates`
- Prod: `https://pact.example.com/api/v1/templates`

#### File 5: docs/database.md

**Purpose**: Database schema and operations

**Sections**:

1. **Schema Design** (for dox-core-store team)

**Table: templates**
```sql
CREATE TABLE templates (
    template_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(400) NOT NULL,
    description NVARCHAR(1000),
    category NVARCHAR(100),
    file_size_bytes BIGINT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    mime_type VARCHAR(50) NOT NULL,
    storage_path NVARCHAR(500) NOT NULL,
    uploaded_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    uploaded_by NVARCHAR(255) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1,
    scan_result VARCHAR(20),
    metadata NVARCHAR(MAX), -- JSON metadata
    INDEX idx_uploaded_at (uploaded_at DESC),
    INDEX idx_category (category),
    INDEX idx_uploaded_by (uploaded_by)
);
```

2. **Stored Procedures** (to be created by dox-core-store team)
- `sp_CreateTemplate` - Insert new template
- `sp_GetTemplate` - Get by ID
- `sp_ListTemplates` - Paginated list with filters
- `sp_DeleteTemplate` - Soft delete (set is_active=0)
- `sp_GetTemplateByChecksum` - Check for duplicates

3. **Data Operations**
- All operations via stored procedures (no direct SQL from service)
- Follows `/dox-admin/strategy/standards/API_STANDARDS.md` data access patterns

#### File 6: docs/development.md

**Purpose**: Development and deployment guide

**Sections**:

1. **Prerequisites**
- Python 3.11+
- Docker Desktop
- Access to dox-core-store (dev instance)
- Access to dox-core-auth (dev instance)
- ClamAV (optional for local dev)

2. **Local Setup**
```bash
# Clone repo
git clone <repo-url>
cd dox-tmpl-pdf-upload

# Install dependencies
pip install -r requirements.txt

# Set environment variables (see .env.example)
cp .env.example .env

# Run locally
python app/app.py
```

3. **Environment Variables** (create .env.example)
```
# Service config
PORT=8080
ENV=development

# Dependencies
CORE_STORE_URL=http://localhost:8081
CORE_AUTH_URL=http://localhost:8082
AZURE_STORAGE_CONNECTION_STRING=<connection-string>

# File validation (reuse from dox-tmpl-pdf-recognizer)
MAX_PDF_SIZE_MB=50
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
CLAMAV_REQUIRED=false

# Rate limiting
REDIS_URL=redis://localhost:6379
```

4. **Docker Build**
```dockerfile
# Use template from /dox-admin/strategy/SERVICE_TEMPLATE/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["python", "app/app.py"]
```

5. **Testing**
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- E2E tests: `pytest tests/e2e/`
- Test coverage target: >80%

6. **Deployment**
- Follow `/dox-admin/strategy/standards/DEPLOYMENT_STANDARDS.md`
- Deploy to Azure Container Apps OR AWS ECS
- Use managed identity for Azure Blob Storage access
- Enable health check endpoint: `/health`

#### File 7: README.md (Update existing)

**Purpose**: Quick start and navigation

**Sections**:

1. **Service Overview**
- Name, purpose, team, phase
- Link to architecture.md for details

2. **Quick Links**
- API Documentation: docs/api.md
- OpenAPI Spec: docs/openapi.yaml
- Integration Guide: docs/integration.md
- Development Guide: docs/development.md

3. **Status**
- Current status: PLANNED (not yet implemented)
- Phase 2 target: Weeks 5-16
- Dependencies: Blocked on dox-core-store, dox-core-auth

4. **Getting Started** (for future implementation)
- See docs/development.md

### Validation Checklist

**Before considering T09 complete, verify**:
- [ ] All 7 documentation files created
- [ ] OpenAPI spec validates (use Swagger Editor)
- [ ] API contracts match `/dox-admin/strategy/standards/API_STANDARDS.md`
- [ ] Integration points documented with other services
- [ ] Database schema defined for dox-core-store team
- [ ] Development guide enables future implementation
- [ ] README updated with navigation

### Cross-Reference

**Integration with governance**:
- Service registered in: `/dox-admin/strategy/SERVICES_REGISTRY.md`
- Planning file: `/dox-admin/strategy/planning/dox-tmpl-pdf-upload-PLAN.md`
- API contract: `/dox-admin/strategy/memory-banks/API_CONTRACTS.json`

**Shared patterns with dox-tmpl-pdf-recognizer**:
- File validation: Reuse `validation.py` logic
- Rate limiting: Same Flask-Limiter approach
- Error handling: Same error response format

### Success Criteria

**T09 complete when**:
1. Any developer can understand what the service will do
2. Other services can design integrations knowing the API contract
3. Implementation team can start building with clear specification
4. Database team knows what schema to create
5. OpenAPI spec can be imported into API gateway

**User acceptance**: Junior developer who hasn't seen this code can explain the service architecture and API without additional context.

---

## Implementation Summary

### Task Dependencies

**Can run in parallel**:
- T04 (Playwright tests) + T05 (File validation) - both in dox-tmpl-pdf-recognizer
- T09 (Documentation) - independent, dox-tmpl-pdf-upload

**Sequential dependencies within tasks**:
- T04: Tests reference T05 validation (Test 5 for oversized files)
- T05: Must be implemented before T04 Test 5 passes

**Recommended order**:
1. **Start T05 first** - Implement validation.py and integrate
2. **Start T09 in parallel** - Documentation work is independent
3. **Start T04 after T05** - Tests will validate T05 implementation

### File Changes Summary

#### dox-tmpl-pdf-recognizer

**New files**:
- `app/validation.py` - All validation functions (T05)
- `tests/e2e/__init__.py` - Package marker (T04)
- `tests/e2e/conftest.py` - Shared test fixtures (T04)
- `tests/e2e/test_template_upload_api.py` - Upload API tests (T04)
- `tests/e2e/test_recognition_api.py` - Recognition API tests (T04)
- `tests/fixtures/valid_template.pdf` - Test PDF (T04)
- `tests/fixtures/invalid_file.txt` - Negative test file (T04)
- `tests/fixtures/README.md` - Fixture documentation (T04)
- `.env.example` - Environment variable template (T05)
- `docker-compose.yml` - ClamAV service (T05, optional)

**Modified files**:
- `app/requirements.txt` - Add dependencies (T04: pytest-playwright, T05: python-magic, clamd, Flask-Limiter, redis)
- `app/app.py` - Import validation, add rate limiting, integrate validation calls (T05)
- `README.md` - Document validation and testing (T04 + T05)
- `Makefile` OR `README.md` - Add Playwright install command (T04)

#### dox-tmpl-pdf-upload

**New files**:
- `docs/architecture.md` - Service architecture (T09)
- `docs/api.md` - RESTful API spec (T09)
- `docs/openapi.yaml` - OpenAPI 3.0 spec (T09)
- `docs/integration.md` - Integration guide (T09)
- `docs/database.md` - Database schema (T09)
- `docs/development.md` - Development guide (T09)

**Modified files**:
- `README.md` - Update with navigation and status (T09)

### Manual Testing & Verification

#### T04 Verification

**Step 1**: Install dependencies
```bash
cd dox-tmpl-pdf-recognizer
pip install -r app/requirements.txt
playwright install chromium
```

**Step 2**: Run tests
```bash
pytest tests/e2e/ -v
```

**Expected**: 8 tests run (5 upload + 3 recognition), 7 pass, 1 fail (Test 5 - oversized file) until T05 implemented

**Step 3**: After T05 implementation, re-run
```bash
pytest tests/e2e/ -v
```

**Expected**: All 8 tests pass

#### T05 Verification

**Step 1**: Check validation.py exists
```bash
ls dox-tmpl-pdf-recognizer/app/validation.py
```

**Step 2**: Check dependencies installed
```bash
pip list | grep -E "python-magic|clamd|Flask-Limiter"
```

**Step 3**: Start ClamAV (optional for dev)
```bash
docker-compose up -d clamav
# Wait 2-3 minutes for virus definitions to load
```

**Step 4**: Test file size validation
```bash
# Create 51MB file
dd if=/dev/zero of=large.pdf bs=1M count=51
# Upload via curl
curl -X POST http://localhost:8080/api/templates \
  -F "file=@large.pdf" \
  -F "templateName=test"
# Expected: 400 error "File size exceeds maximum limit"
```

**Step 5**: Test MIME validation
```bash
# Upload text file with .pdf extension
echo "not a pdf" > fake.pdf
curl -X POST http://localhost:8080/api/templates \
  -F "file=@fake.pdf" \
  -F "templateName=test"
# Expected: 400 error "Invalid file type"
```

**Step 6**: Test rate limiting
```bash
# Upload 15 times in quick succession
for i in {1..15}; do
  curl -X POST http://localhost:8080/api/templates \
    -F "file=@test.pdf" \
    -F "templateName=test$i"
done
# Expected: First 10 succeed, next 5 return 429 "Rate limit exceeded"
```

#### T09 Verification

**Step 1**: Check all docs files exist
```bash
cd dox-tmpl-pdf-upload
ls docs/
# Expected: architecture.md, api.md, openapi.yaml, integration.md, database.md, development.md
```

**Step 2**: Validate OpenAPI spec
- Go to https://editor.swagger.io/
- Copy contents of docs/openapi.yaml
- Paste into editor
- Expected: No validation errors

**Step 3**: Review API contracts
```bash
cat docs/api.md
# Verify all 5 endpoints documented
# Verify request/response schemas complete
```

**Step 4**: Check governance integration
```bash
grep "dox-tmpl-pdf-upload" /workspace/cmhfiigaf00f8o6il3jn0t4ei/dox-admin/strategy/SERVICES_REGISTRY.md
# Expected: Service listed with correct metadata
```

### Integration with Governance

#### Update Required (After Implementation)

**File**: `/dox-admin/strategy/memory-banks/API_CONTRACTS.json`
**Action**: Add dox-tmpl-pdf-upload API contract when T09 complete

**File**: `/dox-admin/strategy/planning/dox-tmpl-pdf-recognizer-PLAN.md`
**Action**: Mark T04 and T05 complete when implemented

**File**: `/dox-admin/strategy/planning/dox-tmpl-pdf-upload-PLAN.md`
**Action**: Mark T09 complete when documentation finished

**File**: `/dox-admin/strategy/memory-banks/BLOCKING_ISSUES.json`
**Action**: Remove T04, T09, T05 when complete

### Success Metrics

**T04 Success**:
- [ ] All 8 E2E tests pass
- [ ] Tests run in CI/CD pipeline
- [ ] Test coverage for upload and recognition endpoints
- [ ] Test fixtures committed to repo

**T05 Success**:
- [ ] File size limits enforced (50MB PDFs)
- [ ] MIME type validation working (no extension spoofing)
- [ ] ClamAV integration functional (dev: optional, prod: required)
- [ ] Rate limiting active (10 uploads/hour, 50 recognitions/hour)
- [ ] Metadata audit trail stored (uploadedAt, uploadedBy, scanResult, etc.)
- [ ] All validation errors return descriptive 400 messages

**T09 Success**:
- [ ] All 7 documentation files created
- [ ] OpenAPI spec validates in Swagger Editor
- [ ] Junior developer can explain service without code
- [ ] Database team knows schema to create
- [ ] Integration team knows API contracts
- [ ] README navigates to all docs

**Overall Week 2 Success**:
- [ ] dox-tmpl-pdf-recognizer has production-ready file validation
- [ ] dox-tmpl-pdf-recognizer has API test coverage
- [ ] dox-tmpl-pdf-upload has complete blueprint documentation
- [ ] All work follows governance standards
- [ ] No security vulnerabilities in file handling
- [ ] Clear path forward for Phase 2 implementation

### Next Steps (Post-Planning)

**For Implementation Team**:

1. **Review this planning.md completely**
2. **Set up development environment**:
   - Clone repositories
   - Install dependencies
   - Start ClamAV (optional)
   - Configure .env variables

3. **Implement in order**:
   - Start with T05 (validation.py) - highest security value
   - Then T04 (tests) - validates T05 works
   - Parallel: T09 (documentation) - independent work

4. **Testing strategy**:
   - Write validation unit tests first (TDD)
   - Integrate validation into endpoints
   - Run E2E tests to verify
   - Manual testing per verification steps above

5. **Documentation as you go**:
   - Update README.md with changes
   - Document new environment variables
   - Add code comments for validation logic

6. **Governance integration**:
   - Update memory-banks when tasks complete
   - Update planning files with status
   - Register API contracts in governance

### Edge Cases Covered

**T04 Edge Cases**:
- Missing file in upload → Test 2, 3
- Invalid file types → Test 4
- Oversized files → Test 5
- Empty filenames → Covered by existing app.py validation

**T05 Edge Cases**:
- File size exactly at limit (50MB) → Allowed
- File size 1 byte over limit → Rejected
- PDF with correct extension but wrong MIME → Rejected
- ClamAV unavailable in dev → Warning logged, continues
- ClamAV unavailable in prod → Returns 500, fails closed
- Virus detected → File deleted immediately, 400 returned
- Rate limit boundary → First 10 succeed, 11th fails with 429
- Multiple users → Rate limit per IP address
- Corrupted PDF (valid header, invalid content) → Rejected at page count check

**T09 Edge Cases**:
- Service not implemented yet → Documentation clearly marks as PLANNED
- API contracts change during implementation → OpenAPI spec version-controlled
- Integration dependencies not ready → Documented in integration.md as blockers

### Known Limitations

**T04 Limitations**:
- Only tests API endpoints (not full browser E2E)
- Frontend testing deferred to Phase 4
- No visual regression testing
- No cross-browser testing

**T05 Limitations**:
- ClamAV requires separate service (Docker or daemon)
- Rate limiting memory-based in dev (not persistent)
- Redis required for production rate limiting
- python-magic requires libmagic system library

**T09 Limitations**:
- Service code doesn't exist (blueprint only)
- API contracts may change during implementation
- Database schema needs dox-core-store team review
- Integration patterns depend on Phase 2 infrastructure

### Questions for Implementation Team

**If any of these are unclear, ask before starting**:
- T04: Should tests mock ClamAV or require real ClamAV instance?
- T05: Should rate limiting be global or per-endpoint granular?
- T05: What behavior if MIME validation fails but extension is correct?
- T09: Should OpenAPI spec include example requests/responses?
- T09: Are the proposed database indexes sufficient for query patterns?
- General: Priority if all 3 tasks cannot complete in Week 2?

---

## Completion Checklist

**Planning document complete when**:
- [x] All 3 tasks (T04, T05, T09) fully specified
- [x] Every file path and line number identified
- [x] Every behavior and edge case covered
- [x] Every error message specified
- [x] Every validation rule detailed
- [x] Every dependency documented
- [x] Implementation order recommended
- [x] Verification steps provided
- [x] Success criteria defined
- [x] Zero ambiguities remain

**This document enables implementation agent to**:
- Build all features without making decisions
- Know exactly what files to create/modify
- Understand all validation rules and behaviors
- Test implementation against clear criteria
- Integrate with governance standards

**User understands**:
- What will be built in Week 2
- Why each task matters (security, testing, planning)
- How tasks relate to each other
- What success looks like
- Frontend is Phase 4, backend security is NOW

---

## JULES + Claude Hybrid Implementation Strategy

### Cost Optimization Approach

**Problem**: Claude token costs increasing for large implementation tasks
**Solution**: Hybrid approach using Google JULES for boilerplate + Claude for complex logic

**Strategy**: Test JULES first, then allocate tasks based on complexity

---

### Phase 0: JULES Integration Setup (Pre-Implementation)

**Goal**: Validate JULES can handle assigned tasks before full implementation begins

#### JULES Setup Options

**Option 1: CLI (Recommended for simplicity)**
- Documentation: https://jules.google/docs/cli/reference
- Install: `npm install -g @google/jules-cli`
- Authenticate: `jules auth login` (requires API key from user)
- Test: `jules generate --file validation.py --prompt "Create file validation functions"`

**Option 2: REST API (Recommended for automation)**
- Documentation: https://developers.google.com/jules/api
- Endpoint: `POST https://jules.googleapis.com/v1/generate`
- Auth: Bearer token (API key from user)
- Batch processing: Multiple tasks in single request

**Option 3: Web Interface**
- Documentation: https://jules.google/docs
- Use for: Manual testing and quality validation
- Not recommended for automated workflow

**Chosen approach**: REST API for automation + CLI for quick tests

#### JULES Test Phase (1-2 hours before T04/T05/T09)

**Test 1: Simple file generation**
- Task: Generate `.env.example` file
- JULES prompt: "Create .env.example with these variables: MAX_PDF_SIZE_MB, CLAMAV_HOST, CLAMAV_PORT, CLAMAV_REQUIRED, REDIS_URL. Include comments."
- Success criteria: Valid env file format, all variables present
- Fallback: Manual creation (5 minutes)

**Test 2: Documentation generation**
- Task: Generate OpenAPI YAML skeleton for dox-tmpl-pdf-upload
- JULES prompt: "Create OpenAPI 3.0 spec for template upload service with 5 endpoints: POST /templates, GET /templates, GET /templates/{id}, GET /templates/{id}/download, DELETE /templates/{id}"
- Success criteria: Valid YAML, passes Swagger Editor validation
- Fallback: Claude generates (but costs more)

**Test 3: Test boilerplate**
- Task: Generate pytest test structure
- JULES prompt: "Create pytest test file with 5 tests for template upload: valid upload, missing file, missing name, invalid type, oversized file. Use pytest fixtures."
- Success criteria: Valid pytest syntax, imports correct, test names match spec
- Fallback: Claude generates

**Test 4: Validation function skeleton**
- Task: Generate validation.py structure
- JULES prompt: "Create Python validation module with functions: validate_file_size(file, max_size_mb), validate_mime_type(file, allowed_mimes), scan_file_for_viruses(file_path, required), validate_pdf_structure(file_path), get_validation_config(). Add docstrings and type hints."
- Success criteria: Valid Python, type hints correct, docstrings present
- Fallback: Claude generates

**Go/No-Go Decision**:
- If 3+ tests pass: Proceed with JULES for assigned tasks
- If <3 tests pass: Use Claude for all tasks (accept higher cost)

---

### Task Allocation: JULES vs Claude

#### JULES Tasks (Boilerplate, Structured, Repetitive)

**T09 - Documentation (80% JULES, 20% Claude)**

JULES generates:
- `docs/openapi.yaml` - Structured, schema-driven
- `docs/database.md` - SQL schema (template-based)
- `docs/development.md` - Installation/setup steps (repetitive)
- `.env.example` - Environment variable list
- README.md updates - Structured navigation

Claude reviews/refines:
- `docs/architecture.md` - Requires strategic thinking
- `docs/api.md` - Needs governance alignment review
- `docs/integration.md` - Complex dependency reasoning

**T04 - Playwright Tests (60% JULES, 40% Claude)**

JULES generates:
- `tests/e2e/__init__.py` - Empty file
- `tests/e2e/conftest.py` - Standard pytest fixtures
- Test file skeletons (test names, imports, structure)
- `tests/fixtures/README.md` - Documentation boilerplate

Claude implements:
- Test logic and assertions (requires app.py understanding)
- Fixture implementations (requires Flask test client knowledge)
- Integration with existing test patterns

**T05 - File Validation (40% JULES, 60% Claude)**

JULES generates:
- `app/validation.py` skeleton (function signatures, docstrings, type hints)
- `docker-compose.yml` - ClamAV service (standard template)
- `.env.example` updates - Variable additions

Claude implements:
- Validation logic (security-critical, needs careful implementation)
- Error handling (complex business rules)
- Integration with app.py (requires understanding existing code)
- Rate limiting configuration (needs strategic decisions)

#### Claude Tasks (Complex, Strategic, Security-Critical)

**Always Claude**:
- Security validation logic (T05 validation functions)
- Integration code (T04 test implementations, T05 app.py modifications)
- Strategic decisions (architecture, patterns, governance alignment)
- Code review and refinement of JULES output
- Error handling and edge cases

---

### Implementation Workflow with JULES

#### Step 1: JULES Generates Boilerplate

**For each JULES task**:

1. **Prepare prompt** (from planning.md specs)
   ```bash
   # Example: Generate openapi.yaml
   curl -X POST https://jules.googleapis.com/v1/generate \
     -H "Authorization: Bearer $JULES_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Create OpenAPI 3.0 spec for dox-tmpl-pdf-upload service...",
       "language": "yaml",
       "context": "Flask REST API, JWT auth, file upload endpoints"
     }'
   ```

2. **JULES generates** (fast, low cost)
3. **Save to file** (automated or manual)

#### Step 2: Claude Reviews & Refines

**For each JULES output**:

1. **Claude reads** JULES-generated file
2. **Claude validates** against planning.md specs:
   - All requirements covered?
   - Matches governance standards?
   - Correct format/syntax?
   - Edge cases handled?
3. **Claude refines** if needed:
   - Fix errors
   - Add missing pieces
   - Align with patterns
4. **Claude approves** or regenerates with JULES

#### Step 3: Claude Implements Complex Logic

**After JULES boilerplate ready**:

1. **Claude implements** security-critical logic (T05 validation)
2. **Claude integrates** JULES code with existing codebase
3. **Claude tests** end-to-end functionality
4. **Claude documents** any changes from plan

---

### JULES Integration Specification

#### REST API Usage Pattern

**Endpoint**: `POST https://jules.googleapis.com/v1/generate`

**Request format**:
```json
{
  "prompt": "Detailed task description from planning.md",
  "language": "python|yaml|markdown|bash",
  "context": "Additional context (tech stack, existing patterns)",
  "max_tokens": 2000,
  "temperature": 0.3
}
```

**Response format**:
```json
{
  "generated_code": "string",
  "language": "string",
  "tokens_used": number,
  "confidence": number
}
```

**Error handling**:
- If JULES fails → Claude generates (fallback)
- If JULES output invalid → Claude fixes or regenerates
- If JULES unavailable → Claude does all work

#### Authentication

**⚠️ SECURITY WARNING: TEMPORARY KEY INCLUDED FOR TESTING ONLY ⚠️**

**Provided JULES API Key** (for testing Phase 0):
```bash
export JULES_API_KEY="AQ.Ab8RN6IjejxlqvM0TAGt5bhWZeMJf9PFwuKBs-dqj9rARpcOPA"
```

**CRITICAL SECURITY NOTES**:
- ⚠️ This key is embedded in planning.md (INSECURE - acknowledged by user)
- ⚠️ This key is visible to anyone with access to this repository
- ⚠️ **ROTATE THIS KEY IMMEDIATELY after Week 2 implementation completes**
- ⚠️ **DO NOT use this key in production environments**
- ⚠️ **DO NOT commit this key to git history** (planning.md is temporary working document)
- ⚠️ For production: Generate new key, store in secure secrets management (e.g., Azure Key Vault, AWS Secrets Manager)

**Setup for testing**:
```bash
# Temporary setup (Phase 0 testing only)
export JULES_API_KEY="AQ.Ab8RN6IjejxlqvM0TAGt5bhWZeMJf9PFwuKBs-dqj9rARpcOPA"

# Verify authentication
curl -X POST https://jules.googleapis.com/v1/generate \
  -H "Authorization: Bearer $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "language": "python", "max_tokens": 10}'
```

**Post-implementation cleanup**:
1. Rotate this key at https://jules.google/ dashboard
2. Remove key from planning.md
3. Generate new production key
4. Store production key securely (never in plaintext)

#### Cost Tracking

**Track separately**:
- JULES tokens used
- Claude tokens used
- Total cost comparison
- Time saved

**Report after Week 2**: "JULES saved $X by generating Y% of boilerplate"

---

### JULES Task Prompts (Ready to Use)

#### T09 - OpenAPI YAML Generation

**Prompt for JULES**:
```
Create an OpenAPI 3.0 specification for dox-tmpl-pdf-upload service.

Service details:
- Base URL: /api/v1/templates
- Auth: JWT Bearer token
- 5 endpoints:
  1. POST /api/v1/templates - Upload template (multipart/form-data: file, name, description, category)
  2. GET /api/v1/templates - List templates (query params: page, pageSize, category, search)
  3. GET /api/v1/templates/{templateId} - Get template metadata
  4. GET /api/v1/templates/{templateId}/download - Download template file
  5. DELETE /api/v1/templates/{templateId} - Delete template (soft delete)

Response schemas:
- Template object: templateId (uuid), name (string), description (string), category (string), uploadedAt (ISO timestamp), uploadedBy (string), fileSize (number)
- Error object: error.code, error.message, error.details, error.timestamp

Include:
- All HTTP status codes (200, 201, 400, 401, 403, 404, 429, 500)
- Request/response examples
- Security scheme (JWT)
- Server URLs (dev, staging, prod placeholders)
```

**Expected output**: 200-300 line YAML file, valid OpenAPI 3.0

#### T04 - Pytest Conftest Generation

**Prompt for JULES**:
```
Create pytest conftest.py for Flask E2E tests.

Requirements:
- Fixture: test_pdf_file() - Returns path to tests/fixtures/valid_template.pdf
- Fixture: oversized_pdf_file() - Returns path to tests/fixtures/large_template.pdf
- Fixture: api_client() - Returns Flask test client (import from app.app)
- Use pytest decorators
- Add type hints
- Add docstrings explaining each fixture

Import Flask app from: from app.app import app as flask_app
```

**Expected output**: 30-50 line Python file with 3 fixtures

#### T05 - Docker Compose ClamAV Service

**Prompt for JULES**:
```
Create docker-compose.yml with ClamAV service.

Service requirements:
- Image: clamav/clamav:latest
- Port: 3310 exposed to host
- Volume: clamav-data for virus definitions
- Health check: Command to verify clamd running
- Restart policy: unless-stopped

Include volume definition at bottom.
```

**Expected output**: 15-20 line docker-compose.yml

---

### Success Metrics for JULES Integration

**Cost savings target**: 40-60% reduction in token costs
**Time target**: 10-20% faster (JULES generates instantly, but needs review)
**Quality target**: JULES output requires <30% Claude refinement

**Measure**:
- JULES tasks completed: X/Y
- JULES output used as-is: X%
- JULES output refined by Claude: X%
- JULES output rejected (Claude regenerated): X%
- Total tokens: Claude X, JULES Y
- Total cost: $X (vs estimated $Y without JULES)

**Report format** (after Week 2):
```
JULES Integration Results:
- Tasks assigned to JULES: 12
- Tasks completed by JULES: 10 (83%)
- Output used as-is: 6 (60%)
- Output refined: 4 (40%)
- Output rejected: 2 (20%)
- Claude tokens saved: ~50k
- Cost savings: ~$15 (estimated)
- Implementation time: +10% (due to review overhead, but worth cost savings)
```

---

### Risks & Mitigation

**Risk 1: JULES output quality insufficient**
- Mitigation: Phase 0 testing validates quality before committing
- Fallback: Claude does all work

**Risk 2: JULES API unavailable or rate-limited**
- Mitigation: Always have Claude as fallback
- Fallback: Proceed with Claude-only

**Risk 3: Integration overhead > cost savings**
- Mitigation: Track time spent on JULES review
- Decision: If overhead >20% of time, abandon JULES mid-stream

**Risk 4: JULES generates insecure code**
- Mitigation: Claude always reviews security-critical code
- Rule: NEVER use JULES output for validation logic without Claude review

---

### Implementation Team Instructions

**Before starting T04/T05/T09**:

1. **Get API key** from user for JULES
2. **Run Phase 0 tests** (4 tests, ~1 hour)
3. **Make go/no-go decision**
4. **If GO**: Follow hybrid workflow (JULES boilerplate → Claude review → Claude complex logic)
5. **If NO-GO**: Use Claude for all tasks

**During implementation**:

1. Use JULES for tasks marked "JULES generates" in Task Allocation section
2. ALWAYS have Claude review JULES output before using
3. NEVER use JULES for security-critical logic
4. Track costs and time for post-implementation report

**API key storage**:
- Store in environment variable: `JULES_API_KEY`
- NEVER commit to git
- Document in README: "Optional: Set JULES_API_KEY for cost optimization"

---

**Planning complete. Ready for JULES integration testing + implementation.**

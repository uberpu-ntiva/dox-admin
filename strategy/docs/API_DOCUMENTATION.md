# DOX Platform API Documentation

Complete API documentation for all DOX platform services with workflow integration.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Workflow Orchestrator API](#workflow-orchestrator-api)
3. [Validation Service API](#validation-service-api)
4. [Template PDF Upload API](#template-pdf-upload-api)
5. [Template PDF Recognizer API](#template-pdf-recognizer-api)
6. [Core Services APIs](#core-services-apis)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Webhook Events](#webhook-events)

---

## Authentication

### JWT Authentication
All API endpoints require JWT authentication unless explicitly marked as public.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**API Key Authentication (Alternative):**
```
X-API-Key: <api_key>
```

### Authentication Service Integration
JWT tokens are validated against `dox-core-auth` service.

---

## Workflow Orchestrator API

### Base URL: `http://dox-workflow-orchestrator:5000`

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "dox-workflow-orchestrator",
  "version": "1.0.0",
  "timestamp": "2025-11-02T17:00:00Z",
  "components": {
    "workflow_engine": "healthy",
    "state_manager": "healthy",
    "event_publisher": "healthy",
    "service_connector": "healthy"
  }
}
```

### Start Workflow
```http
POST /api/v1/workflows
```

**Request Body:**
```json
{
  "rule_name": "process_document_upload",
  "context": {
    "document_id": "doc_123456",
    "user_id": "user_789",
    "file_path": "/tmp/upload.pdf",
    "filename": "document.pdf"
  },
  "workflow_id": "optional_custom_id"
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "wf_abc123",
  "rule_name": "process_document_upload",
  "status": "started",
  "timestamp": "2025-11-02T17:00:00Z"
}
```

### Get Workflow Status
```http
GET /api/v1/workflows/{workflow_id}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "wf_abc123",
  "status": "running",
  "current_step": "File Validation",
  "start_time": "2025-11-02T17:00:00Z",
  "steps_completed": 2,
  "step_results": {
    "File Validation": {
      "status": "success",
      "duration_ms": 1500
    }
  }
}
```

### Pause Workflow
```http
POST /api/v1/workflows/{workflow_id}/pause
```

### Resume Workflow
```http
POST /api/v1/workflows/{workflow_id}/resume
```

### Cancel Workflow
```http
DELETE /api/v1/workflows/{workflow_id}
```

### List Workflows
```http
GET /api/v1/workflows?status=running&service=dox-tmpl-pdf-upload&limit=50&offset=0
```

**Query Parameters:**
- `status`: Filter by workflow status (pending, running, success, failed, etc.)
- `service`: Filter by service name
- `limit`: Maximum number of results (default: 50)
- `offset`: Pagination offset (default: 0)

### Trigger Team Coordination
```http
POST /api/v1/coordination/sync
```

**Response:**
```json
{
  "success": true,
  "sync_id": "sync_456789",
  "teams_updated": 7,
  "timestamp": "2025-11-02T17:00:00Z"
}
```

### List Workflow Rules
```http
GET /api/v1/rules
```

**Response:**
```json
{
  "success": true,
  "rules": [
    {
      "name": "process_document_upload",
      "service": "All Upload Services",
      "version": "1.0.0",
      "priority": "high",
      "description": "Main workflow for document upload processing",
      "steps_count": 7,
      "trigger_type": "api_request"
    }
  ],
  "count": 5,
  "timestamp": "2025-11-02T17:00:00Z"
}
```

### Check Services Health
```http
GET /api/v1/services/health
```

---

## Validation Service API

### Base URL: `http://dox-validation-service:5007`

### Health Check
```http
GET /health
```

### Scan File for Viruses
```http
POST /api/v1/validate/scan
```

**Request Body:**
```json
{
  "file_path": "/tmp/upload.pdf",
  "file_hash": "sha256:abc123...",
  "file_size": 1048576
}
```

**Response (Clean):**
```json
{
  "success": true,
  "scan_result": {
    "scan_result": "clean",
    "scan_time": 2.34,
    "scanner": "clamav",
    "file_hash": "sha256:abc123...",
    "file_size": 1048576,
    "timestamp": "2025-11-02T17:00:00Z"
  }
}
```

**Response (Infected):**
```json
{
  "success": false,
  "scan_result": {
    "scan_result": "infected",
    "scan_time": 3.12,
    "scanner": "clamav",
    "file_hash": "sha256:abc123...",
    "threat_name": "Trojan.Generic.ABC",
    "timestamp": "2025-11-02T17:00:00Z"
  }
}
```

### Check Rate Limit
```http
POST /api/v1/validate/rate-check
```

**Request Body:**
```json
{
  "user_id": "user_123",
  "account_id": "account_456",
  "time_window": "24h"
}
```

**Response:**
```json
{
  "within_limit": true,
  "rate_limit_info": {
    "within_limit": true,
    "window_hours": 24,
    "user_count": 45,
    "user_limit": 100,
    "account_count": 200,
    "account_limit": 500,
    "timestamp": "2025-11-02T17:00:00Z"
  }
}
```

### Complete File Validation
```http
POST /api/v1/validate/file
```

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file`: The file to validate (required)
- `user_id`: User ID (optional)
- `account_id`: Account ID (optional)
- `skip_rate_limit`: Skip rate limiting (optional, default: false)

**Response:**
```json
{
  "success": true,
  "validation_result": {
    "file_path": "/tmp/upload.pdf",
    "original_filename": "document.pdf",
    "file_hash": "sha256:abc123...",
    "file_size": 1048576,
    "file_extension": "pdf",
    "validation_timestamp": "2025-11-02T17:00:00Z",
    "steps_completed": [
      "file_size",
      "file_extension",
      "mime_type",
      "virus_scan",
      "format_validation"
    ],
    "final_status": "valid",
    "virus_scan_result": {
      "scan_result": "clean",
      "scan_time": 2.34
    },
    "validation_duration": 3.45
  }
}
```

### Get Validation Configuration
```http
GET /api/v1/validate/config
```

---

## Template PDF Upload API

### Base URL: `http://dox-tmpl-pdf-upload:5002`

### Upload Document
```http
POST /api/v1/documents/upload
```

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file`: The document file (required)
- `metadata`: JSON metadata (optional)

**Headers:**
```
Authorization: Bearer <jwt_token>
X-Request-ID: optional_request_id
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "document_id": "doc_123456",
  "file_hash": "sha256:abc123...",
  "workflow_id": "wf_def789",
  "storage_location": "s3://dox-documents/2025/11/02/doc_123456",
  "validation_result": {
    "final_status": "valid",
    "steps_completed": 5
  },
  "next_steps": {
    "document_classification": "pending",
    "field_extraction": "pending"
  },
  "timestamp": "2025-11-02T17:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Validation failed
- `413 Payload Too Large`: File too large (>50MB)
- `415 Unsupported Media Type`: Invalid file type
- `419 Suspicious Content`: Virus detected
- `429 Too Many Requests`: Rate limit exceeded

### Get Document Status
```http
GET /api/v1/documents/{document_id}/status
```

---

## Template PDF Recognizer API

### Base URL: `http://dox-tmpl-pdf-recognizer:5003`

### Recognize Template
```http
POST /api/recognize/template
```

**Request Body:**
```json
{
  "document_id": "doc_123456",
  "document_path": "/tmp/document.pdf",
  "options": {
    "max_candidates": 10,
    "confidence_threshold": 0.50
  }
}
```

**Response:**
```json
{
  "success": true,
  "recognition_profile_id": "rp_456789",
  "document_id": "doc_123456",
  "template_matched": {
    "template_id": "tpl_invoice_standard",
    "template_name": "Standard Invoice",
    "confidence_score": 0.87,
    "approval_type": "auto_accepted"
  },
  "field_mappings": {
    "invoice_number": "INV-2025-001",
    "total_amount": "1250.00",
    "vendor_name": "ABC Corporation"
  },
  "processing_time_ms": 2500,
  "timestamp": "2025-11-02T17:00:00Z"
}
```

### Get Recognition Status
```http
GET /api/recognize/status/{recognition_profile_id}
```

### Multi-Agent Collaboration Dashboard
```http
GET /api/collaboration/dashboard/{document_id}
```

---

## Core Services APIs

### Core Store Service
**Base URL:** `http://dox-core-store:5000`

#### Store Document
```http
POST /api/documents
```

#### Get Document
```http
GET /api/documents/{document_id}
```

#### Search Documents
```http
GET /api/documents/search?query=invoice&limit=50
```

### Core Auth Service
**Base URL:** `http://dox-core-auth:5001`

#### Authenticate User
```http
POST /api/auth/login
```

#### Validate Token
```http
POST /api/auth/validate
```

#### Get User Info
```http
GET /api/auth/user/{user_id}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional error details",
    "code": "error_code",
    "timestamp": "2025-11-02T17:00:00Z"
  },
  "request_id": "req_123456"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `413 Payload Too Large`: File too large
- `415 Unsupported Media Type`: Invalid file type
- `419 Suspicious Content`: Virus detected
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: Service unavailable
- `503 Service Unavailable**: Service temporarily unavailable

---

## Rate Limiting

### Rate Limits by Service
- **dox-tmpl-pdf-upload**: 100 uploads per user per day
- **dox-tmpl-pdf-recognizer**: 500 recognitions per user per day
- **dox-validation-service**: 1000 validations per user per day
- **dox-workflow-orchestrator**: 1000 workflow starts per user per day

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698912345
```

### Rate Limit Exceeded Response
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "details": {
    "limit": 100,
    "window": "24 hours",
    "reset_time": "2025-11-03T17:00:00Z"
  }
}
```

---

## Webhook Events

### Event Format
```json
{
  "event_id": "evt_123456",
  "event_type": "workflow_completed",
  "event_data": {
    "workflow_id": "wf_abc123",
    "status": "success",
    "duration_ms": 5000
  },
  "timestamp": "2025-11-02T17:00:00Z",
  "service": "dox-workflow-orchestrator"
}
```

### Event Types
- `workflow_started`: Workflow execution started
- `workflow_completed`: Workflow completed successfully
- `workflow_failed`: Workflow failed
- `workflow_paused`: Workflow paused
- `workflow_resumed`: Workflow resumed
- `step_completed`: Workflow step completed
- `step_failed`: Workflow step failed
- `team_coordination_started`: Team sync started
- `team_coordination_completed`: Team sync completed
- `memory_bank_updated`: Memory bank updated
- `service_health_changed`: Service health status changed

### Event Subscription
Events are published via Redis pub/sub channels:
- `workflows`: All workflow events
- `workflows:started`: Workflow started events
- `workflows:completed`: Workflow completed events
- `workflows:failed`: Workflow failed events
- `coordination`: Team coordination events
- `memory_banks`: Memory bank update events
- `services`: Service health events

---

## SDK Examples

### Python Client Example
```python
import requests

# Start workflow
response = requests.post(
    "http://dox-workflow-orchestrator:5000/api/v1/workflows",
    json={
        "rule_name": "process_document_upload",
        "context": {
            "document_id": "doc_123",
            "user_id": "user_456"
        }
    },
    headers={"Authorization": "Bearer <jwt_token>"}
)

workflow_id = response.json()["workflow_id"]

# Check workflow status
status = requests.get(
    f"http://dox-workflow-orchestrator:5000/api/v1/workflows/{workflow_id}",
    headers={"Authorization": "Bearer <jwt_token>"}
)
```

### JavaScript Client Example
```javascript
// Upload document with validation
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('user_id', 'user_123');

fetch('http://dox-tmpl-pdf-upload:5002/api/v1/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  },
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Document uploaded:', data.document_id);
});
```

---

## Testing

### Health Check Endpoints
All services provide a `/health` endpoint for monitoring:

```bash
curl http://dox-workflow-orchestrator:5000/health
curl http://dox-validation-service:5007/health
curl http://dox-tmpl-pdf-upload:5002/health
curl http://dox-tmpl-pdf-recognizer:5003/health
```

### Integration Tests
Run the comprehensive integration test suite:

```bash
cd dox-tmpl-pdf-upload
python test_basic_validation.py
```

---

## Version History

- **v1.0.0**: Initial release with complete workflow orchestration and validation
- Last Updated: 2025-11-02

For more information, see the [DOX Platform Documentation](../README.md).
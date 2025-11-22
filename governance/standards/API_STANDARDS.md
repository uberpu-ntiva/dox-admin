# Pact Platform: API STANDARDS

**Standard REST API patterns, security practices, and conventions for all 20 microservices**

**Last Updated**: 2025-10-31
**Owner**: Core Architecture Team
**Status**: Active

---

## Table of Contents

1. [REST Endpoint Patterns](#rest-endpoint-patterns)
2. [Request/Response Format](#requestresponse-format)
3. [Authentication & Authorization](#authentication--authorization)
4. [Error Handling](#error-handling)
5. [Pagination, Filtering, Sorting](#pagination-filtering-sorting)
6. [Rate Limiting](#rate-limiting)
7. [Versioning](#versioning)
8. [Status Codes](#status-codes)
9. [CORS](#cors)
10. [Security](#security)

---

## REST Endpoint Patterns

### Resource-Oriented Design

All endpoints follow RESTful resource-oriented patterns:

```
/api/v1/[resource]              # List/Create
/api/v1/[resource]/{id}         # Get/Update/Delete
/api/v1/[resource]/{id}/[sub]   # Sub-resources
```

### Endpoint Examples

```
POST   /api/v1/templates                  # Create template
GET    /api/v1/templates                  # List templates
GET    /api/v1/templates/{id}             # Get template
PUT    /api/v1/templates/{id}             # Update template
DELETE /api/v1/templates/{id}             # Delete template
POST   /api/v1/templates/{id}/fields      # Add field to template
GET    /api/v1/templates/{id}/fields      # List template fields
```

### HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|-----------|------|
| GET | Retrieve resource | ✓ | ✓ |
| POST | Create resource | ✗ | ✗ |
| PUT | Replace resource (full) | ✓ | ✗ |
| PATCH | Partial update | ✗ | ✗ |
| DELETE | Delete resource | ✓ | ✗ |
| HEAD | Like GET, no body | ✓ | ✓ |
| OPTIONS | Describe communication options | ✓ | ✓ |

### URI Design Rules

✅ **Do**:
- Use lowercase: `/api/templates` not `/api/Templates`
- Use hyphens for multi-word resources: `/api/template-fields` not `/api/templateFields`
- Use meaningful names: `/api/templates/{id}/fields` not `/api/temp/flds`
- Use query params for filtering: `/api/templates?status=active`
- Use path params for IDs: `/api/templates/{id}`

❌ **Don't**:
- Use query strings for state-changing operations (use POST/PUT/DELETE)
- Mix verb and noun in endpoints (use nouns only)
- Use file extensions in URIs (`.json`, `.xml`)
- Use trailing slashes: `/api/templates/` (not `/api/templates/`)

---

## Request/Response Format

### Request Format

```http
POST /api/v1/templates
Content-Type: application/json
Authorization: Bearer {jwt-token}

{
  "name": "Invoice Template",
  "description": "Standard invoice template",
  "fields": [
    {
      "name": "invoice_number",
      "type": "text",
      "required": true
    }
  ]
}
```

### Success Response Format

**200 OK (Get/Update):**
```json
{
  "status": "success",
  "data": {
    "id": "template-123",
    "name": "Invoice Template",
    "created_at": "2025-10-31T12:00:00Z",
    "updated_at": "2025-10-31T12:00:00Z"
  }
}
```

**201 Created (Post):**
```json
{
  "status": "success",
  "data": {
    "id": "template-123",
    "name": "Invoice Template",
    "created_at": "2025-10-31T12:00:00Z"
  }
}
```

**204 No Content (Delete):**
```
(Empty body)
```

### List Response Format

```json
{
  "status": "success",
  "data": [
    { "id": "1", "name": "Template 1" },
    { "id": "2", "name": "Template 2" }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### Request/Response Headers

**Required Request Headers**:
- `Content-Type: application/json` (for POST/PUT/PATCH)
- `Authorization: Bearer {jwt-token}` (for protected endpoints)

**Response Headers**:
- `Content-Type: application/json`
- `X-Request-ID: {uuid}` (for tracing)
- `X-API-Version: v1` (API version)
- `X-RateLimit-Limit: 100` (rate limit)
- `X-RateLimit-Remaining: 95` (remaining requests)
- `X-RateLimit-Reset: 1630000000` (unix timestamp)

---

## Authentication & Authorization

### JWT Token Format

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "user-id-123",
  "email": "user@example.com",
  "roles": ["admin", "signer"],
  "site_id": "site-456",
  "exp": 1630000000,
  "iat": 1629900000
}
```

**Token Expiry**: 15 minutes (access token), 7 days (refresh token)

### Bearer Token Usage

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### RBAC (Role-Based Access Control)

**Roles**:
- `admin` - Full platform access
- `signer` - Can sign documents
- `manager` - Can manage templates and batches
- `viewer` - Read-only access
- `api-client` - Machine-to-machine access

**Permissions**:
```json
{
  "admin": ["read:*", "write:*", "delete:*"],
  "manager": ["read:templates", "write:templates", "read:batches", "write:batches"],
  "signer": ["read:documents", "write:signatures"],
  "viewer": ["read:*"]
}
```

### Protected Endpoint Pattern

All endpoints (except auth endpoints) require JWT token:

```python
@app.route('/api/v1/templates', methods=['GET'])
@require_auth  # Middleware decorator
def list_templates():
    # Endpoint implementation
    pass
```

### Multi-Tenancy

All endpoints enforce multi-tenancy via `site_id` from JWT:

```python
@app.route('/api/v1/templates/{id}', methods=['GET'])
@require_auth
def get_template(id):
    template = Template.query.filter(
        Template.id == id,
        Template.site_id == current_user.site_id  # Enforce site isolation
    ).first()
    if not template:
        return {"error": "NOT_FOUND"}, 404
    return template
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "name": "Name is required",
      "email": "Invalid email format"
    }
  },
  "request_id": "req-uuid-12345",
  "timestamp": "2025-10-31T12:00:00Z"
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `INVALID_JSON` | 400 | Malformed JSON in request body |
| `MISSING_FIELD` | 400 | Required field missing |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token |
| `EXPIRED_TOKEN` | 401 | JWT token has expired |
| `INVALID_TOKEN` | 401 | JWT token is invalid or tampered |
| `FORBIDDEN` | 403 | User lacks required permissions/roles |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists or state conflict |
| `UNPROCESSABLE_ENTITY` | 422 | Request valid but cannot be processed |
| `RATE_LIMITED` | 429 | Too many requests (rate limit exceeded) |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Validation Error Example

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Validation failed",
    "details": {
      "name": "Name must be 1-255 characters",
      "email": "Email format invalid",
      "phone": "Phone number must be 10-15 digits"
    }
  }
}
```

### Business Logic Error Example

```json
{
  "status": "error",
  "error": {
    "code": "CONFLICT",
    "message": "Email already registered",
    "details": {
      "email": "user@example.com",
      "existing_user_id": "user-456"
    }
  }
}
```

---

## Pagination, Filtering, Sorting

### Pagination

Query parameters:
- `page` (integer, default 1) - Page number
- `limit` (integer, default 20, max 100) - Items per page

```
GET /api/v1/templates?page=2&limit=50
```

Response includes:
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 250,
    "pages": 5,
    "has_next": true,
    "has_prev": true
  }
}
```

### Filtering

Query parameters for filtering:
```
GET /api/v1/templates?status=active&type=invoice
GET /api/v1/templates?created_at:gte=2025-01-01
```

**Filter Operators**:
- `:eq` - Equals (default)
- `:ne` - Not equals
- `:gt` - Greater than
- `:gte` - Greater than or equal
- `:lt` - Less than
- `:lte` - Less than or equal
- `:in` - In list
- `:contains` - String contains
- `:startswith` - Starts with

### Sorting

Query parameter `sort`:
```
GET /api/v1/templates?sort=name:asc
GET /api/v1/templates?sort=created_at:desc
GET /api/v1/templates?sort=name:asc,created_at:desc
```

**Sort Order**:
- `:asc` - Ascending (default)
- `:desc` - Descending

---

## Rate Limiting

### Rate Limit Headers

All responses include rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1630000000
```

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Most endpoints | 100/minute per user |
| Authentication | 10/minute per IP |
| Upload | 20/minute per user |
| Batch operations | 5/minute per user |

### Rate Limit Exceeded Response

```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests",
    "retry_after": 60
  },
  "headers": {
    "X-RateLimit-Limit": 100,
    "X-RateLimit-Remaining": 0,
    "X-RateLimit-Reset": 1630000060
  }
}
```

HTTP Status: **429 Too Many Requests**

---

## Versioning

### API Version Header

All endpoints support versioning via URL path:
```
/api/v1/templates      # Version 1
/api/v2/templates      # Version 2
```

**Current Version**: v1

**Version Introduction Timeline**:
- v1: Initial release (2025-10-31)
- v2: TBD (future breaking changes)

### Breaking Changes

Breaking changes require new version. Non-breaking changes (additions) don't:

**Breaking Changes**:
- Removing an endpoint
- Changing response structure
- Changing parameter meaning
- Changing error codes

**Non-Breaking Changes**:
- Adding optional response fields
- Adding new endpoints
- Adding optional query parameters
- Adding new error codes

---

## Status Codes

### Success Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET/PUT request |
| 201 | Created | Successful POST creating resource |
| 202 | Accepted | Async operation accepted (long-running) |
| 204 | No Content | Successful DELETE or empty response |

### Redirect Codes

| Code | Meaning |
|------|---------|
| 301 | Moved Permanently |
| 302 | Found (temporary redirect) |
| 304 | Not Modified |

### Client Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |

### Server Error Codes

| Code | Meaning |
|------|---------|
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

---

## CORS

### CORS Headers

For services with browser-based frontends:

```
Access-Control-Allow-Origin: https://pact-platform.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
```

### CORS Policy

- Allowed Origins: `https://pact-platform.com` (production), `http://localhost:*` (development)
- Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed Headers: Content-Type, Authorization, X-Request-ID
- Credentials: Allowed (cookies, auth headers)
- Max Age: 3600 seconds

---

## Security

### Input Validation

**ALL inputs must be validated**:

```python
# Validate types
if not isinstance(request.json.get('name'), str):
    return {"error": "Name must be string"}, 400

# Validate length
if len(request.json.get('name')) > 255:
    return {"error": "Name must be <255 chars"}, 400

# Validate format
if not re.match(r'^[a-zA-Z0-9_-]+$', resource_id):
    return {"error": "Invalid resource ID format"}, 400
```

### SQL Injection Prevention

**Always use parameterized queries**:

```python
# ✅ GOOD - Parameterized
user = User.query.filter(User.email == email).first()

# ❌ BAD - SQL injection risk
user = db.session.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### XSS Prevention

**Always escape user input in responses**:

```python
# ✅ GOOD - Escaped
response = {
    "name": html.escape(user_input_name)
}

# Store as plain JSON, escape on rendering
```

### CSRF Protection

All state-changing operations require CSRF token (automatic with frameworks like Flask):

```
X-CSRF-Token: {token}
```

### Logging

**NEVER log sensitive data**:

```python
# ✅ GOOD - Don't log passwords
logger.info(f"User login attempt: {email}")

# ❌ BAD - Logs password
logger.info(f"User login: {email}:{password}")

# ✅ GOOD - Mask sensitive fields
logger.info(f"Token: {token[:10]}...{token[-4:]}")
```

### PII Protection

**Encrypt PII at rest, use HTTPS in transit**:

```python
from cryptography.fernet import Fernet

# Encrypt sensitive fields
cipher_suite = Fernet(encryption_key)
encrypted_ssn = cipher_suite.encrypt(ssn.encode())

# Store encrypted value in database
user.ssn = encrypted_ssn
```

---

## References

**Related Standards**:
- `/dox-admin/governance/standards/AUTH_STANDARDS.md` - JWT and RBAC details
- `/dox-admin/governance/standards/TECHNOLOGY_STANDARDS.md` - Tech stack per service
- `/dox-admin/governance/standards/DEPLOYMENT_STANDARDS.md` - Deployment patterns

**External References**:
- [REST API Best Practices](https://restfulapi.net/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JSON API Specification](https://jsonapi.org/)

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-10-31
**Version**: 1.0


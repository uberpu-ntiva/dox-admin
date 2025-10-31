# [SERVICE-NAME] API Documentation

**Base URL**: `http://localhost:5000` (development) | `https://[service-name].azurewebsites.net` (production)

**Authentication**: JWT Bearer token (see dox-core-auth service)

**Content-Type**: `application/json`

---

## Authentication

All endpoints require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer [JWT-TOKEN]
```

Get a token from the dox-core-auth service:
```bash
POST /auth/token
Body: { "username": "...", "password": "..." }
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error code",
  "message": "Human-readable error message",
  "status": 400,
  "timestamp": "2025-10-31T12:00:00Z",
  "details": {}
}
```

### Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | User lacks required permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Endpoints

### [RESOURCE] - [Plural Resource Name]

#### GET /api/[resources]

List all resources with pagination and filtering.

**Parameters**:
- `page` (query, integer) - Page number (default: 1)
- `limit` (query, integer) - Items per page (default: 20)
- `sort` (query, string) - Sort by field (format: `field` or `field:asc|desc`)
- `filter` (query, string) - Filter by criteria (format: `field:value`)

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "resource-123",
      "name": "Example Resource",
      "created_at": "2025-10-31T12:00:00Z",
      "updated_at": "2025-10-31T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

**Example**:
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5000/api/resources?page=1&limit=20&sort=name:asc"
```

---

#### GET /api/[resources]/{id}

Get a single resource by ID.

**Parameters**:
- `id` (path, string, required) - Resource ID

**Response** (200 OK):
```json
{
  "data": {
    "id": "resource-123",
    "name": "Example Resource",
    "description": "Resource description",
    "created_at": "2025-10-31T12:00:00Z",
    "updated_at": "2025-10-31T12:00:00Z"
  }
}
```

**Error** (404 Not Found):
```json
{
  "error": "NOT_FOUND",
  "message": "Resource not found",
  "status": 404
}
```

**Example**:
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5000/api/resources/resource-123"
```

---

#### POST /api/[resources]

Create a new resource.

**Body**:
```json
{
  "name": "New Resource",
  "description": "Resource description",
  "type": "default"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "resource-new",
    "name": "New Resource",
    "description": "Resource description",
    "type": "default",
    "created_at": "2025-10-31T12:00:00Z"
  }
}
```

**Validation Errors** (400 Bad Request):
```json
{
  "error": "INVALID_REQUEST",
  "message": "Validation failed",
  "status": 400,
  "details": {
    "name": "Name is required",
    "type": "Invalid type value"
  }
}
```

**Example**:
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Resource"}' \
  "http://localhost:5000/api/resources"
```

---

#### PUT /api/[resources]/{id}

Update an existing resource.

**Parameters**:
- `id` (path, string, required) - Resource ID

**Body**:
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "resource-123",
    "name": "Updated Name",
    "description": "Updated description",
    "updated_at": "2025-10-31T12:00:00Z"
  }
}
```

**Example**:
```bash
curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Name"}' \
  "http://localhost:5000/api/resources/resource-123"
```

---

#### DELETE /api/[resources]/{id}

Delete a resource.

**Parameters**:
- `id` (path, string, required) - Resource ID

**Response** (204 No Content):
```
(Empty response)
```

**Example**:
```bash
curl -X DELETE -H "Authorization: Bearer TOKEN" \
  "http://localhost:5000/api/resources/resource-123"
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Request successful, no response body |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 500 | Server Error - Internal server error |
| 503 | Service Unavailable - Service temporarily down |

---

## Rate Limiting

All endpoints are rate-limited:
- **Rate**: 100 requests per minute per user
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

When rate limited, you'll receive a 429 response:
```json
{
  "error": "RATE_LIMITED",
  "message": "Too many requests. Try again later.",
  "status": 429,
  "retry_after": 60
}
```

---

## Pagination

List endpoints support pagination:

```json
{
  "data": [...],
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

---

## Filtering & Sorting

### Sorting

Use the `sort` parameter:
```
GET /api/resources?sort=name:asc
GET /api/resources?sort=created_at:desc
```

### Filtering

Use the `filter` parameter:
```
GET /api/resources?filter=status:active
GET /api/resources?filter=type:template&filter=status:active
```

---

## Webhooks

[REPLACE_ME: If your service sends webhooks, document them here]

### Webhook Events

**Example**: `resource.created`, `resource.updated`, `resource.deleted`

**Payload**:
```json
{
  "event": "resource.created",
  "timestamp": "2025-10-31T12:00:00Z",
  "data": { ... }
}
```

---

## Changelog

### v1.0.0 (2025-10-31)
- Initial API release
- [REPLACE_ME: List changes]

---

**For detailed technical specification**, see `openapi.yaml`.


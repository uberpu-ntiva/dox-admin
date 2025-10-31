# Pact Platform: TECHNOLOGY STANDARDS

**Locked Technology Stack per Service Type**

**Last Updated**: 2025-10-31
**Owner**: Core Architecture Team
**Status**: FROZEN (No deviations without executive approval)

---

## TECHNOLOGY LOCK - Executive Summary

**These technology decisions are LOCKED and cannot be changed without documented justification and executive approval.**

**Why Lock Technology**:
- Consistency across all 20 services
- Team knowledge transfer efficiency
- Vendor lock-in prevention
- Cost optimization
- Security uniformity
- Operational simplicity

---

## BACKEND SERVICES (Python Flask Stack)

### MANDATORY Stack

| Component | Technology | Version | Locked |
|-----------|-----------|---------|--------|
| **Runtime** | Python | 3.10+ | ✅ YES |
| **Framework** | Flask | 2.0+ | ✅ YES |
| **Database** | MSSQL/PostgreSQL | 2019+ / 14+ | ✅ YES |
| **ORM** | SQLAlchemy | 1.4+ | ✅ YES |
| **API Docs** | OpenAPI 3.0 | Swagger/Redoc | ✅ YES |
| **Testing** | pytest | 7.0+ | ✅ YES |
| **Package Mgr** | pip | Latest | ✅ YES |
| **Linting** | flake8 | Latest | ✅ YES |
| **Formatting** | black | Latest | ✅ YES |
| **Auth** | PyJWT | 2.0+ | ✅ YES |
| **Containerization** | Docker | 20.10+ | ✅ YES |

### APPROVED Libraries (By Service Type)

**Data Processing**:
- SQLAlchemy (ORM) - ✅ Approved
- psycopg2 (PostgreSQL driver) - ✅ Approved
- python-dotenv (config) - ✅ Approved

**PDF Processing** (Services: recognizer, upload, rtns-barcode-matcher):
- pdftk-java - ✅ Approved (CLI tool)
- poppler-utils - ✅ Approved (CLI tool)
- ghostscript - ✅ Approved (CLI tool)
- pdfplumber - ✅ Approved
- fuzzywuzzy - ✅ Approved (text similarity)
- python-Levenshtein - ✅ Approved (optimization for fuzzywuzzy)

**Image Processing** (Services: rtns-barcode-matcher, field-mapper):
- OpenCV - ✅ Approved
- Pillow (PIL) - ✅ Approved
- pyzbar - ✅ Approved (barcode detection)
- pytesseract - ✅ Approved (OCR)

**File Upload** (All services with upload):
- werkzeug - ✅ Approved (file handling)
- python-magic - ✅ Approved (MIME type detection)
- ClamAV (pyclamd) - ✅ Approved (virus scanning)

**DateTime & Scheduling**:
- pytz - ✅ Approved
- APScheduler - ✅ Approved (job scheduling)

**External Services**:
- requests - ✅ Approved (HTTP client)
- httpx - ✅ Approved (HTTP client, async-capable)
- azure-identity - ✅ Approved (Azure auth)
- azure-storage-blob - ✅ Approved (Azure Files)
- microsoft-graph-python - ✅ Approved (SharePoint/Graph API)

**Logging & Monitoring**:
- python-json-logger - ✅ Approved
- structlog - ✅ Approved

### PROHIBITED Technologies

❌ **These are explicitly prohibited**:
- Django, FastAPI, Pyramid (use Flask only)
- SQLAlchemy alternatives (use SQLAlchemy only)
- Complex PDF libraries (stick to pdftk, poppler, ghostscript)
- MongoDb, Redis-cache, NoSQL (use MSSQL/PostgreSQL)
- Celery, RQ (use APScheduler for job scheduling)
- GraphQL (use REST only)
- MicroServices frameworks (use Flask + Docker only)
- Custom PDF tools (use standardized tools only)

---

## FRONTEND SERVICES (Vanilla JavaScript)

### MANDATORY Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Runtime** | Browser JS | ES6+ | ✅ NO frameworks |
| **HTML** | Vanilla HTML5 | 5+ | ✅ Static, no JSX |
| **CSS** | Vanilla CSS3 | 3+ | ✅ Custom, no Tailwind/Bootstrap |
| **Testing** | Playwright | 1.20+ | ✅ E2E only |
| **Build** | None (static) | - | ✅ No webpack, parcel, etc. |
| **Package Mgr** | npm | Latest | ✅ Only for Playwright |
| **Containerization** | Docker | 20.10+ | ✅ With Node.js base |

### APPROVED Libraries (Strict Minimum)

**Important**: Frontend keeps strict library minimalism for performance and maintainability.

- **Fetch API** - ✅ Use for HTTP requests (built-in)
- **DOM API** - ✅ Use for DOM manipulation (built-in)

**If really needed** (rare):
- Playwright - ✅ Testing only (not in production code)
- npm - ✅ Package management only (not for frameworks)

### PROHIBITED Technologies

❌ **These are explicitly prohibited in frontend**:
- React, Vue, Angular, Svelte (use vanilla only)
- Bootstrap, Tailwind CSS (use vanilla CSS only)
- webpack, Parcel, esbuild (no build system)
- TypeScript (use vanilla JavaScript only)
- JSX, template languages (use HTML only)
- Node.js frameworks (use static HTML only)
- CSS preprocessors (SASS, LESS - use CSS only)
- npm packages for UI (no jquery, materialize, etc.)

### Style Guidelines

```javascript
// ✅ GOOD - Vanilla ES6+ JavaScript
class TemplateManager {
  constructor() {
    this.templates = [];
    this.init();
  }

  async init() {
    document.addEventListener('DOMContentLoaded', () => {
      this.loadTemplates();
      this.attachEventListeners();
    });
  }

  async loadTemplates() {
    const response = await fetch('/api/templates', {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    this.templates = await response.json();
    this.render();
  }

  attachEventListeners() {
    document.getElementById('uploadBtn').addEventListener('click',
      () => this.handleUpload());
  }

  render() {
    const html = this.templates.map(t =>
      `<div class="template">${t.name}</div>`
    ).join('');
    document.getElementById('list').innerHTML = html;
  }
}

// Initialize
new TemplateManager();
```

```css
/* ✅ GOOD - Vanilla CSS3 */
.template {
  padding: 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin: 8px 0;
}

.template:hover {
  background: #efefef;
  cursor: pointer;
}

@media (max-width: 768px) {
  .template {
    padding: 12px;
  }
}
```

---

## DATABASE SERVICES (MSSQL + PostgreSQL)

### MANDATORY Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Primary** | MSSQL | 2019 Enterprise/Standard |
| **Alternative** | PostgreSQL | 14+ |
| **ORM** | SQLAlchemy | 1.4+ |
| **Migrations** | Alembic | Latest |
| **Connection Pool** | SQLAlchemy pool | Built-in |

### MSSQL Configuration

**Multi-Tenancy Schema**:
- ALL tables have `site_id` column (non-nullable, indexed)
- ALL queries filter by `site_id` (prevent cross-tenant leaks)
- Composite primary keys: `(site_id, id)`
- Foreign keys enforce same-site relationships

**Stored Procedures** (dox-core-store service):
- Complex business logic goes in stored procedures
- Keep data transformations in application layer
- Use MSSQL native functions for performance

**Indexes**:
- Index all `site_id` columns
- Index all foreign keys
- Index frequently-queried columns (status, type, created_at)
- Use composite indexes for common filters

---

## DEPLOYMENT & INFRASTRUCTURE

### Containerization: MANDATORY Docker

**Dockerfile Requirements**:
- Multi-stage builds for optimization
- Alpine or slim base images (small size)
- Non-root user execution (security)
- Health check endpoint
- .dockerignore file

### Container Registry

- **Primary**: Azure Container Registry (ACR)
- **Alternative**: AWS ECR
- Both services supported

### Orchestration

- **Primary**: Azure Container Instances or App Service
- **Alternative**: AWS ECS Fargate
- Kubernetes NOT approved (too complex for this team size)

### Task Automation: MANDATORY Makefile

Every service must have `Makefile` with:
- `make install` - Install dependencies
- `make test` - Run all tests
- `make build` - Build Docker image
- `make run` - Run locally
- `make docker-up` - Docker compose start
- `make clean` - Clean up

---

## AUTHENTICATION & AUTHORIZATION: MANDATORY Azure B2C

### Azure B2C Configuration

- **Provider**: Azure B2C
- **Token Type**: JWT (RS256 signing)
- **Token Life**: 15 minutes (access), 7 days (refresh)
- **RBAC**: Custom roles in application layer

### JWT Claims (Required)

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

---

## TESTING: MANDATORY pytest + Playwright

### Backend Testing

**Unit Tests** (pytest):
- Test individual functions and methods
- Mock external dependencies
- Target: 80%+ coverage

**Integration Tests** (pytest):
- Test components working together
- Use test database
- Test with actual dependencies

### Frontend Testing

**E2E Tests** (Playwright):
- Test user workflows
- Test in real browser
- Use test environment
- Run before merge

---

## DEVELOPMENT TOOLS: LOCKED

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Runtime |
| Git | 2.30+ | Version control |
| Docker | 20.10+ | Containerization |
| Docker Compose | 1.29+ | Local dev |
| Make | 4.0+ | Task automation |
| curl/Postman | Latest | API testing |
| flake8 | Latest | Linting |
| black | Latest | Formatting |
| pytest | 7.0+ | Testing |
| Playwright | 1.20+ | E2E testing |

---

## ARCHITECTURE PATTERNS: LOCKED

### Monolithic Per Service

Each service is a **monolith** (not microservices within services):
- Single codebase per service
- Single database per service
- Service-to-service via REST APIs
- NO internal microservices

### Stateless Services

- All services are stateless (except databases)
- State stored in database or external cache
- Enables horizontal scaling
- Enables stateless deployment

### API-First Design

- Service contracts defined in OpenAPI
- Generate docs and stubs
- No shared database access
- All communication via REST APIs

---

## APPROVED CLOUD SERVICES

### Azure Services (Primary)

- ✅ Azure Container Instances
- ✅ Azure App Service
- ✅ Azure MSSQL Database
- ✅ Azure PostgreSQL Database
- ✅ Azure Files (file storage)
- ✅ Azure B2C (authentication)
- ✅ Azure Key Vault (secrets management)
- ✅ Application Insights (monitoring)

### AWS Services (Alternative)

- ✅ ECS Fargate (container orchestration)
- ✅ RDS MSSQL/PostgreSQL (database)
- ✅ S3 (file storage)
- ✅ Cognito (authentication, if B2C not available)
- ✅ Secrets Manager (secrets)
- ✅ CloudWatch (monitoring)

---

## DEVIATIONS & EXCEPTIONS

**Process for Technology Deviations**:

1. Document business justification (why locked tech won't work)
2. Research alternatives (compare at least 3 options)
3. Submit deviation request to Architecture Team
4. Approval required before implementation
5. Document decision in this file
6. Notify all team leads

**Approved Deviations**: None yet (open for submission)

---

## WHY THESE CHOICES?

**Python + Flask**:
- Simple, readable, maintainable
- Excellent data science ecosystem (pandas, numpy, scikit-learn)
- PDF tools have strong Python bindings
- Team expertise

**Vanilla JavaScript**:
- No framework bloat or overhead
- Direct DOM manipulation
- Better performance
- Easier debugging
- Smaller bundle size

**MSSQL + PostgreSQL**:
- Enterprise-grade reliability
- Strong ACID compliance
- Excellent multi-tenancy support
- Team expertise

**Azure B2C + JWT**:
- Enterprise SSO support
- Strong OAuth2/OpenID Connect compliance
- Secure token handling
- Team expertise

**Docker + Azure/AWS**:
- Industry standard containerization
- Vendor flexibility (Azure OR AWS)
- Strong container ecosystem
- Cost-effective

---

## REFERENCES

**See Also**:
- `/dox-admin/strategy/standards/API_STANDARDS.md` - API patterns
- `/dox-admin/strategy/standards/DEPLOYMENT_STANDARDS.md` - Deployment patterns
- `/dox-admin/strategy/SERVICE_TEMPLATE/` - Template repository

---

**Status**: ✅ FROZEN (No changes without approval)
**Last Updated**: 2025-10-31
**Version**: 1.0


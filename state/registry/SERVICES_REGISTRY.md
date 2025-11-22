# PACT PLATFORM: COMPLETE SERVICES REGISTRY

**Master Catalog of All 20 Microservices**
**Last Updated**: 2025-10-31
**Owner**: Supervisor Agent
**Purpose**: Single source of truth for service status, dependencies, team assignments, and timeline

---

## QUICK REFERENCE: SERVICE STATUS MATRIX

| # | Service Name | Status | Phase | Team | Timeline | Type | GitHub Repo |
|---|---|---|---|---|---|---|---|
| **1** | dox-tmpl-pdf-recognizer | ✅ Active (v1.0.0) | 1 | N/A | Current | Document | dox-tmpl-pdf-recognizer |
| **2** | dox-tmpl-pdf-upload | ✅ Active (v1.0.0) | 1 | N/A | Current | Document | dox-tmpl-pdf-upload |
| **3** | dox-admin | ✅ Active | 1 | N/A | Current | Admin | dox-admin |
| **4** | dox-core-store | ⏳ In Progress | 2 | Infrastructure | W5-7 | Core | [New] |
| **5** | dox-core-auth | ⏳ In Progress | 2 | Infrastructure | W6-8 | Core | [New] |
| **6** | dox-tmpl-service | 🔜 Planned | 2 | Document | W8-12 | Document | [New] |
| **7** | dox-tmpl-field-mapper | 🔜 Planned | 2 | Document | W8-12 | Document | [New] |
| **8** | dox-gtwy-main | 🔜 Planned | 3 | Frontend | W22-32 | Gateway | [New] |
| **9** | dox-esig-service | 🔜 Planned | 3 | Signing | W13-18 | Business | [New] |
| **10** | dox-esig-webhook-listener | 🔜 Planned | 3 | Signing | W13-18 | Business | [New] |
| **11** | dox-rtns-manual-upload | ⏳ To Port | 3 | Signing | W14-18 | Business | dox-pact-manual-upload |
| **12** | dox-rtns-barcode-matcher | 🔜 Planned | 3 | Signing | W14-18 | Business | [New] |
| **13** | dox-actv-service | 🔜 Planned | 3 | Activation | W16-20 | Business | [New] |
| **14** | dox-actv-listener | 🔜 Planned | 3 | Activation | W16-20 | Business | [New] |
| **15** | dox-data-etl-service | 🔜 Planned | 3 | Data | W18-24 | Business | [New] |
| **16** | dox-data-distrib-service | 🔜 Planned | 3 | Data | W18-24 | Business | [New] |
| **17** | dox-data-aggregation-service | 🔜 Planned | 3 | Data | W18-24 | Business | [New] |
| **18** | dox-auto-workflow-engine | 🔜 Planned | 3 | Automation | W20-26 | Business | [New] |
| **19** | dox-auto-lifecycle-service | 🔜 Planned | 3 | Automation | W20-26 | Business | [New] |
| **20** | dox-core-rec-engine | 🔜 Future | 4 | Reserved | W27+ | Core | [Future] |

**Legend:**
- ✅ = Active/Complete
- ⏳ = In Progress / To Port
- 🔜 = Planned (Not Started)
- Phases: 1=Foundation, 2=Infrastructure, 3=Business, 4=Phase 4+

---

## DEPENDENCY GRAPH

```
EXTERNAL USERS (Signers, Admin, API Consumers)
        │
        ▼
┌────────────────────────────────────────┐
│   dox-gtwy-main (Gateway App)          │
│   • Dashboards • Templates • Bundles   │
│   • Transactions • Activations         │
└────┬─────────────────────────────────┬─┘
     │                                 │
     ▼                                 ▼
┌──────────────────┐          ┌──────────────────┐
│ dox-core-store   │          │ dox-core-auth    │
│ (MSSQL + SPS)    │          │ (Azure B2C)      │
└──────────────────┘          └──────────────────┘
     ▲                              ▲
     │                              │
┌────┴──────────────────────────────┴──┐
│                                       │
├─ DOCUMENT SERVICES ─────────────────┬─┤
│  • dox-tmpl-service                 │ │
│  • dox-tmpl-field-mapper            │ │
│  • dox-tmpl-pdf-recognizer (v1)    │ │
│  • dox-tmpl-pdf-upload (v1)        │ │
├─────────────────────────────────────┤
│                                       │
├─ SIGNING SERVICES ──────────────────┬─┤
│  • dox-esig-service                 │ │
│  • dox-esig-webhook-listener        │ │
│  • dox-rtns-manual-upload           │ │
│  • dox-rtns-barcode-matcher         │ │
├─────────────────────────────────────┤
│                                       │
├─ ACTIVATION SERVICES ───────────────┬─┤
│  • dox-actv-service                 │ │
│  • dox-actv-listener                │ │
├─────────────────────────────────────┤
│                                       │
├─ DATA SERVICES ─────────────────────┬─┤
│  • dox-data-etl-service             │ │
│  • dox-data-distrib-service         │ │
│  • dox-data-aggregation-service     │ │
├─────────────────────────────────────┤
│                                       │
├─ AUTOMATION SERVICES ───────────────┬─┤
│  • dox-auto-workflow-engine         │ │
│  • dox-auto-lifecycle-service       │ │
└────────────────────────────────────────┘
```

---

## DETAILED SERVICE SPECIFICATIONS

### **GROUP 1: CURRENTLY OPERATIONAL (3 Services)**

---

#### **1. dox-tmpl-pdf-recognizer**

**Status**: ✅ Active (v1.0.0)
**Phase**: 1 (Current)
**Team**: N/A (Legacy)
**Timeline**: Current
**Type**: Document Recognition Service
**GitHub**: `uberpu-ntiva/dox-tmpl-pdf-recognizer`
**Repository Location**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-tmpl-pdf-recognizer/`

**Purpose:**
Core PDF template recognition and matching engine. Compares uploaded PDFs against stored templates using weighted scoring (70% text similarity + 30% form field matching).

**Technology Stack:**
- Backend: Python Flask
- Frontend: Vanilla JavaScript
- PDF Tools: pdftk-java, poppler-utils (pdfinfo), ghostscript
- Testing: pytest + Playwright E2E
- Containerization: Docker

**Key Endpoints:**
- `POST /api/templates` - Upload new PDF template
- `POST /api/recognize` - Upload document for recognition
- `POST /api/declare` - Save match decision and update profiles
- `GET /dashboard` - Multi-agent collaboration dashboard

**Key Files:**
- `app/app.py` - Flask application + routes
- `app/pdf_utils.py` - PDF processing (CLI tool encapsulation)
- `docs/api.md` - Human-readable API documentation
- `docs/openapi.yaml` - Machine-readable API specification
- `docs/agent-protocol/README.md` - Multi-agent collaboration protocol
- `docs/plans/sprint_1.md` - Current sprint plan
- `docs/tasks.md` - Completed tasks + backlog

**Dependencies:**
- None (foundation service)

**Downstream Services:**
- dox-gtwy-main (Gateway will consume templates)
- dox-data-aggregation-service (may consume recognition data)

**Known Issues:**
- ⚠️ Playwright E2E tests timeout on Material Design Lite file inputs (HIGH PRIORITY FIX)

**Success Metrics:**
- ✅ All unit tests passing
- ✅ E2E tests passing (after MDL fix)
- ✅ API documentation complete
- ✅ Docker deployment working

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-tmpl-pdf-recognizer.json`

---

#### **2. dox-tmpl-pdf-upload**

**Status**: ✅ Active (v1.0.0)
**Phase**: 1 (Current)
**Team**: N/A (Legacy)
**Timeline**: Current
**Type**: Template Upload Service
**GitHub**: `uberpu-ntiva/dox-tmpl-pdf-upload`
**Repository Location**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-tmpl-pdf-upload/`

**Purpose:**
Handles PDF template upload workflows. Complements pdf-recognizer by managing template ingestion pipelines and validation.

**Technology Stack:**
- Backend: Python Flask
- Frontend: Vanilla JavaScript
- Testing: pytest
- Containerization: Docker

**Key Endpoints:**
- `POST /api/upload` - Upload template with validation
- `GET /api/templates` - List uploaded templates
- `DELETE /api/templates/{id}` - Remove template

**Documentation Status:**
- ⚠️ README only (no API docs, no architecture docs)
- ⚠️ No OpenAPI specification
- ⚠️ No clear integration points defined

**Dependencies:**
- dox-core-store (will need central storage)
- dox-core-auth (will need auth enforcement)

**Downstream Services:**
- dox-gtwy-main (Gateway will manage templates)
- dox-tmpl-service (will replace this in Phase 2)

**Action Items:**
- [ ] Create `docs/api.md` following API_STANDARDS.md
- [ ] Create `docs/openapi.yaml` (OpenAPI 3.0 spec)
- [ ] Create `docs/ARCHITECTURE.md` explaining design
- [ ] Document integration points with dox-core-store
- [ ] Update README with full service description

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-tmpl-pdf-upload.json`

---

#### **3. dox-admin**

**Status**: ✅ Active
**Phase**: 1 (Current)
**Team**: N/A (Central)
**Timeline**: Current
**Type**: Administrative Hub
**GitHub**: `uberpu-ntiva/dox-admin`
**Repository Location**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-admin/`

**Purpose:**
Central administrative hub and specification repository. Houses all master documentation, service registry, team coordination files, and governance standards.

**Structure:**
- `master/` - Master specification PDFs (5 files)
  - Core API Specification.pdf
  - Database Schema Overview.pdf
  - Pact Full System Specification (v2).pdf
  - Pact Gateway_ Page Specification & Recommendations.pdf
  - Gateway Sitemap.pdf
- `strategy/` - Governance documentation (centralized planning)
  - `service-specs/` - Extracted service specifications (20 files)
  - `team-coordination/` - Team tracking documents (7 files)
  - `memory-banks/` - Multi-agent coordination (JSON)
  - `standards/` - Governance standards (10+ files)
  - `reference/` - Master PDFs copied here

**Key Files:**
- `state/registry/SERVICES_REGISTRY.md` - This document (master service catalog)
- `governance/templates/SERVICE_TEMPLATE/` - Standard folder structure for all 20 services
- `strategy/REPO_MAPPING.md` - Existing repos → Pact services mapping
- `strategy/API_STANDARDS.md` - REST API patterns and security standards
- `strategy/TECHNOLOGY_STANDARDS.md` - Locked technology stack per service
- `strategy/MULTI_AGENT_COORDINATION.md` - Multi-agent collaboration protocol
- `strategy/DEPLOYMENT_STANDARDS.md` - Docker, Azure, AWS patterns

**Dependencies:**
- None (central coordination hub)

**Role in System:**
- Central registry for all 20 services
- Governance standards and patterns
- Multi-agent coordination center
- Master specification reference

**Action Items:**
- [ ] Complete `strategy/` folder structure
- [ ] Create all governance standards documents
- [ ] Extract service specifications from master PDFs
- [ ] Initialize all memory-bank templates
- [ ] Register all 20 services in SERVICES_REGISTRY.md

**Memory Bank:**
- Location: `memory-banks/SUPERVISOR.json` (Master coordination log)

---

### **GROUP 2: PHASE 2 - CORE INFRASTRUCTURE (5 Services)**

---

#### **4. dox-core-store**

**Status**: 🔜 Planned
**Phase**: 2 (Infrastructure)
**Team**: Infrastructure Team (2 agents)
**Timeline**: Weeks 5-7 (Start W5)
**Type**: Core Data Service
**GitHub**: [New Repository]

**Purpose:**
Central database and SharePoint integration. Manages all data storage, multi-tenancy enforcement, schema migrations, and enterprise data management.

**Technology Stack:**
- Backend: Python Flask
- Database: MSSQL (SQL Server 2019+)
- Storage: Azure Files / SharePoint Online (Graph API)
- ORM: SQLAlchemy
- Testing: pytest (unit + integration)

**Key Responsibilities:**
- ✓ MSSQL schema design with multi-tenancy (siteId on all tables)
- ✓ Stored procedures and migrations
- ✓ SharePoint Graph API integration
- ✓ Data access layer (DAL) for all services
- ✓ Connection pooling and performance optimization
- ✓ Backup and disaster recovery

**Key Components:**
- Database schema (all tables, indexes, constraints)
- Stored procedures (complex queries, transactions)
- Entity models (SQLAlchemy ORM)
- Migration system (alembic)
- Graph API client for SharePoint
- Connection management

**API Endpoints:**
- CRUD operations for all core entities
- Bulk operations support
- Transaction support
- Schema introspection

**Dependencies:**
- None (foundation service)

**Downstream Services:**
- dox-core-auth (uses users table)
- dox-tmpl-service (uses templates table)
- All other services (depend on data storage)

**Critical Success Factors:**
- ✓ Multi-tenant isolation enforced at database layer
- ✓ MSSQL performance tuned (indexes, query optimization)
- ✓ SharePoint integration tested with real data
- ✓ All migrations tested and reversible
- ✓ 100% unit test coverage for DAL

**Deliverables:**
- MSSQL schema (normalized, documented)
- Python Flask API with CRUD endpoints
- OpenAPI specification
- Docker container with SQL Server init
- Migration scripts and rollback procedures
- Architecture documentation

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-core-store.json`
- Team: `memory-banks/TEAM_INFRASTRUCTURE.json`

---

#### **5. dox-core-auth**

**Status**: 🔜 Planned
**Phase**: 2 (Infrastructure)
**Team**: Infrastructure Team + Security (2 agents)
**Timeline**: Weeks 6-8 (Start W6)
**Type**: Authentication & Authorization Service
**GitHub**: [New Repository]

**Purpose:**
Central authentication and authorization service. Manages Azure B2C integration, JWT token handling, RBAC enforcement, and user role management.

**Technology Stack:**
- Backend: Python Flask
- Auth Provider: Azure B2C
- JWT: PyJWT library
- RBAC: Custom middleware
- Testing: pytest (unit + integration with B2C)

**Key Responsibilities:**
- ✓ Azure B2C user synchronization
- ✓ JWT token generation and validation
- ✓ Role-based access control (RBAC)
- ✓ Permission enforcement middleware
- ✓ User profile management
- ✓ Multi-tenant user isolation

**Key Components:**
- Azure B2C client SDK
- JWT token generator and validator
- RBAC permission checker
- User profile service
- Role assignment manager
- Auth middleware for all services

**API Endpoints:**
- `POST /auth/login` - B2C login flow
- `POST /auth/token` - Token refresh/validation
- `GET /auth/user` - Current user info
- `POST /auth/roles` - Assign/revoke roles
- `GET /auth/permissions` - List user permissions

**Dependencies:**
- dox-core-store (users and roles tables)
- Azure B2C tenant (external)

**Downstream Services:**
- All services (require authentication)
- dox-gtwy-main (enforces auth on UI)

**Critical Success Factors:**
- ✓ JWT tokens properly signed and validated
- ✓ RBAC roles correctly enforced
- ✓ Multi-tenant isolation enforced
- ✓ Azure B2C integration tested
- ✓ Token expiry and refresh working

**Deliverables:**
- JWT middleware for Flask
- RBAC permission checker
- Azure B2C integration layer
- OpenAPI specification
- Auth documentation
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-core-auth.json`
- Team: `memory-banks/TEAM_INFRASTRUCTURE.json`

---

#### **6. dox-tmpl-service**

**Status**: 🔜 Planned
**Phase**: 2 (Infrastructure)
**Team**: Document Team (2 agents)
**Timeline**: Weeks 8-12 (Start W8)
**Type**: Template Management Service
**GitHub**: [New Repository]

**Purpose:**
Template CRUD and bundle management. Replaces dox-tmpl-pdf-upload with comprehensive template lifecycle management, versioning, and bundling support.

**Technology Stack:**
- Backend: Python Flask
- Database: dox-core-store (via API)
- Auth: dox-core-auth (JWT enforcement)
- Testing: pytest (unit + integration + E2E)

**Key Responsibilities:**
- ✓ Template CRUD operations
- ✓ Bundle management (group templates for campaigns)
- ✓ Template versioning
- ✓ Field definition management
- ✓ Access control per template
- ✓ Template search and filtering

**Key Components:**
- Template repository (CRUD)
- Bundle management
- Version control system
- Field mapper integration
- Search and filtering
- Access control layer

**API Endpoints:**
- `POST /api/templates` - Create template
- `GET /api/templates` - List templates
- `GET /api/templates/{id}` - Get template details
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template
- `POST /api/bundles` - Create bundle
- `GET /api/bundles` - List bundles

**Dependencies:**
- dox-core-store (template storage)
- dox-core-auth (authentication)

**Downstream Services:**
- dox-gtwy-main (consume templates)
- dox-esig-service (use templates for signing)
- dox-data-aggregation-service (template statistics)

**Critical Success Factors:**
- ✓ Template CRUD fully working
- ✓ Bundle grouping and versioning
- ✓ Field mapping integration
- ✓ Access control enforced
- ✓ E2E workflows tested

**Deliverables:**
- Flask API with CRUD endpoints
- Template management logic
- Bundle management system
- OpenAPI specification
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-tmpl-service.json`
- Team: `memory-banks/TEAM_DOCUMENT.json`

---

#### **7. dox-tmpl-field-mapper**

**Status**: 🔜 Planned
**Phase**: 2 (Infrastructure)
**Team**: Document Team (2 agents)
**Timeline**: Weeks 8-12 (Start W8)
**Type**: Field Detection & Mapping Service
**GitHub**: [New Repository]

**Purpose:**
Automatic field detection and mapping from PDF templates. Analyzes PDF structure and auto-detects form fields, enabling field mapping workflows.

**Technology Stack:**
- Backend: Python Flask
- PDF Tools: pdftk-java, poppler-utils, ghostscript
- ML: scikit-learn (optional, for advanced detection)
- Testing: pytest (unit + integration)

**Key Responsibilities:**
- ✓ PDF field detection (form fields, text areas, checkboxes)
- ✓ Field type classification (text, number, date, dropdown, checkbox)
- ✓ Field coordinate mapping
- ✓ Field pattern recognition
- ✓ Auto-mapping suggestions

**Key Components:**
- PDF analyzer
- Field detector
- Field classifier
- Pattern recognition engine
- Mapping suggestion generator
- Field repository

**API Endpoints:**
- `POST /api/analyze` - Analyze PDF for fields
- `GET /api/fields/{templateId}` - Get detected fields
- `POST /api/fields/{templateId}` - Create field mapping
- `PUT /api/fields/{templateId}/{fieldId}` - Update field
- `DELETE /api/fields/{templateId}/{fieldId}` - Delete field

**Dependencies:**
- dox-core-auth (authentication)
- dox-tmpl-service (access templates)

**Downstream Services:**
- dox-gtwy-main (UI for field mapping)
- dox-esig-service (use field mappings for signing)

**Critical Success Factors:**
- ✓ Field detection accuracy >90%
- ✓ Field types correctly classified
- ✓ Coordinates precise
- ✓ Pattern recognition working
- ✓ Integration with template service smooth

**Deliverables:**
- Field detection algorithms
- Flask API
- OpenAPI specification
- Pattern recognition engine
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-tmpl-field-mapper.json`
- Team: `memory-banks/TEAM_DOCUMENT.json`

---

### **GROUP 3: PHASE 3 - BUSINESS SERVICES (11 Services)**

---

#### **8. dox-esig-service**

**Status**: 🔜 Planned
**Phase**: 3 (Business)
**Team**: Signing Team (2 agents)
**Timeline**: Weeks 13-18 (Start W13)
**Type**: E-Signature Service
**GitHub**: [New Repository]

**Purpose:**
E-signature integration with AssureSign. Manages signing workflows, envelope creation, signer management, and signature capture.

**Technology Stack:**
- Backend: Python Flask
- E-Sig Provider: AssureSign API
- Testing: pytest (unit + integration with AssureSign sandbox)

**Key Responsibilities:**
- ✓ AssureSign API integration
- ✓ Envelope/document creation
- ✓ Signer management
- ✓ Signing workflow orchestration
- ✓ Signature capture
- ✓ Document delivery

**API Endpoints:**
- `POST /api/envelopes` - Create signing envelope
- `GET /api/envelopes/{id}` - Get envelope status
- `POST /api/signers` - Add signer to envelope
- `PUT /api/envelopes/{id}/send` - Send for signing
- `GET /api/documents/{id}` - Get signed document

**Dependencies:**
- dox-core-store (envelope storage)
- dox-core-auth (authentication)
- dox-tmpl-service (templates for documents)

**Downstream Services:**
- dox-esig-webhook-listener (receives signing events)
- dox-actv-service (integration with activation workflows)

**Critical Success Factors:**
- ✓ AssureSign integration complete
- ✓ Envelope creation working
- ✓ Signer management functional
- ✓ Signature capture tested
- ✓ Webhook integration ready

**Deliverables:**
- AssureSign API client
- Flask API for envelope management
- OpenAPI specification
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-esig-service.json`
- Team: `memory-banks/TEAM_SIGNING.json`

---

#### **9. dox-esig-webhook-listener**

**Status**: 🔜 Planned
**Phase**: 3 (Business)
**Team**: Signing Team (2 agents)
**Timeline**: Weeks 13-18 (Start W13)
**Type**: Webhook Receiver
**GitHub**: [New Repository]

**Purpose:**
Receives and processes asynchronous events from AssureSign (signing completed, rejected, expired, etc.). Updates document status in real-time.

**Technology Stack:**
- Backend: Python Flask
- Message Queue: Azure Service Bus (or RabbitMQ)
- Testing: pytest

**Key Responsibilities:**
- ✓ AssureSign webhook receiver
- ✓ Event validation and parsing
- ✓ Status update propagation
- ✓ Error handling and retry logic
- ✓ Event audit trail

**Webhook Events:**
- Document signed
- Signer declined
- Envelope expired
- Signature requested
- Document voided

**Dependencies:**
- dox-esig-service (provides envelope IDs)
- dox-core-store (status updates)
- Message queue (async processing)

**Downstream Services:**
- dox-actv-service (receives status updates)
- dox-data-aggregation-service (audit trail)

**Critical Success Factors:**
- ✓ Webhook receiver operational
- ✓ Event parsing accurate
- ✓ Status updates timely
- ✓ Retry logic working
- ✓ No events lost

**Deliverables:**
- Webhook receiver endpoint
- Event processor
- Status update service
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-esig-webhook-listener.json`
- Team: `memory-banks/TEAM_SIGNING.json`

---

#### **10. dox-rtns-manual-upload**

**Status**: ⏳ To Port
**Phase**: 3 (Business)
**Team**: Signing Team (2 agents)
**Timeline**: Weeks 14-18 (Start W14, Port Week 2)
**Type**: Manual Return Upload
**GitHub**: Existing `dox-pact-manual-upload` → Port to `dox-rtns-manual-upload`

**Purpose:**
Frontend form and service for manually uploading scanned returned documents. Handles barcode extraction and initial document intake.

**Current Status:**
- Existing implementation in `dox-pact-manual-upload`
- Needs porting to `dox-rtns-manual-upload` with SERVICE_TEMPLATE structure
- Needs documentation and standardization

**Technology Stack:**
- Backend: Python Flask
- Frontend: Vanilla JavaScript
- Barcode Detection: pyzbar library
- Image Processing: OpenCV
- Testing: pytest + Playwright

**Key Responsibilities:**
- ✓ Manual upload form (vanilla JS)
- ✓ File validation (size, type, format)
- ✓ Barcode extraction from images
- ✓ Document preprocessing
- ✓ Integration with barcode matcher

**API Endpoints:**
- `POST /api/upload` - Upload document with barcode
- `GET /api/uploads/{id}` - Get upload status
- `DELETE /api/uploads/{id}` - Cancel upload

**Dependencies:**
- dox-core-auth (authentication)
- dox-core-store (upload storage)

**Downstream Services:**
- dox-rtns-barcode-matcher (barcode processing)
- dox-actv-service (workflow integration)

**Porting Actions (Week 2):**
- [ ] Analyze existing `dox-pact-manual-upload` repo
- [ ] Copy SERVICE_TEMPLATE structure
- [ ] Update README with Pact context
- [ ] Create docs/api.md and docs/openapi.yaml
- [ ] Create docs/ARCHITECTURE.md
- [ ] Update Dockerfile with all dependencies
- [ ] Register in SERVICES_REGISTRY.md
- [ ] Add to memory-banks/TEAM_SIGNING.json

**Critical Success Factors:**
- ✓ Upload form working
- ✓ Barcode extraction accurate
- ✓ File validation complete
- ✓ Integration with barcode matcher seamless

**Deliverables:**
- Ported service with standard structure
- Upload management system
- Barcode extraction logic
- OpenAPI specification
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-rtns-manual-upload.json`
- Team: `memory-banks/TEAM_SIGNING.json`

---

#### **11. dox-rtns-barcode-matcher**

**Status**: 🔜 Planned
**Phase**: 3 (Business)
**Team**: Signing Team (2 agents)
**Timeline**: Weeks 14-18 (Start W14)
**Type**: Barcode & OCR Processing
**GitHub**: [New Repository]

**Purpose:**
Processes barcodes and OCR from returned documents. Matches barcodes to original shipments and documents, extracting critical data.

**Technology Stack:**
- Backend: Python Flask
- Barcode Detection: OpenCV, pyzbar
- OCR: Tesseract
- Image Processing: PIL/Pillow
- Testing: pytest

**Key Responsibilities:**
- ✓ Barcode detection from images
- ✓ Barcode decoding (UPC, Code128, QR, etc.)
- ✓ OCR text extraction
- ✓ Data matching to original documents
- ✓ Confidence scoring

**API Endpoints:**
- `POST /api/process` - Process document image
- `GET /api/results/{id}` - Get extraction results
- `POST /api/match` - Match to original document

**Dependencies:**
- dox-rtns-manual-upload (receives documents)
- dox-core-store (lookup data)

**Downstream Services:**
- dox-actv-service (pass matched data)
- dox-data-aggregation-service (reporting)

**Critical Success Factors:**
- ✓ Barcode detection >95% accurate
- ✓ OCR text extraction reliable
- ✓ Data matching correct
- ✓ Confidence scoring appropriate

**Deliverables:**
- Barcode detection and decoding engine
- OCR integration (Tesseract)
- Data matching logic
- Flask API
- OpenAPI specification
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-rtns-barcode-matcher.json`
- Team: `memory-banks/TEAM_SIGNING.json`

---

#### **12-14. [Additional Business Services Abbreviated]**

**dox-actv-service** (Weeks 16-20, Activation Team)
- Complex duplex workflow state machine
- Pricing and activation rules engine
- Conditional workflow routing

**dox-actv-listener** (Weeks 16-20, Activation Team)
- Async activation event receiver
- Status propagation

**dox-data-etl-service** (Weeks 18-24, Data Team)
- Purchase data ingestion pipeline
- Distributor data synchronization
- Transformation and loading

**dox-data-distrib-service** (Weeks 18-24, Data Team)
- Distributor relationship management
- Pricing tiers and discounts

**dox-data-aggregation-service** (Weeks 18-24, Data Team)
- Analytics and reporting
- KPI aggregation

**dox-auto-workflow-engine** (Weeks 20-26, Automation Team)
- Visual automation builder UI
- Workflow DSL interpreter
- Automation execution engine

**dox-auto-lifecycle-service** (Weeks 20-26, Automation Team)
- Contract lifecycle management
- Status transitions and notifications

---

### **GROUP 4: GATEWAY APPLICATION (1 Service)**

---

#### **15. dox-gtwy-main**

**Status**: 🔜 Planned
**Phase**: 3 (Business)
**Team**: Frontend Team (2 agents) + Backend glue (1)
**Timeline**: Weeks 22-32 (Start W22)
**Type**: Primary Gateway / Cockpit
**GitHub**: [New Repository]

**Purpose:**
Frontend "cockpit" application consuming all microservices. Provides unified dashboard, document management, field mapping, batch operations, and reporting for end users and administrators.

**Technology Stack:**
- Frontend: Vanilla JavaScript
- Backend: Python Flask (glue logic)
- Real-time: WebSockets (status updates)
- Testing: Playwright E2E
- Deployment: Azure App Service or AWS ECS

**Key Pages (25+):**
1. Dashboard (KPI summary)
2. Document Manager (upload, search, organize)
3. Template Library (manage templates)
4. Field Mapper (visual field mapping)
5. Batch Upload (bulk operations)
6. Signing Dashboard (view signings)
7. Activation Manager (pricing activations)
8. Workflow Builder (visual automation)
9. Reports (analytics and KPIs)
10. User Management (admins)
11-25. Additional pages per specifications

**API Integration:**
- Calls all 19 backend services
- Orchestrates complex workflows
- Handles session management
- Real-time status updates via WebSockets

**Dependencies:**
- ALL backend services (19 services)
- dox-core-auth (user authentication)
- dox-core-store (data access)

**Critical Success Factors:**
- ✓ All 25+ pages functional
- ✓ All backend service integrations working
- ✓ Real-time updates via WebSockets
- ✓ E2E tests passing
- ✓ Performance acceptable (<2s page load)

**Deliverables:**
- 25+ HTML pages (vanilla JS)
- Service integration layer
- WebSocket real-time updates
- Admin interfaces
- User documentation
- Docker container

**Memory Bank:**
- Location: `memory-banks/SERVICE_dox-gtwy-main.json`
- Team: `memory-banks/TEAM_FRONTEND.json`

---

### **GROUP 5: FUTURE SERVICES (1 Service)**

---

#### **16. dox-core-rec-engine**

**Status**: 🔜 Future (Phase 4+)
**Phase**: 4
**Team**: Reserved
**Timeline**: Week 27+ (After Phase 3 complete)
**Type**: Recommendation Engine
**GitHub**: [Future]

**Purpose:**
AI-driven recommendation engine providing intelligent suggestions for document routing, pricing optimization, and workflow automation based on historical patterns and ML models.

**Status:** Not started - reserved for Phase 4.

---

## TEAM ASSIGNMENTS

### **Team Organization**

| Team Name | Members | Repos | Phase | Start Week |
|---|---|---|---|---|
| **Infrastructure** | 2 agents | dox-core-store, dox-core-auth | 1-2 | W1 |
| **Document** | 2 agents | dox-tmpl-service, dox-tmpl-field-mapper | 2 | W3 |
| **Signing** | 2 agents | dox-esig-*, dox-rtns-*, dox-pact-manual-upload (port) | 3 | W3 |
| **Activation** | 2 agents | dox-actv-service, dox-actv-listener | 3 | W4 |
| **Data** | 2 agents | dox-data-* (3 services) | 3 | W4 |
| **Frontend** | 2 agents | dox-gtwy-main | 3 | W5 |
| **Automation** | 1-2 agents | dox-auto-workflow-engine, dox-auto-lifecycle-service | 3 | W6 |
| **Supervisor** | 1 agent | Overall coordination, health monitoring | All | W1 |

**Total**: 15 agents across 7 functional teams + 1 supervisor

---

## MEMORY BANK STRUCTURE

**Location**: `/dox-admin/state/memory-banks/`

**File Structure**:
```
memory-banks/
├── SUPERVISOR.json                         # Master coordination log
├── TEAM_INFRASTRUCTURE.json               # Infrastructure team status
├── TEAM_DOCUMENT.json                     # Document team status
├── TEAM_SIGNING.json                      # Signing team status
├── TEAM_ACTIVATION.json                   # Activation team status
├── TEAM_DATA.json                         # Data team status
├── TEAM_FRONTEND.json                     # Frontend team status
├── TEAM_AUTOMATION.json                   # Automation team status
├── SERVICE_dox-tmpl-pdf-recognizer.json  # Per-service tracking (20 files)
├── SERVICE_dox-tmpl-pdf-upload.json
├── SERVICE_dox-core-store.json
├── ... [18 more SERVICE_*.json files]
├── API_CONTRACTS.json                     # Versioned API specifications
├── BLOCKING_ISSUES.json                   # Cross-team dependencies
├── TEST_REFRESH_LOG.json                  # Rolling test updates
└── DEPLOYMENT_LOG.json                    # Service go-live timeline
```

**JSON Schema - Service File**:
```json
{
  "service_name": "dox-core-store",
  "team": "Infrastructure",
  "status": "planned|in_progress|blocked|complete",
  "current_sprint": 1,
  "start_week": 5,
  "estimated_completion": 7,
  "current_task": "Design MSSQL schema",
  "blockers": [],
  "dependencies": [],
  "test_status": "0% - not started",
  "last_update": "2025-10-31T00:00:00Z",
  "notes": "High priority - blocks all other services"
}
```

**JSON Schema - Team File**:
```json
{
  "team_name": "Infrastructure",
  "agents": ["agent-1", "agent-2"],
  "services": ["dox-core-store", "dox-core-auth"],
  "current_phase": 2,
  "sprint": 1,
  "active_tasks": ["Design schema", "Setup Azure connections"],
  "blocked_by": [],
  "blocking": ["all other teams"],
  "test_pass_rate": "0%",
  "last_sync": "2025-10-31T00:00:00Z"
}
```

---

## HOW TO USE THIS REGISTRY

### **For Individual Agents**

1. **Find Your Service**:
   - Locate your service in the matrix above
   - Find detailed spec section for your service
   - Note dependencies and downstream services

2. **Understand Dependencies**:
   - Read "Dependencies" section
   - Note which services you depend on
   - Coordinate with upstream teams

3. **Check Memory Bank**:
   - Read `memory-banks/SERVICE_[name].json` for current status
   - Read `memory-banks/TEAM_[name].json` for team coordination
   - Check `BLOCKING_ISSUES.json` for blockers

4. **Start Building**:
   - Use SERVICE_TEMPLATE/ as boilerplate
   - Follow API_STANDARDS.md for REST patterns
   - Register your service once created
   - Update memory banks regularly

### **For Supervisor Agent**

1. **Daily Monitoring**:
   - Check all memory-banks JSON files
   - Look for `blocked` status services
   - Check BLOCKING_ISSUES.json for conflicts
   - Alert teams on blockers

2. **Weekly Coordination**:
   - Verify all teams updated memory banks
   - Scan for test failures (TEST_REFRESH_LOG.json)
   - Check deployment status (DEPLOYMENT_LOG.json)
   - Schedule sync meetings for blocked items

3. **Sprint Planning**:
   - Update SERVICES_REGISTRY.md status
   - Assign teams to services
   - Set weekly milestones
   - Alert on missed deadlines

### **For New Teams Onboarding**

1. **Read SERVICES_REGISTRY.md** (this document)
2. **Read SERVICE_TEMPLATE/** documentation
3. **Read TECHNOLOGY_STANDARDS.md** for your service type
4. **Read API_STANDARDS.md** for REST patterns
5. **Create memory bank entry** for your service
6. **Join your team's coordination file**
7. **Start building** using SERVICE_TEMPLATE

---

## SUCCESS METRICS

### **Phase 1 Complete (Week 4)**
- [ ] SERVICES_REGISTRY.md populated (all 20 services cataloged)
- [ ] SERVICE_TEMPLATE/ ready for 17 new services
- [ ] REPO_MAPPING.md complete (existing repos mapped)
- [ ] All governance standards documented
- [ ] Memory-banks initialized
- [ ] Teams onboarded (15 agents)

### **Phase 2 Complete (Week 16)**
- [ ] dox-core-store production-ready
- [ ] dox-core-auth production-ready
- [ ] dox-tmpl-service production-ready
- [ ] dox-tmpl-field-mapper production-ready
- [ ] All downstream services unblocked
- [ ] Memory-banks actively updated
- [ ] Zero critical blockers

### **Phase 3 Complete (Week 32)**
- [ ] All 20 services operational
- [ ] Full integration tests passing
- [ ] dox-gtwy-main complete (25+ pages)
- [ ] Multi-tenant platform operational
- [ ] Memory-banks audit trail complete

---

## REFERENCES

**Planning Document**: `/workspace/cmhfcgyd7045kojiqg150pqth/planning.md`

**Master PDFs**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-admin/governance/reference/`

**Service Template**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-admin/governance/templates/SERVICE_TEMPLATE/`

**Standards**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-admin/governance/standards/`

---

**Registry Status**: ✅ ACTIVE & MAINTAINED
**Last Updated**: 2025-10-31
**Owner**: Supervisor Agent
**Next Review**: Weekly

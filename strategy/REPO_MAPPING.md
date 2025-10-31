# PACT PLATFORM: REPOSITORY MAPPING

**Maps existing GitHub repositories to Pact Platform services**

**Last Updated**: 2025-10-31
**Owner**: Core Team
**Purpose**: Track which existing repos map to which Pact services

---

## Existing Repositories → Pact Services Mapping

| GitHub Repo | Maps To | Service Type | Status | Porting Start | Notes |
|---|---|---|---|---|---|
| `dox-tmpl-pdf-recognizer` | dox-tmpl-pdf-recognizer | Document | ✅ In Workspace | N/A | Already integrated (v1.0.0) |
| `dox-tmpl-pdf-upload` | dox-tmpl-pdf-upload | Document | ✅ In Workspace | N/A | Already integrated (minimal docs) |
| `dox-admin` | dox-admin | Admin Hub | ✅ In Workspace | N/A | Central coordination repo |
| `dox-pact-manual-upload` | dox-rtns-manual-upload | Business (Return) | ⏳ To Port | W2 | Manual upload + barcode extraction |
| [Others?] | [Others?] | [Type?] | ⏳ Pending | [When?] | User to clarify |

---

## Currently Operational (3 Repos)

All three repos are already in the workspace and operational.

### ✅ dox-tmpl-pdf-recognizer

**Location**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-tmpl-pdf-recognizer/`

**Pact Service**: dox-tmpl-pdf-recognizer (Document Recognition)

**Status**: Operational (v1.0.0)

**Technology**: Python Flask, vanilla JavaScript, pdftk-java, poppler-utils, ghostscript

**Current Phase**: 1 (In operations)

**Key Files**:
- `app/app.py` - Flask application
- `app/pdf_utils.py` - PDF tool encapsulation
- `docs/api.md` - API documentation
- `docs/openapi.yaml` - OpenAPI spec
- `docs/agent-protocol/README.md` - Agent protocol

**Role in Pact**: Foundation service for template recognition and matching

**Action Items**:
- [ ] Fix Playwright E2E tests (replace MDL with vanilla HTML) - W1

---

### ✅ dox-tmpl-pdf-upload

**Location**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-tmpl-pdf-upload/`

**Pact Service**: dox-tmpl-pdf-upload (Template Upload)

**Status**: Operational (minimal documentation)

**Technology**: Python Flask, vanilla JavaScript

**Current Phase**: 1 (In operations)

**Key Files**:
- README.md only (under-documented)

**Role in Pact**: Complements pdf-recognizer by handling template upload workflows

**Action Items**:
- [ ] Create `docs/api.md` following API_STANDARDS.md
- [ ] Create `docs/openapi.yaml` (OpenAPI 3.0 spec)
- [ ] Create `docs/ARCHITECTURE.md` explaining design
- [ ] Document integration points with dox-core-store
- [ ] Update README with full service description

---

### ✅ dox-admin

**Location**: `/workspace/cmhfcgyd7045kojiqg150pqth/dox-admin/`

**Pact Service**: dox-admin (Administrative Hub)

**Status**: Operational

**Purpose**: Central administrative hub and specification repository

**Structure**:
- `master/` - Master specification PDFs (5 files)
- `strategy/` - Governance documentation (centralized planning)

**Key Files**:
- `master/Core API Specification.pdf`
- `master/Database Schema Overview.pdf`
- `master/Pact Full System Specification (v2).pdf`
- `master/Pact Gateway_ Page Specification & Recommendations.pdf`
- `master/Gateway Sitemap.pdf`

**Role in Pact**: Central coordination hub for all 20 services

**Action Items**:
- [ ] This repository is the central coordination hub - no porting needed
- [ ] All other services register with this hub

---

## Repository Porting Process

### dox-pact-manual-upload → dox-rtns-manual-upload

**Current Status**: ⏳ To Port (Target: Week 2)

**Purpose Clarification**:
Frontend form for uploading scanned documents + barcode extraction

**GitHub Repository**:
- Source: `https://github.com/uberpu-ntiva/dox-pact-manual-upload`
- Target: `dox-rtns-manual-upload` (new repo in Pact Platform)

**Pact Architecture Mapping**:
- **Pact Service**: dox-rtns-manual-upload
- **Phase**: 3 (Business Services)
- **Team**: Signing Team
- **Timeline**: Weeks 14-18 (Porting starts W2)
- **Dependencies**:
  - Upstream: dox-core-auth (authentication)
  - Upstream: dox-core-store (storage)
  - Downstream: dox-rtns-barcode-matcher (sends scanned images)
  - Downstream: dox-actv-service (workflow integration)

**Porting Steps**:

#### Step 1: Analyze Existing Repository (Week 1-2)
```bash
# Clone the existing repo
git clone https://github.com/uberpu-ntiva/dox-pact-manual-upload.git

# Analyze structure
ls -la
cat README.md
tree app/
tree tests/ (if exists)
```

**Questions to Answer**:
- [ ] What's the exact purpose of this service?
- [ ] What files does it upload? (PDFs, images, both?)
- [ ] What barcode types does it support? (1D, 2D, QR, etc.)
- [ ] Current technology stack? (Flask? Node? What frontend framework?)
- [ ] What testing infrastructure exists?
- [ ] What are the dependencies? (external services, libraries, APIs?)
- [ ] What storage mechanism? (local filesystem, cloud storage?)
- [ ] Is authentication already implemented?

#### Step 2: Map to Pact Architecture (Week 2)
- [ ] Document current functionality
- [ ] Identify what stays vs what changes
- [ ] Design integration with Pact architecture
- [ ] Create mapping document

**Mapping Decisions**:
- **Upload Form**: Keep vanilla JS, ensure Playwright-compatible (no Material Design Lite)
- **File Storage**: Replace with dox-core-store integration
- **Barcode Extraction**: Keep existing barcode library (pyzbar or similar)
- **Authentication**: Integrate with dox-core-auth (JWT tokens)
- **Response Format**: Standardize to Pact API_STANDARDS.md format

#### Step 3: Restructure to SERVICE_TEMPLATE (Week 2)

**3.1 Prepare New Repository**:
```bash
# Create new directory for new service
mkdir dox-rtns-manual-upload
cd dox-rtns-manual-upload

# Copy SERVICE_TEMPLATE structure
cp -r /dox-admin/strategy/SERVICE_TEMPLATE/* .

# Initialize git
git init
git remote add origin [new-repo-url]
```

**3.2 Move Existing Code**:
```bash
# Copy app code from old repo to new /app directory
cp -r [old-repo]/app/* app/

# Restructure if needed to match SERVICE_TEMPLATE
# Ensure these directories exist:
# - app/
# - app/static/
# - app/templates/
# - tests/unit/
# - tests/integration/
# - docs/
```

**3.3 Update Configuration**:
- [ ] **app/requirements.txt** - Add/remove dependencies as needed
- [ ] **README.md** - Replace with Pact-specific content
- [ ] **.env.example** - Document required env variables
- [ ] **Dockerfile** - Ensure uses SERVICE_TEMPLATE version
- [ ] **docker-compose.yml** - Configure dependencies on other services
- [ ] **Makefile** - Update service name

**3.4 Create/Update Documentation**:
- [ ] **docs/api.md** - Create REST API documentation (human-readable)
- [ ] **docs/openapi.yaml** - Create OpenAPI 3.0 spec
- [ ] **docs/ARCHITECTURE.md** - Document design and integration points
- [ ] **docs/SETUP.md** - How to set up dev environment
- [ ] Copy **docs/agent-protocol/README.md** from dox-tmpl-pdf-recognizer

**3.5 Update Code for Pact Compliance**:
- [ ] Replace file upload form with vanilla HTML (Playwright-compatible)
- [ ] Update upload API to match API_STANDARDS.md
- [ ] Add authentication middleware (dox-core-auth integration)
- [ ] Implement file validation (size, MIME type, virus scan)
- [ ] Update error handling (match Pact error format)
- [ ] Add health check endpoint (`GET /health`)
- [ ] Update logging (follow Pact patterns)
- [ ] Add multi-tenancy support (enforce siteId)

**3.6 Update Tests**:
- [ ] Move/update unit tests to `tests/unit/`
- [ ] Create integration tests in `tests/integration/`
- [ ] Create E2E tests in `tests/e2e/` (Playwright for upload form)
- [ ] Target: 80%+ code coverage
- [ ] Ensure all tests use `make test`

**3.7 Finalize Documentation**:
- [ ] AGENTS.md - Copy from dox-tmpl-pdf-recognizer (standard)
- [ ] .gitignore - Copy from SERVICE_TEMPLATE (standard)
- [ ] All [REPLACE_ME] placeholders filled in
- [ ] README.md complete with Pact context

#### Step 4: Register & Coordinate (Week 2)

**4.1 Update Central Registry**:
```bash
# 1. Edit /dox-admin/strategy/SERVICES_REGISTRY.md
# - Update dox-rtns-manual-upload entry
# - Set status to "In Progress" (W14-18)
# - Set team to "Signing Team"
# - Document dependencies

# 2. Create memory bank entry
# /dox-admin/strategy/memory-banks/SERVICE_dox-rtns-manual-upload.json
{
  "service_name": "dox-rtns-manual-upload",
  "team": "Signing",
  "status": "ported",
  "current_sprint": 1,
  "start_week": 14,
  "estimated_completion": 18,
  "current_task": "Integration testing",
  "blockers": [],
  "dependencies": ["dox-core-auth", "dox-core-store"],
  "test_status": "85% - E2E needed",
  "last_update": "2025-10-31T00:00:00Z"
}

# 3. Update team coordination file
# /dox-admin/strategy/memory-banks/TEAM_SIGNING.json
# - Add dox-rtns-manual-upload to services list
# - Update team status
```

**4.2 Update REPO_MAPPING.md**:
- [ ] Mark dox-pact-manual-upload as ported
- [ ] Record completion date
- [ ] Add any notes about the porting process

**4.3 Notify Teams**:
- [ ] Post in #signing-team Slack channel
- [ ] Update sprint board
- [ ] Mention in daily standup
- [ ] Add to SERVICES_REGISTRY.md dependencies for dependent services

#### Step 5: Local Testing (Week 2)

Before releasing:
```bash
make test       # All tests pass
make build      # Docker image builds
make docker-up  # Services start
curl http://localhost:5000/health  # Health check works
```

---

## Porting Checklist for dox-pact-manual-upload

Before marking as complete:

- [ ] Code copied to new repo structure
- [ ] All files from SERVICE_TEMPLATE present
- [ ] All [REPLACE_ME] placeholders filled
- [ ] Documentation complete (api.md, openapi.yaml, ARCHITECTURE.md, SETUP.md)
- [ ] Tests updated (target 80%+ coverage)
- [ ] `make test` passes 100%
- [ ] `make build` succeeds
- [ ] `make docker-up` starts services
- [ ] Health check endpoint working
- [ ] API follows Pact standards (error format, auth, pagination)
- [ ] AGENTS.md copied
- [ ] .gitignore copied
- [ ] README.md updated with Pact context
- [ ] Registered in SERVICES_REGISTRY.md
- [ ] Memory bank entry created
- [ ] Team coordination file updated
- [ ] Git repo initialized with tags
- [ ] Initial commit made and pushed

---

## Future Repository Porting

**Criteria for Porting**:
- Existing repo implements Pact service functionality
- Code is reasonably well-structured
- Tests exist (at least some)
- Not dependent on specific deployment (can run in Docker)

**Process**:
1. Identify repository on GitHub
2. Document in REPO_MAPPING.md
3. Follow steps above
4. Register in SERVICES_REGISTRY.md

**Questions for User**:
- Are there other existing repos to port?
- Should we focus on porting dox-pact-manual-upload first or look for others?
- Are there specific repos you want prioritized?

---

## References

**Related Documents**:
- `/dox-admin/strategy/SERVICES_REGISTRY.md` - Master service catalog
- `/dox-admin/strategy/SERVICE_TEMPLATE/` - Boilerplate for new services
- `/dox-admin/strategy/standards/API_STANDARDS.md` - API patterns
- `/dox-admin/strategy/standards/DEPLOYMENT_STANDARDS.md` - Deployment patterns

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-10-31
**Version**: 1.0


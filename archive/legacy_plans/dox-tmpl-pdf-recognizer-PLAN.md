# dox-tmpl-pdf-recognizer: Service Planning

**Centralized Planning for PDF Template Recognition Service**

**Location**: `/dox-admin/strategy/planning/service-plans/dox-tmpl-pdf-recognizer-PLAN.md`

**Repository**: `/dox-tmpl-pdf-recognizer`

**Service Type**: Document Recognition

**Phase**: 1 (Current - Stable v1.0.0)

**Status**: Active & Operational

**Last Updated**: 2025-10-31

---

## Service Overview

Core PDF template recognition and matching engine. Compares uploaded PDFs against stored templates using weighted scoring (70% text similarity + 30% form field matching).

**Team Assignment**: N/A (Existing service, no team assigned until Phase 2)

**GitHub**: `uberpu-ntiva/dox-tmpl-pdf-recognizer`

---

## Completed Work (v1.0.0)

### Core Features
- ✅ Full-stack application (Flask backend + vanilla JS frontend)
- ✅ PDF recognition engine (weighted scoring algorithm)
- ✅ Monorepo structure with documentation
- ✅ Docker containerization
- ✅ Multi-agent collaboration framework
- ✅ Agent protocol documentation
- ✅ Contributor dashboard UI
- ✅ Governance standards integration

### Key Components Implemented
- ✅ `app/app.py` - Flask application with routes
- ✅ `app/pdf_utils.py` - PDF tool encapsulation
- ✅ Template upload endpoint (`POST /api/templates`)
- ✅ Document recognition endpoint (`POST /api/recognize`)
- ✅ Declaration endpoint (`POST /api/declare`)
- ✅ Dashboard endpoint (`GET /dashboard`)
- ✅ API documentation (`docs/api.md`)
- ✅ OpenAPI specification (`docs/openapi.yaml`)
- ✅ Architecture documentation
- ✅ Deployment configurations (Docker, AWS, Azure)

---

## Current Backlog & Tasks

### CRITICAL PRIORITY

#### T04: Fix Playwright E2E Tests

**Status**: 🔴 TO DO (BLOCKING)

**Issue**:
- Playwright E2E tests timeout when interacting with Material Design Lite file input elements
- `make test` command fails
- Blocking all frontend validation work

**Impact**:
- Cannot validate frontend changes
- Blocks Phase 1 completion
- Blocks gateway application development (phase 3)

**Root Cause**:
- MDL framework interferes with Playwright's interaction model
- File input interaction not properly handled by Playwright

**Solution**:
- Replace Material Design Lite with vanilla HTML5 file input
- Ensure `<input type="file" />` is Playwright-compatible
- Remove MDL dependency from upload form

**Acceptance Criteria**:
- [ ] MDL removed from file upload form
- [ ] Vanilla HTML5 file input implemented
- [ ] All E2E tests passing (`make test` = 100%)
- [ ] No Playwright errors or timeouts
- [ ] UI still functional and user-friendly

**Estimated Effort**: 3-5 days

**Owner**: Infrastructure team / First implementation agent

**Target Week**: Week 1 (URGENT)

---

### HIGH PRIORITY

#### T04B: Backend File Validation

**Status**: ⏳ PLANNED

**Scope**: All file upload services

**Requirements**:
- [ ] File size validation (PDF max 50MB, images max 10MB)
- [ ] MIME type validation (whitelist application/pdf, image/png, image/jpeg)
- [ ] Virus scanning (ClamAV integration)
- [ ] Content scanning (reject suspicious headers)
- [ ] Metadata storage (hash, original name, timestamp)
- [ ] Filename sanitization (prevent path traversal)
- [ ] Rate limiting (prevent abuse)

**Implementation Location**: `app/pdf_utils.py` or new `app/file_validator.py`

**Estimated Effort**: 2-3 days

**Target Week**: Week 1-2

---

### MEDIUM PRIORITY

#### Implement UI Overlay Feature

**Status**: ⏳ PLANNED

**Description**:
- Overlay template SVG on top of document page image for visual comparison
- Helps users verify template matches before declaration
- Implement in `static/js/main.js`

**Acceptance Criteria**:
- [ ] SVG overlay rendered on document image
- [ ] Overlay toggleable (show/hide)
- [ ] Responsive to zoom/pan
- [ ] No performance degradation

**Estimated Effort**: 3-4 days

**Target Week**: Week 3-4

---

#### Refine Scoring Algorithm

**Status**: ⏳ PLANNED

**Current Algorithm**:
- 70% text similarity (fuzzywuzzy)
- 30% form field similarity (Jaccard index via pdftk)
- Returns top 5 matches per page

**Improvements**:
- [ ] Make weighting configurable
- [ ] Test with more document types
- [ ] Explore advanced text comparison (TFIDF, semantic similarity)
- [ ] Add relevance scoring based on field names
- [ ] Tune thresholds based on real-world data

**Estimated Effort**: 2-3 days (iterative)

**Target Week**: Week 4+

---

#### Improve "Recognition Profiles"

**Status**: ⏳ PLANNED

**Current Implementation**:
- Saves text of matched pages for learning

**Improvements**:
- [ ] Build structured ML pipeline
- [ ] Train model on recognition decisions (declarations)
- [ ] Use profiles to improve matching scores over time
- [ ] Add confidence scoring
- [ ] Track profile effectiveness

**Estimated Effort**: 5-7 days

**Target Week**: Week 5+

**Dependencies**:
- Requires sufficient real-world usage data
- May need data science expertise

---

### LOW PRIORITY

#### Production Deployment Optimization

**Status**: ⏳ PLANNED

**Current**: Flask development server

**Required for Production**:
- [ ] WSGI server setup (Gunicorn)
- [ ] Reverse proxy (Nginx)
- [ ] Load balancing configuration
- [ ] SSL/TLS setup
- [ ] Health check endpoint
- [ ] Graceful shutdown handling
- [ ] Performance tuning
- [ ] Monitoring & alerting

**Estimated Effort**: 2-3 days

**Target Week**: Week 5+

---

#### Template Management UI

**Status**: ⏳ PLANNED

**Current**: Only template upload available

**New Features**:
- [ ] View existing templates
- [ ] Search templates (by name, type, date)
- [ ] Delete templates
- [ ] Edit template metadata
- [ ] Bulk operations
- [ ] Pagination and sorting

**Estimated Effort**: 3-4 days

**Target Week**: Week 6+

---

#### UI/UX Refinements

**Status**: ⏳ PLANNED

**Improvements**:
- [ ] Better loading indicators (spinners, progress bars)
- [ ] More detailed error messages
- [ ] Polished visual design
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)

**Estimated Effort**: Ongoing (low priority)

---

## Dependencies

### Upstream (What We Depend On)
- None (foundation service for recognition)

### Downstream (What Depends On Us)
- dox-gtwy-main (Gateway app will consume templates)
- dox-tmpl-service (future replacement for template CRUD)
- dox-data-aggregation-service (may use recognition data)

---

## Integration Points

### Current
- Standalone service (v1.0.0)
- Not yet integrated with Pact core services

### Phase 2 Integration
- Will depend on dox-core-store (central storage)
- Will depend on dox-core-auth (authentication)
- Will feed into dox-gtwy-main (gateway app)

### Phase 3 Integration
- Will be replaced by dox-tmpl-service (more advanced)
- Field mapping will use dox-tmpl-field-mapper

---

## Technical Debt

### Known Issues
1. **Playwright E2E Tests** (CRITICAL)
   - MDL file input incompatibility
   - Tests timeout on file interactions
   - **Fix Target**: Week 1

2. **Missing API Documentation** (MEDIUM)
   - API docs incomplete
   - OpenAPI spec needs updating
   - **Fix Target**: Week 2

3. **Limited Error Handling** (MEDIUM)
   - Some edge cases not handled
   - Error messages not standardized
   - **Fix Target**: Week 3

4. **PDF Tool Encapsulation** (LOW)
   - Could improve pdf_utils.py organization
   - Error handling in CLI wrapper
   - **Fix Target**: Week 4+

---

## Testing Status

| Test Type | Status | Coverage |
|-----------|--------|----------|
| Unit Tests | ✅ Passing | ~85% |
| Integration Tests | ✅ Passing | ~60% |
| E2E Tests | ❌ Failing | N/A (MDL issue) |
| API Tests | ✅ Passing | ~90% |

**Target**: 100% E2E passing after MDL fix (Week 1)

---

## Deployment Status

| Environment | Status | Version |
|-------------|--------|---------|
| Development | ✅ Active | v1.0.0 |
| Docker Local | ✅ Working | Latest |
| AWS | ⏳ Planned | TBD |
| Azure | ⏳ Planned | TBD |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Code Files | 3 (app.py, pdf_utils.py + routes) |
| Test Coverage | 85% (unit/integration) |
| API Endpoints | 4 |
| Python Version | 3.10+ |
| Dependencies | ~15 packages |
| Docker Image Size | ~500MB (optimizable) |

---

## Governance Alignment

**Standards Applied**:
- ✅ API_STANDARDS.md - REST patterns
- ✅ TECHNOLOGY_STANDARDS.md - Python/Flask/vanilla JS
- ✅ MULTI_AGENT_COORDINATION.md - Agent protocol
- ✅ DEPLOYMENT_STANDARDS.md - Docker setup

**Next Alignment**:
- Phase 2: Integrate with dox-core-auth (JWT enforcement)
- Phase 2: Integrate with dox-core-store (centralized storage)
- Phase 3: Replace with dox-tmpl-service (more advanced)

---

## Sprint Planning

### Sprint 1: Multi-Agent Foundation (Weeks 1-4)

**In Sprint**:
- ✅ T01: Agent protocol
- ✅ T02: Dashboard UI
- ✅ T03: Sprint planning
- 🔴 T04: Fix E2E tests (HIGH PRIORITY)

**Related**:
- T04B: File validation (concurrent)
- Governance standards setup

### Sprint 2+: Service Enhancements (Weeks 5+)

- [ ] UI overlay feature
- [ ] Algorithm refinement
- [ ] Recognition profiles ML
- [ ] Production deployment
- [ ] Template management UI

---

## Coordination Notes

**Cross-Team Dependencies**:
- Signing team will use this for document extraction (Phase 3)
- Frontend team will integrate templates into gateway (Phase 3)
- Data team may consume recognition results (Phase 3+)

**Handoff Points**:
- Phase 2 W8: Migrate to dox-core-store + dox-core-auth
- Phase 3 W22: UI integrated into dox-gtwy-main

**Known Risks**:
- Test suite fix critical path (currently blocking Phase 1)
- ML profile training needs sufficient real-world data
- Performance may degrade with large template libraries

---

## How to Contribute

1. Check this plan for assigned tasks
2. Pick a task from backlog
3. Create feature branch: `feature/pdf-recognizer/[task-name]`
4. Follow git workflow: `standards/MULTI_AGENT_COORDINATION.md`
5. Update progress in memory banks: `memory-banks/SERVICE_dox-tmpl-pdf-recognizer.json`
6. Create PR when ready

---

## References

**Source Documents**:
- Original tasks: `/dox-tmpl-pdf-recognizer/docs/tasks.md`
- Sprint planning: `/dox-tmpl-pdf-recognizer/docs/plans/sprint_1.md`
- API docs: `/dox-tmpl-pdf-recognizer/docs/api.md`
- Architecture: `/dox-tmpl-pdf-recognizer/docs/archive-architecture.md`

**Related Planning**:
- `SERVICES_REGISTRY.md` - Service catalog entry
- `memory-banks/SERVICE_dox-tmpl-pdf-recognizer.json` - Real-time status
- `PLANNING_FILES_REGISTRY.md` - Master planning index

**Standards**:
- `standards/API_STANDARDS.md` - REST patterns
- `standards/TECHNOLOGY_STANDARDS.md` - Tech stack
- `standards/DEPLOYMENT_STANDARDS.md` - Deployment

---

**Status**: ✅ ACTIVE & CONSOLIDATED

**Last Updated**: 2025-10-31

**Owner**: PDF Recognition Service Team (TBD)

**Next Update**: Weekly (each Friday 4 PM)


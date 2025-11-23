# dox-tmpl-pdf-upload: Service Planning

**Centralized Planning for PDF Template Upload Service**

**Repository**: `/dox-tmpl-pdf-upload`

**Service Type**: Template Upload & Management

**Phase**: 1 (Current - Minimal v1.0.0)

**Status**: Operational (Under-documented)

**Last Updated**: 2025-10-31

---

## Service Overview

Handles PDF template upload workflows. Complements pdf-recognizer by managing template ingestion pipelines and validation.

**Status**: Functional but under-documented (README only, no API docs, no architecture)

**GitHub**: `uberpu-ntiva/dox-tmpl-pdf-upload`

---

## Completed Work (v1.0.0)

- ✅ Basic upload functionality
- ✅ Template storage
- ✅ Minimal README

---

## Current Backlog & Tasks

### CRITICAL PRIORITY

#### Documentation Gap (T09)

**Status**: 🔴 TO DO (BLOCKING for Phase 2)

**Issue**:
- No API documentation
- No OpenAPI specification
- No architecture documentation
- No integration points defined
- No error handling documented

**Impact**:
- Cannot integrate with Phase 2 services (dox-core-store, dox-core-auth)
- Blocks other teams from understanding integration points
- Risk of duplicate work (dox-tmpl-service replacing this)

**Requirements**:
- [ ] Create `docs/api.md` (human-readable API)
- [ ] Create `docs/openapi.yaml` (OpenAPI 3.0 spec)
- [ ] Create `docs/ARCHITECTURE.md` (design decisions)
- [ ] Create `docs/SETUP.md` (dev environment)
- [ ] Update README with full service description
- [ ] Document integration with dox-core-store
- [ ] Document authentication requirements
- [ ] Document error handling

**Acceptance Criteria**:
- [ ] All docs complete and accurate
- [ ] API follows API_STANDARDS.md
- [ ] Integration points clear
- [ ] Setup reproducible

**Estimated Effort**: 2-3 days

**Owner**: Upload service team / First implementation agent

**Target Week**: Week 1-2 (parallel with tests fix)

---

#### File Validation Implementation

**Status**: ⏳ PLANNED (same as pdf-recognizer)

**Scope**:
- [ ] File size validation (max 50MB)
- [ ] MIME type validation (whitelist PDF, PNG, JPEG)
- [ ] Virus scanning
- [ ] Content validation
- [ ] Rate limiting

**Estimated Effort**: 2-3 days

**Target Week**: Week 1-2

---

### HIGH PRIORITY

#### Integration with dox-core-store

**Status**: ⏳ PLANNED

**Task**:
- [ ] Replace local storage with dox-core-store
- [ ] Implement multi-tenancy (siteId isolation)
- [ ] Add authentication middleware (JWT)
- [ ] Update API to match standards

**Estimated Effort**: 3-4 days

**Target Week**: Week 8+ (after dox-core-store ready)

---

#### API Standardization

**Status**: ⏳ PLANNED

**Task**:
- [ ] Update endpoints to match API_STANDARDS.md
- [ ] Standardize error responses
- [ ] Add request validation
- [ ] Add rate limiting

**Estimated Effort**: 1-2 days

**Target Week**: Week 1

---

### MEDIUM PRIORITY

#### Playwright E2E Tests

**Status**: ⏳ PLANNED

**Task**:
- [ ] Create E2E tests for upload form
- [ ] Use vanilla HTML (not MDL)
- [ ] Test file validation errors
- [ ] Test success paths

**Estimated Effort**: 2-3 days

**Target Week**: Week 2-3

---

## Dependencies

### Upstream
- None (can operate standalone)

### Downstream
- dox-core-store (will store templates)
- dox-gtwy-main (gateway will manage templates)
- dox-tmpl-service (will eventually replace this)

---

## Technical Debt

1. **Missing Documentation** (CRITICAL)
   - No API docs
   - No architecture docs
   - **Fix Target**: Week 1-2

2. **No Integration Tests** (HIGH)
   - Only basic unit tests
   - **Fix Target**: Week 2

3. **Limited Error Handling** (MEDIUM)
   - Needs standardization
   - **Fix Target**: Week 1

4. **Local Storage** (MEDIUM)
   - Not scalable for multi-tenant
   - **Fix Target**: Week 8+

---

## Governance Alignment

**To Apply**:
- API_STANDARDS.md (REST patterns)
- TECHNOLOGY_STANDARDS.md (Python/Flask)
- DEPLOYMENT_STANDARDS.md (Docker)
- MULTI_AGENT_COORDINATION.md (Agent protocol)

---

## Sprint Planning

### Sprint 1: Documentation & Standardization (Weeks 1-2)

**Tasks**:
- [ ] T09: Complete documentation
- [ ] File validation (concurrent with pdf-recognizer)
- [ ] API standardization
- [ ] Governance alignment

### Sprint 2+: Integration & Enhancement

- [ ] Integrate with dox-core-store
- [ ] Add E2E tests
- [ ] Performance optimization
- [ ] Multi-tenancy support

---

## How to Contribute

1. Pick a task from this plan
2. Create feature branch: `feature/pdf-upload/[task-name]`
3. Follow standards
4. Update memory banks
5. Create PR

---

**Status**: ✅ PLANNING CONSOLIDATED

**Last Updated**: 2025-10-31


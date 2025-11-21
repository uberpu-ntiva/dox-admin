# Research

## Summary
The Phase 1 governance infrastructure is complete with a comprehensive governance hub in dox-admin/strategy/ containing 20-service registry, centralized planning, and multi-agent coordination framework. Week 2 critical path tasks are identified and ready for execution.

## Repository: dox-admin

### Component: Governance Hub
**Location:** `dox-admin/strategy/`

**Key files**
- `strategy/README.md` - Master navigation and coordination hub
- `strategy/SERVICES_REGISTRY.md` - Complete catalog of all 20 microservices with dependencies, timelines, and team assignments
- `strategy/PHASE_1_IMPLEMENTATION_COMPLETE.md` - Phase 1 completion summary
- `strategy/PLANNING_FILES_REGISTRY.md` - Master planning document index

**How it works**
- Comprehensive governance standards frozen in 4 documents (API, Technology, Multi-agent Coordination, Deployment)
- Service template boilerplate ready for all 20 services with 13-phase checklist
- 12+ memory bank JSON files for real-time agent coordination across 7 teams
- Complete dependency mapping and critical path identification

**Connections**
- Central coordination hub linking all 20 services
- Memory banks provide real-time status tracking
- Planning documents integrated with service registry

## Repository: dox-tmpl-pdf-recognizer

### Component: PDF Recognition Service
**Location:** `dox-tmpl-pdf-recognizer/`

**Key files**
- `app/app.py` - Flask application with recognition endpoints
- `app/pdf_utils.py` - PDF processing utilities
- `tests/` - Test suite with Playwright E2E tests (currently failing)

**How it works**
- PDF template recognition using weighted scoring (70% text + 30% form fields)
- Material Design Lite frontend components causing Playwright test failures
- Multi-agent collaboration dashboard already implemented

**Connections**
- Foundation service for document recognition
- Will integrate with dox-core-store and dox-core-auth in Phase 2

## Repository: dox-tmpl-pdf-upload

### Component: Template Upload Service
**Location:** `dox-tmpl-pdf-upload/`

**Key files**
- README.md only (minimal documentation)
- Basic Flask application structure

**How it works**
- Handles PDF template upload workflows
- Complements pdf-recognizer service
- Currently under-documented with no API docs

**Connections**
- Needs integration with dox-core-store for centralized storage
- Will be replaced by dox-tmpl-service in Phase 2

## Repository: dox-pact-manual-upload

### Component: Document Return Processing System
**Location:** `dox-pact-manual-upload/`

**Key files**
- `app/app.py` - Complex Flask app with comprehensive document processing
- `app/ocr_utils.py` - OCR and barcode processing
- `app/pdf_utils.py` - PDF manipulation utilities
- `app/models.py` - Database models for document returns
- Comprehensive API endpoints for document processing workflow

**How it works**
- Processes system-originated documents with datamatrix codes
- Handles manual/external documents with template matching
- OCR integration with EasyOCR and handwriting detection
- SharePoint integration for document storage
- Complex database schema for document tracking

**Connections**
- Target for porting to dox-rtns-manual-upload
- Will integrate with dox-core-auth and dox-core-store
- Complex service requiring careful migration planning

### Critical Week 2 Tasks Identified

**Task T04: Fix Playwright E2E Tests**
- Location: dox-tmpl-pdf-recognizer
- Issue: MDL file input component incompatible with Playwright
- Status: Blocking - needs immediate attention

**Task T09: Complete Documentation**
- Location: dox-tmpl-pdf-upload
- Issue: Minimal documentation (README only)
- Status: Blocking integration work

**Task T05: File Validation Infrastructure**
- Scope: All upload services
- Architecture: Shared validation modules embedded in services (not separate service)
- Status: Critical for platform security
- Implementation: ClamAV integration, Redis rate limiting, MIME validation

**Task T06: Port dox-pact-manual-upload**
- Source: dox-pact-manual-upload (existing, complex service)
- Target: dox-rtns-manual-upload
- Status: Ready for porting with comprehensive 5-step process
- Complexity: Document return processing with OCR, barcode extraction, SharePoint integration

**Task T07: Team Onboarding**
- Scope: 7 teams across 20 services
- Structure: Infrastructure, Document, Signing, Activation, Data, Frontend, Automation teams
- Status: Memory banks and coordination protocols ready

## Coordination Framework

### Multi-Agent Coordination System
**Location:** `dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`

**Components**
- File locking protocol for preventing conflicts
- Memory bank structure for real-time status tracking
- Agent lifecycle and state management
- Supervisor coordination role

**Memory Banks Structure**
- `SUPERVISOR.json` - Master coordination log
- `TEAM_[name].json` - Team status for 7 teams
- `SERVICE_[name].json` - Per-service tracking
- `BLOCKING_ISSUES.json` - Cross-team dependencies
- `API_CONTRACTS.json` - Versioned API specifications

### Service Template Structure
**Location:** `dox-admin/strategy/SERVICE_TEMPLATE/`

**Ready Components**
- 13-phase checklist for service creation
- Standard file structure and documentation templates
- Docker deployment configurations
- API standards compliance templates

## Workflow Rules Coordination

### Existing Workflow Patterns
**From dox-pact-manual-upload analysis**
- Document upload → OCR processing → Template matching → Field mapping → Account association
- System documents use datamatrix codes for automatic batch identification
- Manual documents require template matching and field mapping workflows
- SharePoint integration with version conflict resolution

**From dox-tmpl-pdf-recognizer**
- Template upload → PDF analysis → Recognition profile creation
- Multi-agent collaboration dashboard for decision management
- Declaration workflow for saving match decisions

### Integration Patterns
- All services follow API_STANDARDS.md for consistent REST patterns
- JWT authentication middleware from dox-core-auth
- Centralized storage via dox-core-store
- File validation modules embedded in each service
- Memory bank updates for real-time coordination

## Implementation Readiness

### Phase 1 Complete ✅
- Governance infrastructure operational
- Service registry cataloging all 20 services
- Planning hub with centralized task management
- Multi-agent coordination framework ready

### Week 2 Critical Path 🔄
- T04: Playwright tests (BLOCKING - pdf-recognizer)
- T09: Documentation (BLOCKING - pdf-upload)
- T05: File validation (CRITICAL - all services)
- T06: Service porting (HIGH - rtns-manual-upload)
- T07: Team onboarding (HIGH - coordination)

### Dependencies Mapped
- Complete service dependency graph available
- Cross-team coordination protocols defined
- Integration points documented
- Risk mitigation strategies in place

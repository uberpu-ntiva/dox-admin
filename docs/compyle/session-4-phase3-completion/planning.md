# Phase 3: Hybrid Implementation + AGENTS.md Distribution

## Overview
Continuing from Phase 1 & 2 completion (documented in dox-admin/continuity/CONTINUITY_MEMORY.md), this plan covers:

1. **Create HYBRID_IMPLEMENTATION_PLAN.md** - Formal plan for Phase 3 hybrid approach
2. **Distribute AGENTS.md files** - Add agent coordination protocols to all 22 missing repositories

## Current State Analysis

**From research.md:**
- 4/26 repositories have AGENTS.md (DOX, dox-mcp-server, dox-pact-manual-upload, dox-tmpl-pdf-recognizer)
- 22/26 repositories missing AGENTS.md
- No AGENTS.md exists in dox-admin itself
- No AGENTS.md template in dox-admin/strategy/SERVICE_TEMPLATE/

**AGENTS.md Complexity Patterns Found:**
- **Basic** (DOX): 32 lines, generic template with Jules capabilities
- **Service-Focused** (dox-tmpl-pdf-recognizer): 35 lines, tool-specific
- **Comprehensive** (dox-mcp-server): 319 lines, complete protocol with best practices, daily sync requirements, continuity updates

**Key Resource:**
- `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md` - Master coordination protocol
- `/dox-admin/strategy/SERVICES_REGISTRY.md` - Service metadata for customization

## Desired End State

**After implementation:**
1. ✅ HYBRID_IMPLEMENTATION_PLAN.md exists in dox-admin/continuity/ with complete Phase 3 strategy
2. ✅ Master AGENTS.md exists in dox-admin/
3. ✅ All 22 missing repositories have customized AGENTS.md files
4. ✅ AGENTS.md template added to dox-admin/strategy/SERVICE_TEMPLATE/docs/
5. ✅ Each service-specific AGENTS.md references correct service metadata
6. ✅ All AGENTS.md files reference /dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md
7. ✅ Continuity memory updated with implementation details

---

## Task 1: HYBRID_IMPLEMENTATION_PLAN.md Creation

**Purpose:** Document the complete Phase 3 hybrid implementation strategy

**Sections to include:**
1. **Executive Summary** - Overview of hybrid approach
2. **Phase 3A: Local Infrastructure Setup** - Details from CONTINUITY_MEMORY.md
   - MSSQL, Redis, File Storage deployment
   - Web interfaces for access
   - Jules MCP server creation
3. **Phase 3B: Core Services Completion** - Service-by-service roadmap
4. **Phase 3C: Production Architecture** - Advanced UI and testing
5. **Timeline & Milestones** - Week-by-week breakdown
6. **Resource Requirements** - Infrastructure costs and alternatives
7. **Success Criteria** - How to measure completion

---

## Task 2: AGENTS.md Distribution

**22 Repositories Missing AGENTS.md:**
1. dox-admin
2. dox-actv-listener
3. dox-actv-service
4. dox-auto-lifecycle-service
5. dox-auto-workflow-engine
6. dox-batch-assembly
7. dox-core-auth
8. dox-core-rec-engine
9. dox-core-store
10. dox-data-aggregation-service
11. dox-data-distrib-service
12. dox-data-etl-service
13. dox-esig-service
14. dox-esig-webhook-listener
15. dox-gtwy-main
16. dox-rtns-barcode-matcher
17. dox-rtns-manual-upload
18. dox-tmpl-field-mapper
19. dox-tmpl-pdf-upload
20. dox-tmpl-service
21. jules-mcp
22. test-jules

---

## Planning Questions & Decisions

**AGENTS.md Complexity Level:**
- ✅ DECISION: Use comprehensive pattern (dox-mcp-server model) for all services
- Rationale: Ensures full protocol compliance, daily sync requirements, continuity updates

---

## Task 3: Master AGENTS.md for dox-admin

**Location:** `/dox-admin/AGENTS.md`

**Customization:**
- **Objective**: Central coordination hub and specification repository
- **Architecture**: Focus on strategy/ folder structure, governance files, memory-banks
- **Core Technologies**:
  - Markdown (documentation standards)
  - JSON (memory-banks coordination)
  - Git (version control)
- **Key Files**:
  - `strategy/SERVICES_REGISTRY.md` - Master service catalog
  - `strategy/standards/MULTI_AGENT_COORDINATION.md` - Coordination protocol
  - `continuity/CONTINUITY_MEMORY.md` - Implementation tracking
  - `memory-banks/` - Agent coordination files

**Sections to include:**
1. Objective
2. Architecture & Key Files
3. Core Technologies
4. Multi-Agent Collaboration Protocol (reference)
5. Development Workflow
6. Continuity Updates (CRITICAL - update CONTINUITY_MEMORY.md)
7. Best Practices & Sync Requirements (daily)

---

## Task 4: AGENTS.md Template for SERVICE_TEMPLATE

**Location:** `/dox-admin/strategy/SERVICE_TEMPLATE/docs/AGENTS.md`

**Purpose:** Comprehensive template for all future services (300+ lines)

**Complete Template Structure (comprehensive pattern):**

```markdown
# Agent Protocol: [SERVICE_NAME]

## Objective

**CUSTOMIZE**: Replace this section with your service's specific purpose.
Example: "This document provides the specific protocols and conventions for working on the [SERVICE_NAME] service. All agents must adhere to these rules."

**Template placeholder**: "This service provides [brief description of service purpose] for the Pact Platform."

## Architecture & Key Files

**CUSTOMIZE**: List the key files and directories for your service.

**Template placeholder structure**:
- **`app/main.py`**: [Main application entry point - Flask/FastAPI application]
- **`app/models/`**: [Data models and database schemas]
- **`app/api/v1/endpoints/`**: [REST API endpoint implementations]
- **`app/services/`**: [Business logic and service layer]
- **`app/core/`**: [Core configuration and dependencies]
- **`tests/`**: [Unit and integration tests]
- **`docs/`**: [API documentation and architecture]
- **`requirements.txt`**: [Python dependencies]
- **`Dockerfile`**: [Container configuration]

## Core Technologies

**CUSTOMIZE**: List your service's technology stack.

**Template placeholder**:
- **Backend**: Python Flask (or FastAPI for async services)
- **Database**: [Specify: MSSQL, PostgreSQL, Redis, or None]
- **ORM**: SQLAlchemy (if database used)
- **Testing**: pytest (unit + integration)
- **Containerization**: Docker
- **Additional**: [Service-specific libraries]

## Multi-Agent Collaboration Protocol

**FIXED**: All agents must adhere to the formal protocol for task acknowledgement, file locking, and status reporting.

**IMPORTANT: All agents MUST read and adhere to the full protocol documented in `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md` before taking any action.**

Failure to comply with the protocol may result in conflicting changes and work being overwritten.

## Development Workflow

**Generic workflow (customize as needed)**:

1. **Dependencies**: All Python dependencies must be added to `requirements.txt`
2. **Testing**:
   - Unit tests: `pytest tests/unit/`
   - Integration tests: `pytest tests/integration/`
   - API tests: `pytest tests/api/`
3. **Documentation**:
   - Update `README.md` with service overview
   - Create `docs/api.md` with OpenAPI specification
   - Add comprehensive docstrings to all functions
4. **Code Quality**:
   - Run `black app/` to format code
   - Run `flake8 app/` to lint code
   - Run `mypy app/` for type checking

## Adding New Features

**When adding new features**:

1. Create feature branch: `feature/[service]/[description]`
2. Implement following API_STANDARDS.md patterns
3. Add comprehensive tests
4. Update documentation
5. Submit pull request for review
6. Update memory-banks/SERVICE_[service-name].json

## Service Integration

**CUSTOMIZE**: Document how this service integrates with others.

**Template placeholder**:
This service integrates with:
- **dox-core-auth**: Authentication and authorization
- **dox-core-store**: Data storage and retrieval
- **[Other services]**: [Description of integration]

All HTTP calls to other services must:
- Use async httpx client (if using FastAPI)
- Include authentication headers
- Handle timeouts gracefully (default: 30s)
- Retry on transient failures
- Log all requests with correlation IDs

## Error Handling Standards

**Standardized error handling (customize specifics)**:

```python
try:
    result = await perform_operation()
    return {"success": True, "data": result}
except ValidationError as e:
    return {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": str(e),
            "retryable": False
        }
    }
except ServiceUnavailableError as e:
    logger.error(f"Service unavailable: {e}", extra={"correlation_id": correlation_id})
    return {
        "success": False,
        "error": {
            "code": "SERVICE_UNAVAILABLE",
            "message": str(e),
            "retryable": True
        }
    }
```

## Configuration Management

**Standard configuration approach**:

All configuration through environment variables:
- `SERVICE_PORT`: Service port (default: 8080)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `DATABASE_URL`: Database connection string (if applicable)
- `API_BASE_URL`: Base URL for API calls
- [Service-specific environment variables]

Never hardcode URLs, credentials, or configuration values.

## Health Monitoring

**Standard health endpoints**:

The service provides health check endpoints:
- `GET /health`: Basic health check
- `GET /health/detailed`: Detailed health with dependency status

Health checks must verify:
- Service is running
- Database connections (if applicable)
- External service dependencies
- All critical components are functional

## Best Practices & Sync Requirements

**MANDATORY DAILY SYNC**: This document must be checked and updated if it's more than 1 day old to ensure best practices compliance.

### General Best Practices (2025 Standards)

**Development Standards**:
- ✅ **Clear Boundaries**: Each service should have a single, well-defined responsibility
- ✅ **API Versioning**: Use `/api/v1/` for all endpoints
- ✅ **Error Handling**: Provide structured error responses with retry indicators
- ✅ **Input Validation**: Use Pydantic models for all input parameters
- ✅ **Async/Await**: Use async/await for I/O operations (FastAPI)

**Integration Standards**:
- ✅ **HTTP Client Standards**: Use httpx with proper timeout handling
- ✅ **Authentication**: Always include proper auth headers in service calls
- ✅ **Logging**: Structured logging with correlation IDs for all operations
- ✅ **Health Checks**: Implement comprehensive health monitoring

**Testing Requirements**:
- ✅ **Unit Tests**: Test each component in isolation
- ✅ **Integration Tests**: Test service-to-service communication
- ✅ **API Tests**: Validate REST endpoints
- ✅ **Performance Tests**: Validate performance under load

### Daily Sync Checklist (REQUIRED)

**Every 24 hours, agents must:**
1. **Check Last Updated**: Verify this document's last updated date
2. **Review Best Practices**: Ensure current implementation follows standards
3. **Update if Needed**: Add any new best practices or compliance requirements

---

## Continuity Updates

**REQUIRED**: After completing any significant work on this service, agents must update `/dox-admin/continuity/CONTINUITY_MEMORY.md` with:

- What features were added or modified
- Which files were created/modified
- Any architectural considerations
- Dependencies added or changed
- Known issues or limitations
- Best practices compliance status

**CRITICAL**: Always verify this AGENTS.md document is current with latest best practices before proceeding with any development work.

This ensures proper handoff between agents and implementation sessions.

## Contact & Support

**CUSTOMIZE**: Set team information.

**Template placeholder**:
- **Team**: [Team Name from SERVICES_REGISTRY.md]
- **Service Owner**: [Team Lead]
- **Coordination**: Via `/dox-admin/strategy/memory-banks/TEAM_[TEAM_NAME].json`
- **Standards**: `/dox-admin/strategy/standards/`
- **Service Registry**: `/dox-admin/strategy/SERVICES_REGISTRY.md`

---

**Status**: ✅ ACTIVE
**Last Updated**: [DATE_CREATED]
**Version**: 1.0
**Next Sync Check**: [DATE_PLUS_1_DAY] (24-hour requirement)
**Best Practices Compliance**: ✅ Current with 2025 standards
```

**Customization Instructions for Template**:
- Sections marked **CUSTOMIZE** need service-specific customization
- **FIXED** sections are standard across all services
- **Template placeholder** sections show examples to replace
- Always maintain the comprehensive structure (300+ lines)
- Include all references to coordination standards

---

## Task 5: Service-Specific AGENTS.md Customization

**Strategy:** Create master comprehensive template, then customize per service using SERVICES_REGISTRY.md data

**Master Template Structure (based on dox-mcp-server):**
```markdown
# Agent Protocol: [Service Name]

## Objective
[Service purpose from SERVICES_REGISTRY.md]

## Architecture & Key Files
- **[Main application file]**: [Description]
- **[Key directories/files]**: [Descriptions based on service type]

## Core Technologies
[List from SERVICES_REGISTRY.md Technology Stack]

## Multi-Agent Collaboration Protocol
Reference: `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`

## Development Workflow
1. Dependencies management
2. Testing requirements
3. Documentation standards
4. Code quality checks

## Service Integration
[List dependencies and downstream services from registry]

## Continuity Updates
CRITICAL: Update `/dox-admin/continuity/CONTINUITY_MEMORY.md`

## Best Practices & Sync Requirements
Daily sync requirement (24-hour check)

## Contact & Support
Team assignment from SERVICES_REGISTRY.md
```

**Customization Data per Service (from SERVICES_REGISTRY.md):**

### Core Infrastructure Services:
1. **dox-admin**:
   - Purpose: Central administrative hub and specification repository
   - Technologies: Markdown, JSON, Git
   - Key Files: strategy/SERVICES_REGISTRY.md, continuity/CONTINUITY_MEMORY.md
   - Team: Supervisor Agent

2. **dox-core-store**:
   - Purpose: Central database and SharePoint integration
   - Technologies: Python Flask, MSSQL, SQLAlchemy
   - Key Files: app/models/database.py, app/api/v1/endpoints/
   - Team: Infrastructure Team

3. **dox-core-auth**:
   - Purpose: Authentication and authorization with Azure B2C
   - Technologies: Python Flask, Azure B2C, PyJWT
   - Key Files: app/jwt_manager.py, app/services/auth.py
   - Team: Infrastructure Team

4. **dox-core-rec-engine**:
   - Purpose: AI-driven recommendation engine (Phase 4+)
   - Technologies: Python, scikit-learn, TensorFlow
   - Key Files: app/models/recommendations.py, app/analytics/
   - Team: Reserved (Phase 4+)

### Document Services:
5. **dox-tmpl-service**:
   - Purpose: Template CRUD and bundle management
   - Technologies: Python Flask, dox-core-store API
   - Key Files: app/services/templates.py, app/services/bundles.py
   - Team: Document Team

6. **dox-tmpl-field-mapper**:
   - Purpose: Automatic field detection and mapping
   - Technologies: Python Flask, pdftk-java, OpenCV
   - Key Files: app/pdf_analyzer.py, app/field_detector.py
   - Team: Document Team

7. **dox-tmpl-pdf-upload**:
   - Purpose: Template upload workflows (complements pdf-recognizer)
   - Technologies: Python Flask, Azure Storage
   - Key Files: app/services/upload.py, app/services/validation.py
   - Team: Document Team

8. **dox-tmpl-pdf-recognizer** (existing AGENTS.md):
   - Already has AGENTS.md (service-focused pattern)
   - Update to comprehensive pattern

### Signing Services:
9. **dox-esig-service**:
   - Purpose: E-signature integration with AssureSign
   - Technologies: Python Flask, AssureSign API
   - Key Files: app/services/esig_client.py, app/services/envelopes.py
   - Team: Signing Team

10. **dox-esig-webhook-listener**:
    - Purpose: Receives AssureSign webhook events
    - Technologies: Python Flask, Azure Service Bus
    - Key Files: app/webhooks/handlers.py, app/events/processor.py
    - Team: Signing Team

11. **dox-rtns-manual-upload**:
    - Purpose: Manual upload of returned documents
    - Technologies: Python Flask, pyzbar, OpenCV
    - Key Files: app/services/upload.py, app/services/barcode.py
    - Team: Signing Team

12. **dox-rtns-barcode-matcher**:
    - Purpose: Barcode and OCR processing
    - Technologies: Python Flask, Tesseract, OpenCV
    - Key Files: app/services/ocr.py, app/services/matching.py
    - Team: Signing Team

### Activation Services:
13. **dox-actv-service**:
    - Purpose: Complex duplex workflow state machine
    - Technologies: Python Flask, State Machine
    - Key Files: app/workflows/engine.py, app/rules/pricing.py
    - Team: Activation Team

14. **dox-actv-listener**:
    - Purpose: Async activation event receiver
    - Technologies: Python Flask, Message Queue
    - Key Files: app/events/listener.py, app/services/propagation.py
    - Team: Activation Team

### Data Services:
15. **dox-data-etl-service**:
    - Purpose: Purchase data ingestion pipeline
    - Technologies: Python Flask, Apache Airflow
    - Key Files: app/etl/pipelines.py, app/transformations/
    - Team: Data Team

16. **dox-data-distrib-service**:
    - Purpose: Distributor relationship management
    - Technologies: Python Flask, PostgreSQL
    - Key Files: app/services/distributors.py, app/services/pricing.py
    - Team: Data Team

17. **dox-data-aggregation-service**:
    - Purpose: Analytics and reporting
    - Technologies: Python Flask, Redis, Analytics
    - Key Files: app/analytics/kpi.py, app/reports/dashboard.py
    - Team: Data Team

### Automation Services:
18. **dox-auto-workflow-engine**:
    - Purpose: Visual automation builder
    - Technologies: Python Flask, Workflow DSL
    - Key Files: app/workflows/executor.py, app/builder/visual.py
    - Team: Automation Team

19. **dox-auto-lifecycle-service**:
    - Purpose: Contract lifecycle management
    - Technologies: Python Flask, State Machine
    - Key Files: app/lifecycle/contracts.py, app/services/notifications.py
    - Team: Automation Team

### Gateway Application:
20. **dox-gtwy-main**:
    - Purpose: Primary gateway/cockpit application
    - Technologies: Vanilla JavaScript, Python Flask
    - Key Files: static/js/pages/, app/api/integration/
    - Team: Frontend Team

### Support Services:
21. **jules-mcp**:
    - Purpose: Jules MCP server for cost optimization
    - Technologies: FastMCP, Google Jules API
    - Key Files: app/mcp_server.py, app/tools/code_generation.py
    - Team: Support

22. **test-jules**:
    - Purpose: Jules testing framework
    - Technologies: Python, pytest
    - Key Files: tests/integration/, tests/e2e/
    - Team: Support

**Integration Points to Document:**
- All services depend on dox-core-auth (authentication)
- Most services depend on dox-core-store (data)
- Document services integrate with each other
- Signing services have webhook dependencies
- Gateway depends on all backend services
- Data services provide analytics to others

**Customization Approach:**
1. Create master comprehensive template (300+ lines)
2. For each service: replace [placeholders] with service-specific data
3. Ensure all reference `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`
4. Include daily sync requirement and continuity update protocol
5. Set team coordination memory-bank references correctly

---

## Task 6: Continuity Memory Update

**CRITICAL:** After completing all AGENTS.md distribution, update:
- `/dox-admin/continuity/CONTINUITY_MEMORY.md`
- Add new session documenting:
  - HYBRID_IMPLEMENTATION_PLAN.md creation
  - Master AGENTS.md for dox-admin
  - 22 service-specific AGENTS.md files
  - SERVICE_TEMPLATE AGENTS.md template
  - Total files created and locations

---

## Task 7: Final Validation & Success Criteria

### Ultimate Test Check

**If I were the implementation agent with ONLY this planning.md and the codebase, could I implement this EXACTLY as intended with ZERO decisions?**

✅ **HYBRID_IMPLEMENTATION_PLAN.md**:
- Clear section structure with 7 specific parts
- Executive summary requirements defined
- Phase 3A (Local Infrastructure) details from CONTINUITY_MEMORY.md
- Phase 3B (Core Services) roadmap clear
- Phase 3C (Production Architecture) specified
- Timeline & milestones format specified
- Resource requirements defined
- Success criteria measurable

✅ **Master AGENTS.md for dox-admin**:
- Objective clearly defined (central coordination hub)
- Architecture specified (strategy/ folder structure)
- Core technologies listed (Markdown, JSON, Git)
- Key files identified (SERVICES_REGISTRY.md, CONTINUITY_MEMORY.md)
- Reference to MULTI_AGENT_COORDINATION.md included
- Continuity update requirement specified

✅ **AGENTS.md Template for SERVICE_TEMPLATE**:
- Complete 300+ line comprehensive template provided
- Customization sections clearly marked
- Fixed sections defined
- All references to coordination standards included
- Daily sync requirements specified
- Continuity update protocol included

✅ **Service-Specific AGENTS.md Customization**:
- All 22 services listed with specific data
- Purpose, technologies, key files from SERVICES_REGISTRY.md
- Integration points documented
- Team assignments specified
- Customization approach clear (master template + service data)

✅ **Implementation Order**:
- Clear 5-step sequence defined
- Dependencies between steps understood
- Final continuity update requirement specified

### Quality Checklist Validation

✅ **Every file path specified with exact location**
✅ **Every behavior explicitly described** (comprehensive pattern, daily sync)
✅ **Every edge case covered** (continuity updates, coordination references)
✅ **Every error message specified** (template includes error handling patterns)
✅ **Every validation rule detailed** (customization markers, team assignments)
✅ **Every API endpoint referenced** (from SERVICES_REGISTRY.md)
✅ **Every UI element described** (N/A - this is backend/services focus)
✅ **Cross-repo connections documented** (integration points per service)
✅ **Existing patterns referenced** (dox-mcp-server pattern, MULTI_AGENT_COORDINATION.md)
✅ **No actual code written** (only specifications and templates)
✅ **Junior dev can explain everything** (clear structure, templates, customization data)
✅ **User knows exactly what will be built** (25+ AGENTS.md files with specific content)
✅ **Zero ambiguities remain** (all decisions made, patterns selected)
✅ **Zero decisions left for implementation** (comprehensive template, service data provided)

### Implementation Deliverables Summary

**Total Files to Create/Update:**
1. **HYBRID_IMPLEMENTATION_PLAN.md** (new) - `/dox-admin/continuity/`
2. **dox-admin/AGENTS.md** (new) - `/dox-admin/`
3. **SERVICE_TEMPLATE/docs/AGENTS.md** (new) - `/dox-admin/strategy/SERVICE_TEMPLATE/docs/`
4. **22 Service AGENTS.md files** (new) - One in each repository
5. **CONTINUITY_MEMORY.md update** (update) - `/dox-admin/continuity/`

**Total: 25+ files** fully specified with exact content and structure.

### Ready for Implementation

**All critical questions answered:**
- ✅ HYBRID_IMPLEMENTATION_PLAN.md structure (7 sections specified)
- ✅ AGENTS.md complexity level (comprehensive pattern chosen)
- ✅ Customization approach (master template + service-specific data)
- ✅ Service-specific data sources (SERVICES_REGISTRY.md)
- ✅ Integration requirements (all reference MULTI_AGENT_COORDINATION.md)
- ✅ Continuity update protocol (update CONTINUITY_MEMORY.md)

**No ambiguities remain. Implementation is mechanical.**

---

## Implementation Order

1. **HYBRID_IMPLEMENTATION_PLAN.md** (dox-admin/continuity/)
   - Create comprehensive Phase 3 strategy document
   - Include all 7 sections with detailed content

2. **Master AGENTS.md** (dox-admin/)
   - Create comprehensive protocol for dox-admin coordination hub
   - Focus on governance and memory-bank management

3. **AGENTS.md Template** (dox-admin/strategy/SERVICE_TEMPLATE/docs/)
   - Create 300+ line comprehensive template
   - Include customization instructions and placeholders

4. **Batch Service Distribution** (22 repositories)
   - Create master comprehensive template
   - Customize for each of 22 services using SERVICES_REGISTRY.md data
   - Ensure all reference coordination standards

5. **Continuity Memory Update** (dox-admin/continuity/CONTINUITY_MEMORY.md)
   - Document all files created and their purposes
   - Update executive summary and implementation status
   - Record session completion for future handoff

**Success**: Implementation agent can proceed without any further questions or decisions.

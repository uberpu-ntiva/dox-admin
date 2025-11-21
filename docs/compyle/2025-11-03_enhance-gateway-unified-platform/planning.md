# Workflow Rules Coordination - Phase 2 Implementation Plan

## Overview

Implement a hybrid workflow rules engine for the 20-service document management platform that combines centralized orchestration with embedded service-level workflows. This unified system will coordinate document processing workflows (upload → OCR → matching → validation) and cross-service orchestration (authentication → storage → notifications), integrating seamlessly with existing governance infrastructure while enabling Week 2 critical tasks to execute in parallel.

**Architecture**: Hybrid model with:
- **Centralized Orchestration Service** (dox-workflow-orchestrator) - Manages cross-service workflows, coordination, and state
- **Embedded Workflow Library** (dox-workflow-core) - Reusable package embedded in all services for local workflow execution
- **Memory Bank Integration** - Real-time coordination via existing JSON-based memory banks in dox-admin/strategy/

---

## Phase 2 Critical Path Context

**Current Blocking Issues**:
- T04: Playwright E2E tests failing (dox-tmpl-pdf-recognizer) - MDL file input incompatible
- T09: Documentation incomplete (dox-tmpl-pdf-upload) - blocks integration work
- T05: File validation missing (all upload services) - security critical
- T06: dox-rtns-manual-upload not ported from dox-pact-manual-upload
- T07: 7 teams not onboarded - coordination not activated

**How Workflow Engine Enables**:
- T04/T09: Playwright tests and documentation will use standardized workflow patterns
- T05: File validation rules become centralized in workflow configuration
- T06: Porting process automated via workflow templates
- T07: Team coordination automated via memory bank updates

---

## Part 1: Unified Workflow Engine Architecture

### 1.1 High-Level Design

**Hybrid Architecture Pattern**:
```
Requests from Services
    ↓
Service Embedded Workflow (dox-workflow-core)
    ↓ (delegates complex orchestration)
Centralized Orchestrator (dox-workflow-orchestrator)
    ↓ (updates status via)
Memory Banks (dox-admin/strategy/memory-banks/)
    ↓ (provides coordination context to)
Other Services' Embedded Workflows
```

**Repository: dox-workflow-core** (Embedded Library)

**Purpose**: Reusable workflow library embedded in all services
**Location**: PyPI package (Python); installed as dependency in all services
**Scope**: Local workflow execution, state tracking, error handling
**Size**: Small (~500 LOC), minimal dependencies

**Key Components**:
- `WorkflowRunner` class - Executes workflow rules locally
- `WorkflowState` enum - Tracks workflow progress (pending, running, success, failed, retry)
- `WorkflowRule` class - Defines single workflow rule with conditions and actions
- `RuleRegistry` class - Manages available rules per service
- Error handling and retry logic

**Installation**: Each service adds `dox-workflow-core` to requirements.txt

---

**Repository: dox-workflow-orchestrator** (Centralized Service)

**Purpose**: Coordinates cross-service workflows, manages complex orchestration
**Location**: New microservice (follows SERVICE_TEMPLATE structure)
**Scope**: Complex multi-step workflows spanning services
**Size**: Medium (~1500 LOC), connects all services

**Key Components**:
- `OrchestrationEngine` - Manages workflow orchestration across services
- `WorkflowDAG` (Directed Acyclic Graph) - Models dependencies between workflow steps
- `StateManager` - Persists workflow state (Redis + PostgreSQL)
- `EventPublisher` - Publishes workflow events for real-time updates
- `ServiceConnector` - HTTP calls to service APIs
- `MemoryBankSync` - Updates coordination memory banks

**Endpoints** (Implemented in dox-workflow-orchestrator):
- `POST /api/workflows/start` - Start new workflow
- `GET /api/workflows/{id}` - Get workflow status
- `POST /api/workflows/{id}/pause` - Pause workflow
- `POST /api/workflows/{id}/resume` - Resume workflow
- `DELETE /api/workflows/{id}` - Cancel workflow
- `GET /api/workflows` - List active workflows

**Tech Stack**:
- Framework: Flask (consistent with other services)
- State Storage: Redis (fast state queries) + PostgreSQL (persistence)
- Event System: Redis Pub/Sub for real-time updates
- Async Tasks: Celery for background job processing

---

### 1.2 Workflow Rules Definition

**Format**: YAML-based rules stored in dox-admin/strategy/workflows/

**Rule Structure**:
```
Name: [Descriptive rule name]
Service: [Target service name]
Priority: [high/medium/low]
Trigger: [Event that starts rule]
Conditions: [Prerequisites to execute]
Steps: [Sequential actions]
ErrorHandling: [Retry/skip/escalate policy]
Coordinates: [Cross-service dependencies]
MemoryBankUpdate: [Which memory bank to update]
```

**Trigger Types**:
- `api_request` - HTTP request to service endpoint
- `event` - Event from another service
- `schedule` - Cron-based timing
- `manual` - Human initiation via dashboard
- `cascade` - Triggered by workflow completion elsewhere

**Condition Types**:
- `file_validation` - File meets criteria (size, MIME type, virus scan)
- `service_ready` - Service health check passes
- `user_permission` - User has required authorization
- `rate_limit` - Rate limit not exceeded
- `dependency_ready` - Upstream service completed
- `custom_logic` - Custom Python function

**Step Action Types**:
- `api_call` - Call another service's API
- `data_transform` - Transform data between services
- `store_result` - Save to database
- `publish_event` - Emit event for other services
- `update_memory` - Update memory bank
- `notify_team` - Send notification
- `validate_data` - Run validation rules
- `retry_logic` - Retry with backoff

**Error Handling Policies**:
- `retry` - Automatic retry (3 attempts, exponential backoff)
- `skip_step` - Continue to next step, log warning
- `escalate` - Mark blocking issue in memory bank
- `rollback` - Revert all previous steps
- `manual_intervention` - Set status to waiting_for_human

---

## Part 2: Document Processing Workflows (From Existing Repos)

### 2.1 Workflow: Document Upload Processing (from dox-pact-manual-upload analysis)

**Name**: `process_document_upload`
**Source Services**: dox-tmpl-pdf-upload, dox-pact-manual-upload (to be ported to dox-rtns-manual-upload)
**Target Services**: All upload services
**Complexity**: Multi-step, handles both system and manual documents

**Workflow Steps**:

1. **Step 1: File Validation**
   - Trigger: `POST /api/documents/upload` (HTTP request)
   - Conditions: File received, MIME type in allowed list, user authenticated
   - Action: Call validation API (T05 - File Validation Service)
   - Validates:
     - File size (max 50MB from existing config)
     - MIME type (pdf, png, jpg, jpeg, tiff)
     - Virus scan via ClamAV
     - Rate limiting per user
   - On Success: Continue to Step 2
   - On Failure: Return 400 with specific error message, log to BLOCKING_ISSUES.json

2. **Step 2: File Storage**
   - Trigger: Step 1 success
   - Conditions: Validated file, user authorized
   - Action: Call dox-core-store API
   - Storage Details:
     - Store file in centralized document store
     - Generate unique document_id (UUID)
     - Create metadata record (filename, upload_time, user_id, MIME type)
     - Return storage_path and document_id
   - On Success: Continue to Step 3
   - On Failure: Escalate - update BLOCKING_ISSUES.json with storage failure

3. **Step 3: Document Classification**
   - Trigger: Step 2 success
   - Conditions: File stored, document_id generated
   - Action: Determine document type
   - Logic:
     - If datamatrix code detected (from pdf_utils): **System Document** → Step 4a
     - If no datamatrix: **Manual Document** → Step 4b
   - Route based on classification

4a. **Step 4a: System Document Processing (Datamatrix)**
   - Trigger: Step 3 classifies as system document
   - Conditions: Datamatrix code present and readable
   - Action: Extract batch information
   - Logic (from app.py):
     - Call OCR service to read datamatrix code
     - Extract batch_id and account_id from code
     - Verify batch exists in database
   - On Success: Continue to Step 5a
   - On Failure: Set status to manual_review_required, update memory bank

4b. **Step 4b: Manual Document Processing (Template Matching)**
   - Trigger: Step 3 classifies as manual document
   - Conditions: No datamatrix code
   - Action: Match against known templates
   - Logic (from dox-tmpl-pdf-recognizer):
     - Call template recognition service (dox-tmpl-pdf-recognizer)
     - Score document against templates (70% text + 30% form fields)
     - If match confidence > 0.85: auto-accept
     - If match confidence 0.50-0.85: human review needed
     - If no match: manual template selection required
   - On High Confidence: Continue to Step 5b
   - On Low Confidence: Route to Step 5c (Human Review)

5a. **Step 5a: Extract System Document Fields**
   - Trigger: Step 4a successful classification
   - Conditions: Batch and account confirmed
   - Action: Extract fields using OCR + template
   - Logic:
     - Get template for this document type (from dox-tmpl-service)
     - Use EasyOCR to extract text from document
     - Match OCR results to template fields
     - Store extracted field values
   - On Success: Continue to Step 6
   - On Failure: Mark for manual field verification

5b. **Step 5b: Extract Manual Document Fields**
   - Trigger: Step 4b auto-accepted template match
   - Conditions: Template matched, confidence high
   - Action: Extract fields using matched template
   - Logic: Same as Step 5a but using matched template
   - On Success: Continue to Step 6
   - On Failure: Mark for manual field verification

5c. **Step 5c: Human Review Required**
   - Trigger: Template match confidence low OR user manually selected template
   - Conditions: Document needs human attention
   - Action: Route to multi-agent collaboration dashboard
   - Logic (from dox-tmpl-pdf-recognizer):
     - Display document and template options to human operator
     - Operator selects correct template
     - Operator confirms field extractions
     - System learns from decision
   - On Approval: Continue to Step 6
   - On Rejection: Document marked as unprocessable, escalate

6. **Step 6: Account Association**
   - Trigger: Steps 5a/5b/5c completed successfully
   - Conditions: Document classified and fields extracted
   - Action: Associate document with customer account
   - Logic:
     - For system docs: Account already identified (Step 4a)
     - For manual docs: Extract account number from fields or user input
     - Verify account exists in dox-core-store
   - On Success: Continue to Step 7
   - On Failure: Mark as unmatched account, escalate

7. **Step 7: Workflow Completion & Update Memory Bank**
   - Trigger: Steps 6 completed
   - Conditions: Document fully processed
   - Action: Update status and coordination
   - Logic:
     - Mark document as processed in database
     - Update memory bank: SERVICE_[service].json
     - Update team memory bank: TEAM_[name].json
     - Log to SUPERVISOR.json
     - Publish event: `document_processing_complete`
   - Return: Success response with document_id, extracted_fields, account_id

**Error Handling Strategy**:
- File validation failures: Return immediately with clear error message
- Storage failures: Retry up to 3 times with exponential backoff, then escalate
- OCR failures: Retry once, then route to human review
- Account association failures: Escalate to Signing team (memory bank)

**Memory Bank Updates**:
- SERVICE_[service].json: Increment processed_documents counter
- TEAM_[name].json: Add to team's daily metrics
- BLOCKING_ISSUES.json: If critical failure during processing

---

### 2.2 Workflow: Template Recognition (from dox-tmpl-pdf-recognizer analysis)

**Name**: `recognize_template_from_document`
**Source Service**: dox-tmpl-pdf-recognizer
**Target Services**: Used by document upload workflow, template management
**Complexity**: AI-based recognition, high accuracy required

**Workflow Steps**:

1. **Step 1: PDF Analysis**
   - Trigger: Document submitted for template recognition
   - Conditions: Valid PDF file, supported format
   - Action: Analyze PDF structure
   - Logic (from pdf_utils.py):
     - Extract text content from all pages
     - Identify form fields (text boxes, checkboxes, etc.)
     - Extract images and their positions
     - Build document profile
   - Returns: Structured document representation

2. **Step 2: Template Candidate Selection**
   - Trigger: Step 1 PDF analysis complete
   - Conditions: Document profile created
   - Action: Find potential matching templates
   - Logic:
     - Query dox-tmpl-service for all templates
     - Filter by page count similarity
     - Filter by field count similarity
     - Reduce candidate set to top 10 templates
   - Returns: List of candidate templates sorted by likelihood

3. **Step 3: Scoring & Matching**
   - Trigger: Step 2 candidates selected
   - Conditions: Candidate list available
   - Action: Score document against each candidate
   - Scoring Formula (from existing code):
     - Text Match Score (70% weight):
       - Compare OCR text with template field labels
       - Match percentage based on keyword overlap
     - Form Field Score (30% weight):
       - Compare document fields with template fields
       - Score based on position, size, type similarity
   - Returns: Ranked list of templates with confidence scores

4. **Step 4: Decision Making**
   - Trigger: Step 3 scoring complete
   - Conditions: Ranked template list available
   - Decision Logic:
     - If top score > 0.85: Auto-accept (HIGH confidence)
     - If 0.50 < top score < 0.85: Human review (MEDIUM confidence)
     - If top score < 0.50: Manual selection (LOW confidence)
   - On Auto-accept: Jump to Step 6
   - On Human review: Go to Step 5
   - On Manual selection: Go to Step 5

5. **Step 5: Multi-Agent Collaboration Dashboard**
   - Trigger: Step 4 requires human decision
   - Conditions: Confidence insufficient or manual selection needed
   - Action: Present to human operator via dashboard
   - UI Components (from existing dashboard):
     - Document preview (left side)
     - Template options (right side, ranked by confidence)
     - Matched fields highlighted
     - User can approve top match or select different template
   - Operator Action:
     - Reviews suggested templates
     - Selects best matching template
     - Confirms field mappings
     - System learns from decision
   - Returns: Selected template_id, confirmed fields

6. **Step 6: Create Recognition Profile**
   - Trigger: Steps 4 (auto-accept) or 5 (human approved) complete
   - Conditions: Template selected and confidence established
   - Action: Create and store recognition profile
   - Profile Contents:
     - document_type (template matched)
     - confidence_score (from Step 3 or Step 5)
     - field_mappings (OCR text → template fields)
     - recognition_timestamp
     - approved_by (user_id if human approved)
   - Storage: Save to dox-core-store
   - Returns: recognition_profile_id

7. **Step 7: Update Learning System & Memory Bank**
   - Trigger: Step 6 profile created
   - Conditions: Profile stored successfully
   - Action: Update ML models and coordination
   - Logic:
     - If human approval: Use as training data for future recognition
     - Update template confidence metrics
     - Update SERVICE_dox-tmpl-pdf-recognizer.json
     - Log recognition event to SUPERVISOR.json
   - Returns: Success confirmation

**Confidence Thresholds**:
- > 0.85: High confidence (auto-process)
- 0.50-0.85: Medium confidence (human review)
- < 0.50: Low confidence (manual selection)

**Memory Bank Updates**:
- SERVICE_dox-tmpl-pdf-recognizer.json: Add recognition_event
- TEAM_Document.json: Update recognition_accuracy metrics
- SUPERVISOR.json: Log decision if human intervention

---

### 2.3 Workflow: File Validation (T05 - Core Infrastructure)

**Name**: `validate_file_for_upload`
**Target Services**: All upload services (dox-tmpl-pdf-upload, dox-pact-manual-upload → dox-rtns-manual-upload)
**Complexity**: Critical security workflow, reused everywhere
**Status**: NEW - Created in T05

**Embedded Validation Steps** (in each service):

1. **Step 1: Size Validation**
   - Check: File size <= 50MB (max from config)
   - Return: 400 "File exceeds maximum size of 50MB" if exceeded
   - Performance: Instant, no I/O

2. **Step 2: MIME Type Validation**
   - Check: File extension in ALLOWED_EXTENSIONS
   - Allowed types: pdf, png, jpg, jpeg, tiff, tif
   - Check: MIME type from file header matches extension
   - Return: 400 "Invalid file type. Allowed: PDF, PNG, JPG, TIFF" if mismatch
   - Performance: Instant, header scan only

3. **Step 3: Virus Scanning** (Calls external validation service)
   - Check: Call ClamAV service via API
   - Endpoint: POST /api/validate/scan (dox-validation-service)
   - Request body: file_path, file_hash
   - Response: {scan_result: "clean" | "infected", details: {}}
   - Return: 419 "File failed security scan" if infected
   - Performance: 2-5 seconds per file
   - Async option: Background scan with notification

4. **Step 4: Rate Limiting** (Calls centralized rate limiter)
   - Check: User/account hasn't exceeded upload quota
   - Endpoint: POST /api/validate/rate-check (dox-validation-service)
   - Request body: user_id, time_window (last 24 hours)
   - Limits (configurable via env vars):
     - Per user per day: 100 files
     - Per account per day: 500 files
   - Return: 429 "Upload quota exceeded" if exceeded
   - Performance: Redis lookup, instant

5. **Step 5: Format-Specific Validation**
   - For PDFs:
     - Check: PDF is valid (not corrupted)
     - Check: PDF is readable (not encrypted/password-protected)
     - Action: Try to read first page
     - Return: 400 "PDF file is invalid or corrupted" if fails
   - For Images:
     - Check: Image dimensions within limits (max 4000x4000 pixels)
     - Check: Image not corrupted
     - Return: 400 "Image dimensions exceed limits" if too large

**Validation Rule Registry** (Centralized config in dox-validation-service):
```
validation_rules.yaml:
  file_size_max_mb: 50
  allowed_extensions: [pdf, png, jpg, jpeg, tiff, tif]
  allowed_mimetypes: [application/pdf, image/png, image/jpeg, image/tiff]
  image_max_width: 4000
  image_max_height: 4000
  clamav_enabled: true
  rate_limit_per_user_per_day: 100
  rate_limit_per_account_per_day: 500
  virus_scan_async: false  # true = background scan, false = blocking
```

**Error Message Format** (Consistent across all services):
```json
{
  "error": "Validation failed",
  "details": {
    "type": "file_validation",
    "rule_violated": "file_size",
    "message": "File exceeds maximum size of 50MB",
    "max_allowed": 52428800,
    "provided": 104857600
  },
  "timestamp": "2025-11-02T12:34:56Z"
}
```

**Memory Bank Updates**:
- If virus detected: Log to BLOCKING_ISSUES.json
- Daily metrics: Update SERVICE_[service].json with validation_stats

---

## Part 3: Cross-Service Orchestration Workflows (Phase 2+)

### 3.1 Workflow: Team Coordination & Memory Bank Updates

**Name**: `sync_team_coordination`
**Orchestrator**: Supervisor Agent
**Target**: All 7 teams
**Frequency**: Daily at 9 AM (configurable)
**Status**: NEW - Automated by workflow engine

**Workflow Steps**:

1. **Step 1: Read All Service Status**
   - Action: Query all SERVICE_*.json files
   - Read: 20 services × completion %, assigned agents, current tasks, blockers
   - Aggregate: By team ownership

2. **Step 2: Analyze Dependencies**
   - Action: Check cross-team dependencies
   - Logic:
     - For each service: Check if it blocks other services
     - For each team: Identify external dependencies
     - Build dependency matrix

3. **Step 3: Identify Blockers**
   - Action: Scan BLOCKING_ISSUES.json
   - Logic:
     - List all active blockers
     - Map to teams responsible for resolution
     - Calculate blocker aging (time waiting for resolution)

4. **Step 4: Update Team Memory Banks**
   - Action: Write updates to each TEAM_*.json
   - Update Fields:
     - current_phase
     - sprint_goal (if sprint started)
     - team_blockers (pulled from BLOCKING_ISSUES.json)
     - external_dependencies
     - test_pass_rate
     - deployment_status
   - Atomic writes to prevent conflicts

5. **Step 5: Publish Coordination Summary**
   - Action: Update SUPERVISOR.json with daily summary
   - Contents:
     - timestamp
     - overall_progress_percent
     - blockers_count
     - teams_on_track (bool per team)
     - critical_alerts (list)

6. **Step 6: Emit Events for Teams**
   - Action: Publish Redis events for each team
   - Event types:
     - `team_update_ready` - New coordination data available
     - `blocker_escalation` - Critical blocker needs attention
     - `dependency_ready` - External dependency completed

---

### 3.2 Workflow: Service Integration Testing

**Name**: `test_service_integration`
**Target**: Services ready for integration
**Trigger**: Service deploy event OR manual trigger
**Status**: NEW - Enables T04/T09 validation

**Workflow Steps**:

1. **Step 1: Run Embedded Unit Tests**
   - Service runs local test suite
   - Tests validate service-level functionality
   - Pass/fail recorded in SERVICE_*.json

2. **Step 2: Run E2E Tests**
   - Orchestrator coordinates E2E test execution
   - Tests validate workflows across services
   - For pdf-recognizer (T04): Playwright tests with vanilla HTML input
   - For pdf-upload (T09): Workflow tests with documentation examples

3. **Step 3: Validate API Contracts**
   - Action: Compare service API against API_CONTRACTS.json
   - Check: All expected endpoints present
   - Check: Response schemas match contract
   - Check: No breaking changes introduced

4. **Step 4: Update Test Results**
   - Action: Write to SERVICE_*.json
   - Update: test_coverage %, test_pass_rate, last_test_run

---

## Part 4: Week 2 Critical Tasks Integration

### 4.1 Task T04: Fix Playwright E2E Tests (dox-tmpl-pdf-recognizer)

**Workflow Integration**:
- **Workflow Used**: `recognize_template_from_document` (2.2)
- **Specific Focus**: Step 5 - Multi-Agent Collaboration Dashboard
- **Issue Addressed**: MDL file input incompatible with Playwright
- **Solution**: Replace MDL with vanilla HTML file input

**Implementation in planning.md context**:

**File**: dox-tmpl-pdf-recognizer/templates/upload.html
**Location**: Replace MDL components with vanilla HTML
**Change**:
- Old: Material Design Lite `<mdl-input>` component for file selection
- New: Standard HTML `<input type="file">` element
- Purpose: Playwright can interact with native file inputs

**Playwright Test Updates**:
- Location: dox-tmpl-pdf-recognizer/tests/test_e2e.py
- Update: Test selectors from `mdl-input` to `input[type="file"]`
- Behavior: Same functionality, compatible with Playwright automation
- Success Criteria: All tests pass, file upload workflow still works

**Workflow Engine Role**:
- Embedded workflow library used in tests
- Test validates: File upload → OCR analysis → Template matching flow works
- Memory bank update: SERVICE_dox-tmpl-pdf-recognizer.json updated with test status

**Timeline**: 3-5 days (from existing plan)
**Blocking**: Yes - other frontend tests depend on this

---

### 4.2 Task T09: Complete Documentation (dox-tmpl-pdf-upload)

**Workflow Integration**:
- **Workflow Used**: `process_document_upload` (2.1)
- **Specific Focus**: All 7 steps documented with examples
- **Gap Addressed**: Missing API docs, OpenAPI spec, architecture docs

**Implementation Documentation**:

**File 1**: dox-tmpl-pdf-upload/docs/api.md
**Purpose**: Complete API endpoint documentation
**Content**:
- Endpoint: POST /api/documents/upload
- Request format with example
- Response format with example
- Error responses (400, 401, 403, 429, 500)
- Workflow steps 1-7 from workflow definition
- Rate limiting behavior from Step 4
- File validation rules from validation workflow

**File 2**: dox-tmpl-pdf-upload/docs/workflows.md
**Purpose**: Workflow documentation
**Content**:
- Reference to `process_document_upload` workflow (2.1)
- Links to memory bank updates
- Integration with file validation workflow (2.3)
- Integration with template recognition workflow (2.2)

**File 3**: dox-tmpl-pdf-upload/docs/openapi.yaml
**Purpose**: OpenAPI 3.0 specification
**Content**:
- Generated from workflow definition
- All endpoints from workflow steps
- All error codes documented
- All field validations specified

**File 4**: dox-tmpl-pdf-upload/docs/architecture.md
**Purpose**: System architecture and integration
**Content**:
- Hybrid workflow engine architecture (1.2)
- How this service fits in overall platform
- Dependencies: dox-core-store, dox-tmpl-pdf-recognizer, dox-validation-service
- Data flow: How workflows connect services

**Integration Examples**:
- Example 1: Upload system document with datamatrix
- Example 2: Upload manual document requiring template match
- Example 3: Error handling - virus detected
- Example 4: Error handling - rate limit exceeded

**Workflow Engine Role**:
- Documentation references workflow rules and definitions
- OpenAPI spec generated from workflow definition
- Examples show actual workflow execution paths

**Timeline**: 2-3 days (from existing plan)
**Blocking**: Yes - Phase 2 integration depends on this

---

### 4.3 Task T05: File Validation Infrastructure (All Services)

**Workflow Integration**:
- **Workflow Created**: `validate_file_for_upload` (2.3)
- **Scope**: All upload services
- **Architecture**: Shared validation rules + embedded library

**Implementation Components**:

**Component 1**: dox-workflow-core library (embedded in all services)
**Location**: PyPI package namespace `dox_workflow_core`
**Files**:
- `validation.py`: FileValidator class with 5 validation steps
- `rules.py`: Load validation rules from config
- `exceptions.py`: Validation-specific exceptions

**Component 2**: dox-validation-service (New centralized service)
**Location**: New repository following SERVICE_TEMPLATE
**Key Files**:
- `app/app.py`: Flask API with validation endpoints
- `app/validators.py`: ClamAV integration, rate limiting logic
- `config/validation_rules.yaml`: Centralized rule definitions
- `requirements.txt`: ClamAV client, Redis client

**Component 3**: Integration with Each Service
**Services Updated**:
1. dox-tmpl-pdf-upload
2. dox-tmpl-pdf-recognizer
3. dox-pact-manual-upload
4. dox-rtns-manual-upload (when ported, T06)

**Update for Each Service**:
- Add `dox-workflow-core` to requirements.txt
- In upload endpoint: Call `FileValidator.validate()` before processing
- Pass validation config from environment variables
- Handle validation errors with proper error messages

**Validation Rule Configuration** (Environment Variables):
- VALIDATION_MAX_SIZE_MB=50
- VALIDATION_ALLOWED_TYPES=pdf,png,jpg,jpeg,tiff,tif
- VALIDATION_CLAMAV_ENABLED=true
- VALIDATION_CLAMAV_HOST=clamav-service
- VALIDATION_RATE_LIMIT_DAILY=100
- VALIDATION_IMAGE_MAX_WIDTH=4000
- VALIDATION_IMAGE_MAX_HEIGHT=4000

**Memory Bank Updates**:
- SERVICE_dox-validation-service.json: Track validation stats
- SERVICE_[each-upload-service].json: Track validation failures per service
- BLOCKING_ISSUES.json: Log critical validation failures

**Timeline**: 2-3 days (concurrent with T04/T09)
**Impact**: Security-critical, blocks all upload services

---

### 4.4 Task T06: Port dox-pact-manual-upload to dox-rtns-manual-upload

**Workflow Integration**:
- **Workflow Used**: `process_document_upload` (2.1)
- **Template Applied**: SERVICE_TEMPLATE from dox-admin/strategy/
- **Automation**: Workflow engine automates key porting steps

**Porting Workflow Steps** (Automated):

**Step 1: Repository Structure**
- Action: Apply SERVICE_TEMPLATE structure
- Result: Standardized file layout matching other services

**Step 2: Naming Convention Updates**
- Action: Replace all "pact" references with "rtns"
- Files affected:
  - app/models.py: class names (PactReturn → RtnsReturn)
  - app/app.py: route names, configuration
  - tests: test file names
  - documentation: references

**Step 3: Configuration Alignment**
- Action: Update environment variable naming
- Ports: Changed from 5001 to 5003 (per SERVICE_REGISTRY)
- Database: Update connection strings
- SharePoint: Update endpoint URLs

**Step 4: Governance Compliance**
- Action: Apply frozen standards
- Technology Standards: Confirmed Python/Flask/MSSQL/PostgreSQL
- API Standards: Conform to API_STANDARDS.md
- Multi-Agent Coordination: Add memory bank integration

**Step 5: Integration Point Updates**
- Action: Update service dependencies
- dox-core-auth: Ensure auth middleware matches
- dox-core-store: Ensure storage integration works
- dox-tmpl-service: Ensure template service connection works

**Step 6: Testing**
- Action: Run workflow-based E2E tests
- Validate: Document upload workflow works with new service
- Validate: OCR and template matching work
- Validate: File validation passes (T05)

**Step 7: Registration**
- Action: Update SERVICES_REGISTRY.md
- Add: dox-rtns-manual-upload entry with team assignment
- Update: TEAM_Signing.json with new service
- Create: SERVICE_dox-rtns-manual-upload.json

**Memory Bank Updates**:
- SERVICES_REGISTRY.md: Add new service
- TEAM_Signing.json: Assign service to Signing Team
- SERVICE_dox-rtns-manual-upload.json: Create new tracking file
- SUPERVISOR.json: Log service activation

**Timeline**: 3-5 days
**Dependency**: Depends on T05 (file validation) being complete

---

### 4.5 Task T07: Onboard 7 Teams & Activate Coordination

**Workflow Integration**:
- **Workflow Used**: `sync_team_coordination` (3.1)
- **Automation**: Memory bank sync workflow runs daily

**Team Onboarding Workflow**:

**Step 1: Create Team Plans**
- Location: dox-admin/strategy/planning/team-plans/
- File per team: TEAM_[Name]_PLAN.md
- Contents:
  - Team members and roles
  - Services owned
  - Current phase and timeline
  - Sprint goals
  - Dependencies on other teams

**Step 2: Initialize Memory Banks**
- Location: dox-admin/strategy/memory-banks/
- Create: TEAM_[Name].json for each team
- Schema: Follow MULTI_AGENT_COORDINATION.md structure
- Populate: Team composition, service assignments, initial status

**Step 3: Map Service Dependencies**
- Action: For each team's services, identify external dependencies
- Update: dependencies field in TEAM_*.json
- Example for Signing Team:
  - dox-esig-service depends on dox-core-auth (Infrastructure Team)
  - dox-rtns-manual-upload depends on dox-core-store (Infrastructure Team)
  - dox-rtns-manual-upload depends on dox-tmpl-service (Document Team)

**Step 4: Establish Coordination Protocols**
- Action: Brief each team on multi-agent coordination framework
- Explain: File locking protocol, memory bank updates, git workflow
- Per MULTI_AGENT_COORDINATION.md: Agents use defined lifecycle

**Step 5: Activate Weekly Sync**
- Trigger: Every Monday 9 AM
- Action: Run `sync_team_coordination` workflow
- Coordinator: Supervisor Agent
- Participants: One agent per team
- Topics:
  - Progress on assigned services
  - Blockers and escalations
  - Cross-team dependencies
  - Next week priorities

**Step 6: Set Up Notifications**
- Action: Configure team notification channels
- Via: Redis pub/sub events from orchestration engine
- Events:
  - `blocker_assigned_to_team` - New blocking issue
  - `external_dependency_ready` - Upstream service ready
  - `memory_bank_update` - Team coordination updated

**Step 7: Validate Readiness**
- Action: Confirm all teams can access memory banks
- Test: Each team reads and writes to TEAM_[Name].json
- Result: Log readiness status to SUPERVISOR.json

**7 Teams to Onboard**:
1. **Infrastructure Team**: dox-core-store, dox-core-auth
2. **Document Team**: dox-tmpl-service, dox-tmpl-field-mapper
3. **Signing Team**: dox-esig-service, dox-esig-webhook-listener, dox-rtns-manual-upload (T06)
4. **Activation Team**: dox-actv-service, dox-actv-listener
5. **Data Team**: dox-data-etl-service, dox-data-distrib-service, dox-data-aggregation-service
6. **Frontend Team**: dox-gtwy-main
7. **Automation Team**: dox-auto-workflow-engine, dox-auto-lifecycle-service

**Memory Bank Setup per Team**:
- TEAM_Infrastructure.json: 2 services, authentication focus
- TEAM_Document.json: 2 services, template/field mapping focus
- TEAM_Signing.json: 3 services, e-signature and returns focus
- TEAM_Activation.json: 2 services, workflow activation focus
- TEAM_Data.json: 3 services, data processing focus
- TEAM_Frontend.json: 1 service, UI/API gateway focus
- TEAM_Automation.json: 2 services, automation engine focus

**Timeline**: 2-3 days
**Impact**: Enables parallel Phase 2 execution across teams

---

## Part 5: Implementation Roadmap

### 5.1 Phase 2 Week 2 Execution Timeline

**Day 1 (Monday)**:
- Task: Pull Phase 1 completion branch to main
- Task: Read governance hub documentation
- Parallel Start:
  - T04: Begin Playwright test fixes (pdf-recognizer)
  - T09: Begin documentation (pdf-upload)

**Day 2-3 (Tuesday-Wednesday)**:
- Task: T04 progress - 50% complete (tests identified, MDL replaced)
- Task: T09 progress - 50% complete (API docs drafted)
- Parallel Start:
  - T05: Create dox-workflow-core library
  - T05: Create dox-validation-service
  - T05: Begin integrating into services

**Day 4-5 (Thursday-Friday)**:
- Task: T04 complete - all tests passing
- Task: T09 complete - all documentation updated
- Task: T05 progress - 75% integrated into services
- Parallel Start:
  - T06: Begin porting dox-pact-manual-upload
  - T07: Begin team onboarding

**Week 2 Completion (Following Monday)**:
- Task: T05 complete - all services using validation
- Task: T06 complete - dox-rtns-manual-upload ready
- Task: T07 complete - 7 teams activated and syncing
- Outcome: Week 2 critical path complete, ready for Phase 2 implementation

### 5.2 Cross-Repository Coordination

**Central Hub**: dox-admin/strategy/

**Created in dox-admin**:
```
strategy/
├── workflows/                              [NEW]
│   ├── process_document_upload.yaml       [Defines 2.1]
│   ├── recognize_template.yaml            [Defines 2.2]
│   ├── validate_file.yaml                 [Defines 2.3]
│   ├── sync_team_coordination.yaml        [Defines 3.1]
│   └── test_service_integration.yaml      [Defines 3.2]
├── memory-banks/                          [EXISTING - Enhanced]
│   ├── SUPERVISOR.json                    [Updated with workflow events]
│   ├── TEAM_*.json                        [Updated with T07 onboarding]
│   ├── SERVICE_*.json                     [Updated with workflow metrics]
│   ├── SERVICE_dox-validation-service.json [NEW - T05]
│   ├── SERVICE_dox-rtns-manual-upload.json [NEW - T06]
│   └── WORKFLOW_EXECUTION_LOG.json        [NEW - Tracks running workflows]
└── standards/
    ├── MULTI_AGENT_COORDINATION.md        [EXISTING - Add workflow sections]
    └── WORKFLOW_RULES.md                  [NEW - Document rule syntax]
```

**New Repositories**:
1. **dox-workflow-core** (Python package)
   - Purpose: Embedded workflow library for all services
   - Owner: Infrastructure Team
   - Timeline: Create Week 2 (T05)

2. **dox-workflow-orchestrator** (Microservice)
   - Purpose: Centralized orchestration
   - Owner: Automation Team
   - Timeline: Create Week 2 (T05), enhance Phase 2

3. **dox-validation-service** (Microservice)
   - Purpose: Centralized file validation
   - Owner: Infrastructure Team
   - Timeline: Create Week 2 (T05)

**Services Updated Week 2**:
- dox-tmpl-pdf-recognizer (T04 - Playwright tests)
- dox-tmpl-pdf-upload (T09 - Documentation)
- dox-pact-manual-upload (T06 - Ported to dox-rtns-manual-upload)
- All upload services (T05 - File validation integration)

---

## Part 6: Success Criteria & Validation

### 6.1 Workflow Engine Criteria

✅ **Infrastructure Ready**:
- [ ] dox-workflow-core library created and published to PyPI
- [ ] dox-workflow-orchestrator service deployed and responding
- [ ] dox-validation-service created and validated
- [ ] All 3 YAML workflow definitions created and loadable

✅ **Document Processing Workflows**:
- [ ] `process_document_upload` tested with system documents (datamatrix)
- [ ] `process_document_upload` tested with manual documents (template matching)
- [ ] `recognize_template_from_document` working with Playwright tests (T04)
- [ ] Error handling paths validated for all workflow steps

✅ **Coordination Framework**:
- [ ] Memory bank integration working (reads/writes atomic)
- [ ] `sync_team_coordination` running and updating team memory banks daily
- [ ] Event publishing working via Redis pub/sub
- [ ] All 20 SERVICE_*.json files created and updatable

### 6.2 Week 2 Task Criteria

✅ **T04 Complete** (Playwright E2E Tests):
- [ ] All Playwright tests passing
- [ ] File upload workflow end-to-end validated
- [ ] Tests documented in dox-tmpl-pdf-recognizer/docs/testing.md
- [ ] CI/CD pipeline green

✅ **T09 Complete** (Documentation):
- [ ] API documentation complete with workflow examples
- [ ] OpenAPI specification valid and generated
- [ ] Architecture documentation updated
- [ ] Integration examples for all 3 workflow steps

✅ **T05 Complete** (File Validation):
- [ ] File validation rules centralized in dox-validation-service
- [ ] All 4 upload services using embedded dox-workflow-core library
- [ ] ClamAV integration tested (virus detection)
- [ ] Rate limiting enforced across services

✅ **T06 Complete** (dox-rtns-manual-upload):
- [ ] Repository created and structure matches SERVICE_TEMPLATE
- [ ] All naming conventions updated (pact → rtns)
- [ ] Document processing workflow working with new service
- [ ] Registered in SERVICES_REGISTRY.md

✅ **T07 Complete** (Team Onboarding):
- [ ] All 7 teams have initialized memory banks
- [ ] Team coordination workflow running daily
- [ ] All teams confirmed access to memory banks
- [ ] First team sync meeting completed

### 6.3 Quality Metrics

**Workflow Coverage**:
- All document processing steps have defined rules
- All error paths specified in workflow definitions
- All cross-service dependencies documented

**Code Quality**:
- dox-workflow-core: 100% type hints, 90% test coverage
- dox-workflow-orchestrator: 85% test coverage, async operations tested
- All services updated: No regression in existing functionality

**Documentation**:
- Each workflow defined in YAML with examples
- Each memory bank schema version controlled
- All integration points documented

**Performance**:
- File validation: < 1 second for size/MIME checks
- Virus scanning: < 5 seconds with timeout
- Memory bank sync: < 2 seconds per update
- Document processing: < 30 seconds per document

---

## Appendix: Workflow Rule Syntax (Reference)

**Location**: dox-admin/strategy/standards/WORKFLOW_RULES.md

**YAML Rule Format**:
```yaml
name: [Rule Name]
service: [Service Name]
version: "1.0.0"
description: [What this rule does]
priority: [high|medium|low]

trigger:
  type: [api_request|event|schedule|manual|cascade]
  source: [Service or trigger path]

conditions:
  - type: [file_validation|service_ready|user_permission|rate_limit|dependency_ready|custom_logic]
    check: [Specific condition]

steps:
  - name: [Step Name]
    action: [Action type]
    params:
      key: value
    on_success: [Next step name]
    on_failure: [Error handling strategy]

error_handling:
  file_validation_failure: retry  # or skip_step, escalate, rollback
  storage_failure: escalate
  ocr_failure: retry

memory_bank_updates:
  - file: SERVICE_[name].json
    update: {key: value}
  - file: SUPERVISOR.json
    update: {key: value}
```

---

## Appendix: File Locations Summary

**Governance Hub** (dox-admin/strategy/):
```
├── README.md                                    [Navigation hub]
├── SERVICES_REGISTRY.md                        [All 20 services catalog]
├── PHASE_1_IMPLEMENTATION_COMPLETE.md          [Phase 1 summary]
├── standards/
│   ├── API_STANDARDS.md                       [API design frozen]
│   ├── TECHNOLOGY_STANDARDS.md                [Tech stack frozen]
│   ├── MULTI_AGENT_COORDINATION.md            [Agent coordination]
│   └── WORKFLOW_RULES.md                      [NEW - Workflow syntax]
├── workflows/                                  [NEW - Workflow definitions]
│   ├── process_document_upload.yaml
│   ├── recognize_template.yaml
│   ├── validate_file.yaml
│   ├── sync_team_coordination.yaml
│   └── test_service_integration.yaml
├── memory-banks/                               [Coordination files]
│   ├── SUPERVISOR.json
│   ├── TEAM_Infrastructure.json
│   ├── TEAM_Document.json
│   ├── TEAM_Signing.json
│   ├── TEAM_Activation.json
│   ├── TEAM_Data.json
│   ├── TEAM_Frontend.json
│   ├── TEAM_Automation.json
│   ├── SERVICE_*.json                         [20 service tracking files]
│   ├── API_CONTRACTS.json
│   ├── BLOCKING_ISSUES.json
│   ├── DEPLOYMENT_LOG.json
│   ├── TEST_REFRESH_LOG.json
│   └── WORKFLOW_EXECUTION_LOG.json            [NEW]
└── SERVICE_TEMPLATE/                          [Template for new services]
    ├── CHECKLIST.md
    └── [Standard file structure]
```

**New Repositories**:
```
dox-workflow-core/
├── dox_workflow_core/
│   ├── __init__.py
│   ├── runner.py                              [WorkflowRunner class]
│   ├── rules.py                               [RuleRegistry class]
│   ├── validation.py                          [FileValidator class]
│   ├── state.py                               [WorkflowState enum]
│   └── exceptions.py                          [Custom exceptions]
└── requirements.txt

dox-workflow-orchestrator/
├── app/
│   ├── app.py                                 [Flask API]
│   ├── engine.py                              [OrchestrationEngine]
│   ├── state_manager.py                       [StateManager]
│   ├── event_publisher.py                     [EventPublisher]
│   └── service_connector.py                   [ServiceConnector]
├── docs/
│   └── api.md                                 [API documentation]
└── requirements.txt

dox-validation-service/
├── app/
│   ├── app.py                                 [Flask API]
│   ├── validators.py                          [Validation logic]
│   └── clamav_client.py                       [ClamAV integration]
├── config/
│   └── validation_rules.yaml                  [Rule definitions]
└── requirements.txt
```

---

**Document Status**: ✅ READY FOR REVIEW
**Scope**: Workflow rules coordination + Week 2 critical path integration
**Next Step**: Implementation phase - agents execute per this specification

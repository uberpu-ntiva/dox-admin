# Workflow Rules Standard (Frozen)

**Phase 1 Completion**: This standard defines the workflow rules syntax and patterns for the unified workflow engine. All workflow definitions must follow this standard.

---

## Overview

Workflow rules coordinate document processing and cross-service orchestration across the 20-service platform. Rules are defined in YAML and executed by:
- **Embedded Workflows** (dox-workflow-core) - Local execution within each service
- **Centralized Orchestration** (dox-workflow-orchestrator) - Cross-service coordination

---

## Rule Definition Structure

All workflow rules follow this YAML structure:

```yaml
name: [Descriptive rule name]
service: [Target service name]
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
  [error_type]: [retry|skip_step|escalate|rollback]

memory_bank_updates:
  - file: SERVICE_[name].json
    update: {key: value}
  - file: SUPERVISOR.json
    update: {key: value}
```

---

## Trigger Types

### api_request
- Triggered by HTTP request to service endpoint
- Common for upload workflows
- Synchronous by default

### event
- Triggered by event from another service
- Asynchronous
- Useful for cascade workflows

### schedule
- Triggered by cron-based timing
- For periodic synchronization or cleanup
- Example: Daily team coordination sync

### manual
- Triggered by human initiation via dashboard
- Used for workflows requiring explicit approval
- Example: Template selection after low-confidence match

### cascade
- Triggered by completion of another workflow
- Creates workflow chains across services
- Example: After document uploaded, trigger recognition

---

## Condition Types

### file_validation
- Validates file meets criteria before processing
- Checks: size, MIME type, virus scan, format integrity
- Example:
  ```yaml
  conditions:
    - type: file_validation
      check: "file_size <= 50MB && mime_type in allowed_types"
  ```

### service_ready
- Service health check passes
- Ensures service is available before delegating work
- Example:
  ```yaml
  conditions:
    - type: service_ready
      check: "dox-core-store health == healthy"
  ```

### user_permission
- User has required authorization
- Check against user roles or permissions
- Example:
  ```yaml
  conditions:
    - type: user_permission
      check: "user_role in [admin, reviewer]"
  ```

### rate_limit
- Rate limit not exceeded
- Per-user or per-account quotas
- Example:
  ```yaml
  conditions:
    - type: rate_limit
      check: "user_uploads_today < 100 && account_uploads_today < 500"
  ```

### dependency_ready
- Upstream service or task completed
- Ensures proper workflow sequencing
- Example:
  ```yaml
  conditions:
    - type: dependency_ready
      check: "document_storage_complete && file_validated"
  ```

### custom_logic
- Custom Python function for complex validation
- Implemented in service-specific logic
- Example:
  ```yaml
  conditions:
    - type: custom_logic
      check: "custom_validators.validate_document_type(doc)"
  ```

---

## Step Action Types

### api_call
- Call another service's API
- Synchronous HTTP request
- Example:
  ```yaml
  - name: Store Document
    action: api_call
    params:
      service: dox-core-store
      method: POST
      endpoint: /api/documents
      body: {filename, file_hash, user_id}
    on_success: Extract Fields
    on_failure: escalate
  ```

### data_transform
- Transform data between services
- Map fields from one format to another
- Example:
  ```yaml
  - name: Transform OCR Results
    action: data_transform
    params:
      source: ocr_output
      mappings: {raw_text: extracted_fields}
  ```

### store_result
- Save result to local database
- Persist workflow state
- Example:
  ```yaml
  - name: Save Document Metadata
    action: store_result
    params:
      table: documents
      data: {document_id, extracted_fields, confidence_score}
  ```

### publish_event
- Emit event for other services to react to
- Asynchronous notification
- Example:
  ```yaml
  - name: Notify Recognition Complete
    action: publish_event
    params:
      event: document_recognition_complete
      data: {document_id, template_matched}
  ```

### update_memory
- Update memory bank for team coordination
- Critical for cross-team visibility
- Example:
  ```yaml
  - name: Update Service Status
    action: update_memory
    params:
      file: SERVICE_dox-tmpl-pdf-upload.json
      update: {last_document_id, processed_count, status}
  ```

### notify_team
- Send notification to team
- Via email, Slack, or dashboard
- Example:
  ```yaml
  - name: Notify Blocking Issue
    action: notify_team
    params:
      team: Document
      subject: Manual Template Selection Required
      message: Document {id} requires manual review
  ```

### validate_data
- Run validation rules on data
- Ensure data quality
- Example:
  ```yaml
  - name: Validate Extracted Fields
    action: validate_data
    params:
      schema: template_field_schema
      data: extracted_fields
  ```

### retry_logic
- Retry with exponential backoff
- Configurable retry attempts
- Example:
  ```yaml
  - name: Retry File Validation
    action: retry_logic
    params:
      attempts: 3
      backoff: exponential
      base_delay_ms: 100
  ```

---

## Error Handling Policies

### retry
- Automatic retry with backoff
- Default: 3 attempts, exponential backoff (100ms, 300ms, 900ms)
- Use for transient errors (network timeouts)
- Example:
  ```yaml
  error_handling:
    api_timeout: retry
    service_unavailable: retry
  ```

### skip_step
- Skip current step, continue to next
- Log warning for audit trail
- Use when step is optional
- Example:
  ```yaml
  error_handling:
    optional_validation_failed: skip_step
  ```

### escalate
- Mark as blocking issue in memory bank
- Requires manual intervention
- Stops workflow, no automatic retry
- Example:
  ```yaml
  error_handling:
    storage_failure: escalate
    account_not_found: escalate
  ```

### rollback
- Revert all previous steps
- Restore to pre-workflow state
- Use for critical failures
- Example:
  ```yaml
  error_handling:
    database_constraint_violation: rollback
  ```

### manual_intervention
- Set workflow status to waiting_for_human
- System paused, awaiting user decision
- Example:
  ```yaml
  error_handling:
    low_confidence_match: manual_intervention
  ```

---

## Memory Bank Updates

All workflows update memory banks for coordination visibility.

### SERVICE_*.json Updates
- Location: dox-admin/strategy/memory-banks/SERVICE_[service_name].json
- Fields: processed_documents, validation_stats, last_document_id, status
- Frequency: After each workflow step
- Purpose: Individual service tracking

### TEAM_*.json Updates
- Location: dox-admin/strategy/memory-banks/TEAM_[team_name].json
- Fields: team_blockers, external_dependencies, test_pass_rate, deployment_status
- Frequency: Daily during sync_team_coordination
- Purpose: Cross-team visibility

### SUPERVISOR.json Updates
- Location: dox-admin/strategy/memory-banks/SUPERVISOR.json
- Fields: overall_progress_percent, blockers_count, teams_on_track, critical_alerts
- Frequency: After all workflows execute
- Purpose: Master coordination tracking

### BLOCKING_ISSUES.json Updates
- Location: dox-admin/strategy/memory-banks/BLOCKING_ISSUES.json
- Entry: Automatically created on escalate error
- Fields: issue_id, severity, service, description, timestamp, assigned_team
- Purpose: Cross-team issue tracking

### WORKFLOW_EXECUTION_LOG.json Updates
- Location: dox-admin/strategy/memory-banks/WORKFLOW_EXECUTION_LOG.json
- Entry: Every workflow execution logged
- Fields: workflow_id, name, start_time, end_time, status, steps_executed
- Purpose: Audit trail and performance tracking

---

## Workflow State Enum

All workflows track state through defined phases:

- **pending**: Workflow created, waiting to start
- **running**: Workflow steps executing
- **success**: All steps completed successfully
- **failed**: Workflow stopped due to error
- **retry**: Currently retrying after failure
- **waiting_for_human**: Paused, awaiting manual intervention
- **escalated**: Marked as blocking issue, requires supervisor action
- **cancelled**: Manually cancelled by operator

---

## Workflow Name Convention

Workflow names use snake_case pattern:
- `process_document_upload` - Main document processing
- `recognize_template_from_document` - Template recognition
- `validate_file_for_upload` - File validation
- `sync_team_coordination` - Team sync
- `test_service_integration` - Integration testing

---

## Validation Rules Example

From the frozen standards, all file validation follows:
```yaml
validation_rules:
  file_size_max_mb: 50
  allowed_extensions: [pdf, png, jpg, jpeg, tiff, tif]
  allowed_mimetypes: [application/pdf, image/png, image/jpeg, image/tiff]
  image_max_width: 4000
  image_max_height: 4000
  clamav_enabled: true
  rate_limit_per_user_per_day: 100
  rate_limit_per_account_per_day: 500
  virus_scan_async: false
```

---

## Error Message Format (Standardized)

All workflow errors return consistent format:
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

---

## Integration with Existing Standards

- **API_STANDARDS.md**: All API calls in workflows conform to REST patterns
- **TECHNOLOGY_STANDARDS.md**: Workflows use frozen tech stack (Python/Flask/MSSQL/PostgreSQL)
- **MULTI_AGENT_COORDINATION.md**: Workflow engine integrates with agent lifecycle
- **DEPLOYMENT_STANDARDS.md**: Workflows deployed following Docker and config management

---

## Workflow Engine Repositories

### dox-workflow-core (Embedded Library)
- Executes workflow rules locally within services
- ~500 LOC, minimal dependencies
- Components: WorkflowRunner, WorkflowRule, RuleRegistry, WorkflowState, FileValidator

### dox-workflow-orchestrator (Centralized Service)
- Coordinates complex multi-service workflows
- ~1500 LOC, connects all services
- Components: OrchestrationEngine, WorkflowDAG, StateManager, EventPublisher

### dox-validation-service (Shared Validation)
- Centralized file validation rules and ClamAV integration
- Endpoints: /api/validate/file, /api/validate/scan, /api/validate/rate-check

---

**Status**: Frozen Standard
**Version**: 1.0.0
**Last Updated**: Phase 1 Completion
**Next Review**: After Week 2 critical path completion

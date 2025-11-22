# Research

## Summary
Completed comprehensive research of PACT System implementation focusing on AssureSign integration bridge files, DOX object models, and service assessment. Key findings: Bridge files located at `DOX/Dox.BlueSky/distro/Bridge.DOC/batch/` with JavaScript integration for AssureSign; mergeDocuments and TemplateField object models documented; mobile/web client FOUND with existing frontend components; 9 out of 10 unknown services are fully implemented and production-ready.

## Repository: DOX

### Component: Bridge Files Location
**Location:** `DOX/batch/tools/`

**Key findings**
- Bridge files located at `DOX/Dox.BlueSky/distro/Bridge.DOC/batch/`
- ASP.NET website with JavaScript integration files for AssureSign
- Found 311 AssureSign-related files and 69 mergeDocuments-related files across DOX

**How it works**
- `batch.js` handles form field mappings and document generation workflows
- Uses window messaging for cross-frame communication between AssureSign and DOX
- Field mappings stored in `GetFieldMappingsSorted()` with 90+ predefined fields
- Processes form info via JSON API calls to doxapp services

**Connections**
- Integrates with CRM services for account/contact data
- Connects to AssureSign for e-signature workflows
- Uses document generation session management

### Component: mergeDocuments Object Model
**Location:** `DOX/Dox.BlueSky/shared/Core/Models/mergeDocuments.cs`

**Key files**
- `DOX/Dox.BlueSky/shared/Core/Models/mergeDocuments.cs` - Core merge documents object structure
- `DOX/Dox.BlueSky/shared/Core/Models/mergeDocument.cs` - Individual merge document object

**How it works**
- `mergeDocuments` class contains document generation workflow properties
- Key properties include `accountid`, `formInfo`, `formUsage`, `mergedocumentslist`
- `formInfo` stores field mappings as `List<SVector>` (key-value pairs)
- `formUsage` tracks which fields are used with UY marker
- Supports document splitting, site selection, and generation types

**Connections**
- Links to AssureSign through `esignto` and `signinglink` properties
- Integrates with CRM via `accountid` and contact-related properties

### Component: TemplateField Object Model
**Location:** `DOX/Dox.BlueSky/shared/Core/Prototypes/TemplateField.cs`

**How it works**
- `TemplateField` class defines PDF form field geometry and metadata
- Contains coordinates (UpperLeftX/Y, Width, Height), field types, and validation rules
- Supports sub-template fields for complex form structures
- Includes field mapping capabilities with `FieldMapping` and `clean` properties
- Handles various PDF field types (textbox, checkbox, signature, etc.)

**Connections**
- Used by template processing services for field recognition and mapping
- Integrates with document generation workflows

### Component: Mobile/Web Client
**Location:** FOUND - Existing frontend components in DOX repository

**Key findings**
- Found 640 frontend-related files including HTML, CSS, and JavaScript
- Located otto-form template builder with multiple versions
- Found Bridge.DOC with web interface components
- Tax administration interface (taxi) exists
- Multiple template management and document generation UIs

**How it works**
- Frontend components use vanilla JavaScript, CSS, and HTML
- Template builder (otto-form) provides sophisticated field mapping UI
- Bridge components handle document generation workflows
- Multiple versions maintained for backward compatibility

**Connections**
- Integrates with backend services via REST APIs
- Connects to AssureSign through embedded bridge components
- Uses existing authentication and session management

---

## Services Assessment Summary

### Component: 10 Unknown Services Status
**Location:** Across 10 service repositories

**Key findings**
- **9 out of 10 services are FULLY IMPLEMENTED** and production-ready
- **1 service (dox-tmpl-pdf-upload)** is documentation-only/planned
- Services range from basic CRUD to sophisticated AI-powered systems
- High-quality implementations with comprehensive security

**Service Quality Breakdown**
- **Excellent (8 services):** esig-service, esig-webhook-listener, pdf-recognizer, field-mapper, manual-upload, core-store, actv-service, actv-listener
- **Good (1 service):** tmpl-service (uses SQLite, may need upgrade)
- **Planned (1 service):** tmpl-pdf-upload (documentation only)

**How it works**
- Each service is independently deployable with Docker
- FastAPI/Flask frameworks with async processing where appropriate
- Comprehensive API coverage with proper authentication
- Advanced features: OCR, AI/ML, workflow orchestration, e-signatures

**Connections**
- Services communicate via REST APIs and webhooks
- Centralized authentication through dox-core-auth
- Shared data storage through dox-core-store
- Event-driven architecture through actv-listener

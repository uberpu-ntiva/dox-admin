# Research

## Summary

The dox-tmpl-pdf-upload service is currently in PLANNED status with no implementation. It's designed as a Flask-based REST API for PDF template upload and storage, but contains no MCP or FastAPI integration. The dox-mcp-server repository exists but is empty except for a minimal README.

## Repository: dox-tmpl-pdf-upload

### Component: Service Blueprint
**Location:** `dox-tmpl-pdf-upload/` (entire repository)

**Key files**
- `dox-tmpl-pdf-upload/README.md` - Service overview and status (PLANNED)
- `dox-tmpl-pdf-upload/docs/openapi.yaml` - Complete OpenAPI 3.0 specification
- `dox-tmpl-pdf-upload/docs/architecture.md` - Flask-based architecture design
- `dox-tmpl-pdf-upload/docs/api.md` - REST API documentation
- `dox-tmpl-pdf-upload/docs/integration.md` - Service integration patterns

**How it works**
- Service is planned to use Flask 3.0+ framework (not FastAPI)
- Designed for PDF template upload/download with JWT authentication
- Multi-layer validation: size, MIME, virus scanning, PDF structure
- Integrates with dox-core-store (MSSQL), dox-core-auth (JWT), Azure Blob Storage
- No actual implementation exists - only documentation/blueprints

**Connections**
- Planned upstream: dox-core-store, dox-core-auth, ClamAV, Azure Blob Storage
- Planned downstream: dox-gtwy-main, dox-tmpl-service, dox-tmpl-field-mapper

## Repository: dox-mcp-server

### Component: MCP Server Skeleton
**Location:** `dox-mcp-server/README.md`

**Key files**
- `dox-mcp-server/README.md` - Minimal placeholder file

**How it works**
- Repository exists but contains no implementation
- Only has a basic README with service name
- No MCP server implementation present

**Connections**
- No connections documented - implementation missing

## Open Questions

- Should the Flask-based dox-tmpl-pdf-upload be converted to FastAPI?
- How should MCP (Model Context Protocol) integration be implemented?
- Should the MCP server be built from scratch or integrate with existing services?
- What specific MCP tools/prompts are needed for PDF template management?

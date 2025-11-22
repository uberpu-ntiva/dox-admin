# Agent Protocol: [SERVICE_NAME]

## Objective

**CUSTOMIZE**: Replace this section with your service's specific purpose.
This document provides the specific protocols and conventions for working on the [SERVICE_NAME] service. All agents must adhere to these rules.

**Template placeholder**: This service provides [brief description of service purpose] for the Pact Platform.

## Architecture & Key Files

**CUSTOMIZE**: List the key files and directories for your service.

**Template placeholder structure**:
- **`app/main.py`**: Main application entry point - Flask/FastAPI application
- **`app/models/`**: Data models and database schemas
- **`app/api/v1/endpoints/`**: REST API endpoint implementations
- **`app/services/`**: Business logic and service layer
- **`app/core/`**: Core configuration and dependencies
- **`tests/`**: Unit and integration tests
- **`docs/`**: API documentation and architecture
- **`requirements.txt`**: Python dependencies
- **`Dockerfile`**: Container configuration

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

**Every 24 hours, agents must**:
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
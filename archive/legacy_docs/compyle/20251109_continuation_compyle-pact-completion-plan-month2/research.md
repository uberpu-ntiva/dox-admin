# Research

## Summary
PACT is a 20-microservice document management platform with 152 total Python files across services. Research shows mixed implementation status: some services have substantial code (dox-admin: 22 files, dox-mcp-server: 22 files, dox-core-store: 20 files) while others need full implementation. Critical gaps include no deployed infrastructure and missing UI components in the main gateway.

## Repository: DOX
**Location:** `/workspace/cmhnsfugr01i4r7imru8pykld/DOX`

### Component: DOX Database Schemas
**Location:** `/workspace/cmhnsfugr01i4r7imru8pykld/DOX/Dox.BlueSky/db/`

**Key files**
- `WSSContractsUC.sql` - Main database schema with stored procedures
- Schema definitions for [acs], [idm], [sca] databases
- Contract categorization and classification data structures

**How it works**
- Contains existing MSSQL database schemas for accounts, contracts, candidates, document tracking
- Includes complex categorization system for business entities and healthcare facilities
- Provides foundation for unified PACT database schema design

**Connections**
- Base schemas for dox-core-store unified database design
- Reference data for account and contract management in PACT system

## Repository: dox-gtwy-main
**Location:** `/workspace/cmhnsfugr01i4r7imru8pykld/dox-gtwy-main`

**Status:** 4 Python files - API Gateway implemented, missing UI components

**Key files**
- `app.py` (693 lines) - Complete Flask-based API gateway with routing, auth, rate limiting
- `config.py`, `auth_service.py`, `rate_limiter.py` - Supporting modules

**How it works**
- Flask-based API gateway with comprehensive routing to all 20 downstream services
- Implements authentication middleware, rate limiting, circuit breakers, metrics collection
- Routes requests to microservices but lacks web UI for user interaction
- Uses Redis for caching and rate limiting, JWT for authentication

**Connections**
- Central entry point routing to all other services
- Integrates with dox-core-auth for authentication
- Missing: 25+ web pages for user interface, RBAC UI integration

## Repository: dox-core-auth
**Location:** `/workspace/cmhnsfugr01i4r7imru8pykld/dox-core-auth`

**Status:** 11 Python files - Phase 1 complete, needs Phases 2-3 implementation

**Key files**
- `app.py` (804 lines) - Comprehensive Flask authentication service
- `auth_manager.py`, `user_manager.py`, `token_manager.py` - Core auth components
- `config.py` - Service configuration

**How it works**
- Flask-based authentication service with JWT tokens, MFA support, user registration
- Implements endpoints for login, logout, registration, password reset, profile management
- Supports API keys, email verification, multi-factor authentication
- Auth manager handles user authentication with proper validation and security

**Connections**
- Provides authentication for dox-gtwy-main and all other services
- Missing: RBAC role management, OAuth integration, user management UI

## Repository: dox-core-store
**Location:** `/workspace/cmhnsfugr01i4r7imru8pykld/dox-core-store`

**Status:** 20 Python files - Partial implementation (~4071 lines mentioned in plan)

**Key files**
- Database service with CRUD operations for unified schema
- Support for 8 database schemas: [core], [doc], [acs], [idm], [returns], [esig], [workflow], [analytics]

**How it works**
- Centralized database service providing data access to all other microservices
- Implements database operations for all PACT data models
- Handles connection pooling, transaction management, stored procedures

**Connections**
- Database layer for all other services
- Missing: Complete API endpoints, comprehensive CRUD operations, testing

## Repository: dox-tmpl-service
**Location:** `/workspace/cmhnsfugr01i4r7imru8pykld/dox-tmpl-service`

**Status:** 2 Python files - Comprehensive template management system

**Key files**
- `template_service.py` (994 lines) - Full-featured template service with FastAPI
- Comprehensive template processing, field mapping, validation

**How it works**
- FastAPI-based service with Redis caching and S3 storage
- Supports PDF, HTML, JSON template processing with field validation
- Includes barcode/QR code generation, signature handling, document generation
- Template validation engine with field rules and type checking

**Connections**
- Used by dox-gtwy-main for template management
- Integrates with dox-core-store for persistence
- Ready for production integration

## Services with Partial Code (Need Completion)

### dox-pact-manual-upload
**Status:** 12 Python files - Manual document upload service
- Existing OCR functionality, datamatrix reading, SharePoint integration
- Needs porting to dox-rtns-manual-upload and integration with core services

### dox-rtns-manual-upload
**Status:** 12 Python files - Target service for PACT upload functionality
- Prepared to receive ported code from dox-pact-manual-upload
- Missing core functionality implementation

### dox-tmpl-pdf-recognizer
**Status:** 11 Python files - PDF template recognition
- Template recognition algorithms implemented
- Missing: E2E test fixes, production hardening

### dox-actv-service
**Status:** 8 Python files - Activation workflow service (477 lines base)
- Partial activation workflow implementation
- Missing: Complete workflow integration with dox-auto-workflow-engine

### dox-rtns-barcode-matcher
**Status:** 8 Python files - Barcode processing service
- Partial barcode scanning implementation
- Missing: Complete barcode matching logic, integration with returns workflows

### dox-admin
**Status:** 22 Python files - Administrative interface
- Administrative functions implemented
- Missing: Integration with new authentication system, UI components

### dox-mcp-server
**Status:** 22 Python files - MCP server for JULES integration
- Complete MCP implementation with tools and resources
- Ready for production hardening and gateway integration

## Services Needing Full Implementation (Template/Missing Code)

### dox-tmpl-pdf-upload (0 Python files)
- Template PDF upload service - completely missing implementation
- Should integrate with Azure Blob Storage for file storage

### dox-esig-service (1 Python file)
- E-signature service integration with AssureSign
- Only basic structure exists, needs full API implementation

### dox-esig-webhook-listener (1 Python file)
- Webhook listener for AssureSign callbacks
- Only basic structure exists, needs full webhook processing

### Foundation Services (2 Python files each)
- dox-tmpl-field-mapper - Field detection and mapping
- dox-data-etl-service - Data ingestion from external sources
- dox-data-distrib-service - Distributor account management
- dox-auto-lifecycle-service - Document lifecycle management
- dox-core-rec-engine - AI-powered recommendations

### Advanced Services (1 Python file each)
- dox-auto-workflow-engine - Workflow automation builder
- dox-data-aggregation-service - Reporting and analytics
- dox-actv-listener - Activation event listener

## Infrastructure Dependencies Not Deployed
- MSSQL Server: Local deployment needed for unified database schema
- Redis: Local deployment for rate limiting, caching, session management
- Azure Blob Storage: Cloud storage for documents, PDFs, templates
- Network connectivity: VPN/ExpressRoute between local and Azure

## Current Integration Patterns
- Flask/FastAPI microservice architecture with JSON APIs
- Redis for caching and rate limiting across services
- JWT-based authentication through dox-core-auth
- API Gateway pattern in dox-gtwy-main for centralized routing
- S3/Azure Blob storage for file storage
- Database centralization through dox-core-store

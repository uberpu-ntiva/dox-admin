# PACT System - Complete Repository Audit

## All Repositories (24 total)

### 1. DOX (Main Legacy Repository)
- Purpose: Original ASP.NET/C# codebase with Bridge.DOC
- Contains: Bridge files, object models, legacy UI components

### 2. dox-admin (Central Administration Controller) ⭐
- Purpose: **Central administrative controller + memory/direction hub**
- Main file: app.py
- Serves: Admin interfaces, controls backend administration

### 3. dox-gtwy-main (API Gateway)
- Purpose: Flask API gateway - routes requests to 22 microservices
- Main file: app.py
- Serves: Static HTML from /public, proxies API calls

### Core Services (2)
4. **dox-core-auth** - Authentication/OAuth2 service
5. **dox-core-store** - Document storage service
6. **dox-core-rec-engine** - Recognition engine

### Workflow & Automation (5)
7. **dox-auto-workflow-engine** - Workflow automation engine
8. **dox-auto-lifecycle-service** - Document lifecycle management
9. **dox-actv-service** - Activation service
10. **dox-actv-listener** - Activation event listener
11. **dox-batch-assembly** - Batch document assembly

### Template & Field Services (4)
12. **dox-tmpl-service** - Template management
13. **dox-tmpl-field-mapper** - Field mapping service
14. **dox-tmpl-pdf-recognizer** - PDF recognition
15. **dox-tmpl-pdf-upload** - Template PDF upload

### Document Processing (3)
16. **dox-pact-manual-upload** - PACT manual document upload
17. **dox-rtns-manual-upload** - Returns manual upload
18. **dox-rtns-barcode-matcher** - Barcode matching service

### E-Signature (2)
19. **dox-esig-service** - E-signature service (AssureSign)
20. **dox-esig-webhook-listener** - E-signature webhook handler

### Data Platform (3)
21. **dox-data-etl-service** - ETL operations
22. **dox-data-distrib-service** - Data distribution
23. **dox-data-aggregation-service** - Data aggregation

### Development Tools (2)
24. **dox-mcp-server** - Model Context Protocol server
25. **jules-mcp** - Jules MCP integration
26. **test-jules** - Jules testing

## Duplicate Check

### Potential Duplicates to Investigate:
- ❓ **dox-pact-manual-upload** vs **dox-rtns-manual-upload** - Both manual upload services
- ❓ **dox-tmpl-pdf-upload** vs **dox-pact-manual-upload** - May overlap in PDF upload functionality

## Mocking Code Search Required

Need to search all repositories for:
- Mock data
- Fake/stub implementations
- Development-only code
- TODO comments about mocking
- Commented-out production code

## Architecture Clarity Needed

### Questions:
1. **dox-admin** role: Does it serve HTML interfaces OR just backend admin API?
2. **dox-gtwy-main** role: Should it serve frontend OR just route API calls?
3. **Where should HTML interfaces live?** admin or gateway?

### Current State:
- HTML interfaces currently in: `dox-gtwy-main/public/`
- dox-admin has: app.py with Flask setup
- Gateway has: app.py with Flask + routing

## Production Readiness Checklist

### Must Remove:
- [ ] All mock data generators
- [ ] Stub/fake implementations
- [ ] Development-only endpoints
- [ ] Hardcoded test data

### Must Have:
- [ ] Real database connections
- [ ] OAuth2/Azure B2C configured
- [ ] Redis for caching
- [ ] Service-to-service auth
- [ ] Production logging
- [ ] Error handling
- [ ] Health checks on all services

### Must Test:
- [ ] Single-machine dev setup
- [ ] All services start successfully
- [ ] Frontend connects to real backends
- [ ] End-to-end workflows work

## Next Steps

1. **Clarify Architecture**
   - Define dox-admin vs dox-gtwy-main responsibilities
   - Determine where HTML interfaces should live

2. **Search for Mocking**
   - Grep all repos for mock/fake/stub code
   - Remove or replace with real implementations

3. **Test Production Setup**
   - Create docker-compose for single-machine dev
   - Start all services
   - Verify connectivity

4. **Remove Duplicates**
   - Consolidate or eliminate duplicate upload services
   - Ensure each service has clear, unique purpose

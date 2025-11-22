# Service Setup Checklist

Use this checklist when creating a new Pact Platform service.

## Phase 1: Initialize from Template

- [ ] Copy SERVICE_TEMPLATE/ folder to new service repo
- [ ] Rename folder to [SERVICE-NAME]
- [ ] Update all `[REPLACE_ME]` placeholders
- [ ] Update `[SERVICE-SPECIFIC]` sections

## Phase 2: Root Level Documentation

- [ ] **README.md** - Service overview and quick start
  - [ ] Replace `[SERVICE-NAME]` with actual service name
  - [ ] Replace `[REPO-URL]` with GitHub repository URL
  - [ ] Replace `[Team Name]` with team assignment
  - [ ] Replace `[SERVICE-SPECIFIC TOOLS]` with service-specific requirements
  - [ ] Add primary API endpoints list

- [ ] **AGENTS.md** - Copy from dox-tmpl-pdf-recognizer (standard for all services)
  - [ ] No customization needed - identical across all services

- [ ] **.gitignore** - Standard ignores (already in template)
  - [ ] No customization needed

## Phase 3: Application Code

### Backend (Python Flask)

- [ ] **app/app.py** - Main Flask application
  - [ ] Create Flask app instance with proper config
  - [ ] Add health check endpoint: `GET /health`
  - [ ] Add authentication middleware (from dox-core-auth)
  - [ ] Add error handling and logging
  - [ ] Add your service routes

- [ ] **app/requirements.txt** - Python dependencies
  - [ ] Add Flask and basic dependencies
  - [ ] Add service-specific dependencies
  - [ ] Pin versions for reproducibility

- [ ] **app/models/** (if needed) - Data models
  - [ ] Create SQLAlchemy models (if using database)
  - [ ] Add relationships and indexes

- [ ] **app/routes/** - API route handlers
  - [ ] Organize routes by resource/domain
  - [ ] Follow API_STANDARDS.md patterns
  - [ ] Add input validation
  - [ ] Add proper error handling

- [ ] **app/services/** - Business logic
  - [ ] Create service classes for business logic
  - [ ] Keep routes thin (delegation to services)

### Frontend (Vanilla JavaScript)

- [ ] **app/templates/** - HTML templates
  - [ ] Create base.html template
  - [ ] Create page templates (vanilla HTML only)
  - [ ] No frontend frameworks (React, Vue, Angular, etc.)

- [ ] **app/static/js/** - JavaScript files
  - [ ] Vanilla ES6+ JavaScript only
  - [ ] Keep files organized by feature
  - [ ] Add event handlers
  - [ ] Add API calls

- [ ] **app/static/css/** - Stylesheets
  - [ ] Custom CSS (NO Bootstrap, Tailwind, etc.)
  - [ ] Consider simple CSS reset/framework if needed
  - [ ] Keep styling organized and maintainable

- [ ] **app/static/assets/** - Images and other assets
  - [ ] Add any static assets your service needs

## Phase 4: Testing

- [ ] **tests/unit/** - Unit tests
  - [ ] Create test files matching app structure
  - [ ] Test all business logic functions
  - [ ] Test all routes and endpoints
  - [ ] Target: 80%+ code coverage

- [ ] **tests/integration/** - Integration tests
  - [ ] Test integration with dependencies
  - [ ] Test database operations (if applicable)
  - [ ] Test external API calls

- [ ] **tests/conftest.py** (Backend) or **tests/test-setup.js** (Frontend)
  - [ ] Create test fixtures and setup
  - [ ] Create test databases if needed
  - [ ] Create mocks for external services

- [ ] **tests/e2e/** (Frontend services)
  - [ ] Create Playwright E2E tests
  - [ ] Test complete user workflows
  - [ ] Test cross-browser compatibility if needed

## Phase 5: Documentation

- [ ] **docs/api.md** - Human-readable API documentation
  - [ ] Document all endpoints
  - [ ] Add request/response examples
  - [ ] Document error codes
  - [ ] Add authentication requirements
  - [ ] Use template provided in SERVICE_TEMPLATE/docs/api.md

- [ ] **docs/openapi.yaml** - Machine-readable OpenAPI 3.0 specification
  - [ ] Create from scratch or use Swagger/Insomnia export
  - [ ] Document all paths, methods, parameters
  - [ ] Add schemas for request/response bodies
  - [ ] Add security definitions
  - [ ] Validate YAML syntax

- [ ] **docs/ARCHITECTURE.md** - Design and architecture decisions
  - [ ] Explain service purpose and responsibilities
  - [ ] Show architecture diagrams (Mermaid format)
  - [ ] Document technology choices
  - [ ] Show dependencies (upstream/downstream)
  - [ ] Document major design decisions
  - [ ] Show data flow (if applicable)

- [ ] **docs/SETUP.md** - Development environment setup
  - [ ] Installation instructions
  - [ ] Environment variable configuration
  - [ ] Database setup (if applicable)
  - [ ] Running tests
  - [ ] Troubleshooting common issues

- [ ] **docs/agent-protocol/** - Copy from dox-tmpl-pdf-recognizer
  - [ ] Copy `docs/agent-protocol/README.md` (standard for all services)
  - [ ] No customization needed

- [ ] **docs/diagrams/** (optional) - Architecture diagrams
  - [ ] Create Mermaid diagrams
  - [ ] Add data flow diagrams
  - [ ] Add deployment diagrams

## Phase 6: Deployment Configuration

- [ ] **Dockerfile** - Container definition
  - [ ] Use template as starting point
  - [ ] Multi-stage build for optimization
  - [ ] Non-root user for security
  - [ ] Health check endpoint
  - [ ] Optimize image size

- [ ] **docker-compose.yml** - Local development environment
  - [ ] Define main app service
  - [ ] Add database service if needed
  - [ ] Add Redis/cache if needed
  - [ ] Define volumes for development
  - [ ] Set up networks
  - [ ] Add health checks

- [ ] **Makefile** - Build and task automation
  - [ ] Update `[service-name]` and `[registry]` variables
  - [ ] All targets working (install, test, build, deploy)
  - [ ] Help text accurate
  - [ ] Add custom targets for service-specific tasks

- [ ] **deployments/docker/README.md**
  - [ ] Document Docker build and deployment

- [ ] **deployments/aws/** - AWS deployment configuration
  - [ ] Create CloudFormation template or ECS task definition
  - [ ] Document deployment process
  - [ ] Add scaling configuration

- [ ] **deployments/azure/** - Azure deployment configuration
  - [ ] Create App Service configuration
  - [ ] Document deployment process
  - [ ] Add scaling configuration

## Phase 7: Agent Coordination

- [ ] **.state/** - Ephemeral agent status directory
  - [ ] Create .gitkeep file (already in template)
  - [ ] This directory is auto-populated by agents

- [ ] **memory-banks/** - Long-term agent knowledge
  - [ ] Create .gitkeep file (already in template)
  - [ ] This directory is auto-populated by agents

- [ ] **storage/** - Runtime data storage (git-ignored)
  - [ ] Create .gitkeep file (already in template)
  - [ ] This directory is auto-populated at runtime

## Phase 8: Configuration Files

- [ ] **.env.example** - Environment variables template
  - [ ] List all environment variables
  - [ ] Add descriptions
  - [ ] Include example values
  - [ ] Mark required vs optional

- [ ] **.env** (development only, git-ignored)
  - [ ] Copy from .env.example
  - [ ] Fill in with development values

- [ ] **pyproject.toml** (optional, for Python)
  - [ ] Configure pytest
  - [ ] Configure flake8
  - [ ] Configure black formatting

- [ ] **setup.cfg** (optional, for Python)
  - [ ] Configure development tools
  - [ ] Set max line length
  - [ ] Configure coverage settings

## Phase 9: Git Setup

- [ ] **Initialize Git Repository**
  - [ ] `git init`
  - [ ] Add remote: `git remote add origin [REPO-URL]`

- [ ] **Create Initial Commit**
  - [ ] `git add .`
  - [ ] `git commit -m "feat: Initialize [SERVICE-NAME] service with template"`

- [ ] **Create Feature Branch for Development**
  - [ ] `git checkout -b feature/initial-setup`

## Phase 10: Service Registration

- [ ] **Update SERVICES_REGISTRY.md**
  - [ ] Add service to the appropriate group
  - [ ] Fill in: name, status, phase, team, timeline, type
  - [ ] Add GitHub repository URL
  - [ ] Add dependencies and downstream services
  - [ ] Add memory bank location

- [ ] **Update REPO_MAPPING.md** (if porting existing service)
  - [ ] Document where service came from
  - [ ] Document mapping to Pact architecture
  - [ ] Add porting notes

- [ ] **Create Memory Bank Entry**
  - [ ] Create `memory-banks/SERVICE_[name].json`
  - [ ] Add to `/dox-admin/state/memory-banks/`
  - [ ] Join team's coordination file `TEAM_[name].json`

- [ ] **Join Team Coordination File**
  - [ ] Add service to team's memory bank
  - [ ] Add team members
  - [ ] Set initial status

## Phase 11: Local Development Testing

- [ ] **Run make install**
  - [ ] Dependencies install successfully
  - [ ] Virtual environment created

- [ ] **Run make docker-up**
  - [ ] All services start without errors
  - [ ] Health checks pass

- [ ] **Run make test**
  - [ ] All tests pass
  - [ ] Coverage report generated
  - [ ] Coverage >80%

- [ ] **Run make build**
  - [ ] Docker image builds successfully
  - [ ] No build warnings or errors

- [ ] **Test endpoints manually**
  - [ ] Health check: `curl http://localhost:5000/health`
  - [ ] Sample API calls work
  - [ ] Authentication required for protected endpoints

- [ ] **Check code quality**
  - [ ] Run `make lint` - no errors
  - [ ] Run `make format` - code properly formatted
  - [ ] No unused imports

## Phase 12: Pre-Release Verification

- [ ] **Documentation Complete**
  - [ ] README.md is accurate and complete
  - [ ] API documentation matches implementation
  - [ ] OpenAPI spec is valid (validate with swagger-cli)
  - [ ] ARCHITECTURE.md explains design clearly
  - [ ] All endpoints documented with examples

- [ ] **Code Quality**
  - [ ] Tests passing: `make test`
  - [ ] Coverage >80%: `make coverage`
  - [ ] Linting clean: `make lint`
  - [ ] Code formatted: `make format`
  - [ ] No unused code or imports
  - [ ] Error handling comprehensive

- [ ] **Deployment Ready**
  - [ ] Docker image builds: `make build`
  - [ ] Docker runs without errors
  - [ ] Health check working
  - [ ] Logging configured
  - [ ] Secrets not in code (.env in .gitignore)

- [ ] **Security**
  - [ ] Authentication enforced on all endpoints
  - [ ] Input validation on all endpoints
  - [ ] No credentials in logs
  - [ ] Dependencies up-to-date (pip audit)
  - [ ] No high-severity vulnerabilities

- [ ] **Integration Points**
  - [ ] Service communication patterns documented
  - [ ] Dependencies clearly listed
  - [ ] Error handling for dependent service failures
  - [ ] Timeout handling for external calls
  - [ ] Retry logic implemented (if applicable)

## Phase 13: Release & Registration

- [ ] **Git Final Commit**
  - [ ] All files committed
  - [ ] Commit message: `release(service): [SERVICE-NAME] v1.0.0`
  - [ ] Create git tag: `git tag v1.0.0`
  - [ ] Push to repository

- [ ] **Docker Image Release**
  - [ ] Build final image
  - [ ] Tag with version: `$(REGISTRY)/$(SERVICE_NAME):1.0.0`
  - [ ] Tag with latest: `$(REGISTRY)/$(SERVICE_NAME):latest`
  - [ ] Push to registry: `make push`

- [ ] **Update Central Documentation**
  - [ ] Update `SERVICES_REGISTRY.md` status to "Active"
  - [ ] Update memory banks with release info
  - [ ] Notify dependent teams

- [ ] **Notify Teams**
  - [ ] Slack announcement in #[team-channel]
  - [ ] Update sprint board
  - [ ] Notify downstream teams if this is a dependency

## Verification Checklist (Final)

Before marking service as complete:

- [ ] All files from this checklist created ✓
- [ ] No [REPLACE_ME] placeholders remaining
- [ ] `make test` passes 100%
- [ ] `make build` succeeds
- [ ] `make docker-up` starts all services
- [ ] Health check endpoint responds
- [ ] API documentation complete and accurate
- [ ] README.md has clear quick-start instructions
- [ ] Service registered in SERVICES_REGISTRY.md
- [ ] Team notified and updated
- [ ] Git repository clean and tagged

---

**Status**: [Mark as complete when all items checked]
**Completed By**: [Agent Name]
**Date**: [Date Completed]


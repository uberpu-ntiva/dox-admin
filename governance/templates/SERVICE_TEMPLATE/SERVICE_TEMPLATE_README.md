# SERVICE TEMPLATE: Standard Folder Structure for All Pact Services

This folder contains the **standard boilerplate structure** that all 20 Pact Platform services must follow.

## How to Use This Template

### Step 1: Copy This Entire Folder
```bash
cp -r SERVICE_TEMPLATE/ [SERVICE-NAME]/
cd [SERVICE-NAME]
```

### Step 2: Use the File Creation Checklist
See `CHECKLIST.md` in this folder for the complete list of files to create.

### Step 3: Customize Template Files
Each template file includes `[PLACEHOLDERS]` for service-specific content. Search for `REPLACE_ME` or `[Service-Specific]` comments.

### Step 4: Register Your Service
Update `/dox-admin/state/registry/SERVICES_REGISTRY.md` with your new service entry.

### Step 5: Initialize Memory Banks
Create `memory-banks/SERVICE_[name].json` and join your team's coordination file.

---

## Folder Structure Explanation

```
[SERVICE-NAME]/
│
├── 📋 Root Documentation
│   ├── README.md                    # Service overview, quick start
│   ├── AGENTS.md                    # Agent constraints (MANDATORY READ)
│   └── .gitignore                   # Standard ignores
│
├── 🔧 Application Code
│   ├── app/
│   │   ├── app.py or index.js       # Main entry point (Flask/Node)
│   │   ├── [service-logic]/         # Business logic modules
│   │   └── requirements.txt or package.json
│   ├── tests/
│   │   ├── unit/                    # Unit tests
│   │   ├── integration/             # Integration tests
│   │   └── conftest.py or test-setup.js
│   └── static/ (if frontend)
│       ├── css/
│       ├── js/
│       └── assets/
│
├── 📖 Documentation
│   ├── docs/
│   │   ├── api.md                   # Human-readable API
│   │   ├── openapi.yaml             # Machine-readable spec
│   │   ├── ARCHITECTURE.md          # Design decisions
│   │   ├── SETUP.md                 # Dev environment setup
│   │   └── agent-protocol/
│   │       └── README.md            # Agent protocol (copy from recognizer)
│   └── diagrams/                    # Mermaid/architecture diagrams
│
├── 🐳 Deployment
│   ├── Dockerfile                   # Container definition
│   ├── docker-compose.yml           # Local dev environment
│   ├── Makefile                     # Task automation
│   └── deployments/
│       ├── docker/README.md
│       ├── aws/                     # CloudFormation, ECS configs
│       └── azure/                   # App Service configs
│
├── 🧠 Agent Coordination
│   ├── .state/                      # Ephemeral agent status (git-ignored)
│   │   └── .gitkeep
│   └── memory-banks/                # Long-term agent knowledge
│       └── .gitkeep
│
├── 💾 Runtime Data (git-ignored)
│   └── storage/
│       └── .gitkeep
│
└── 📚 Reference
    └── [Reference: /dox-admin/state/registry/SERVICES_REGISTRY.md]
```

---

## Key Template Files in This Folder

1. **README.md** - Service overview template (customize for your service)
2. **AGENTS.md** - Standard agent constraints (same for all 20 services)
3. **.gitignore** - Standard git ignores
4. **Dockerfile** - Container definition (Python Flask or Node.js template)
5. **docker-compose.yml** - Local dev environment
6. **Makefile** - Build/test automation
7. **docs/api.md** - Human-readable API template
8. **docs/openapi.yaml** - OpenAPI 3.0 specification template
9. **docs/ARCHITECTURE.md** - Design decisions template
10. **docs/SETUP.md** - Development setup guide
11. **CHECKLIST.md** - File creation checklist for teams

---

## File Creation Checklist

Use `CHECKLIST.md` to verify you've created all required files for your service.

---

## Technology Stack

**Enforce these technology choices per your service type:**

**Backend Services:**
- Language: Python 3.10+
- Framework: Flask
- Testing: pytest
- Containerization: Docker
- Package Manager: pip

**Frontend Services:**
- Language: Vanilla JavaScript (NO frameworks like React, Vue, Angular)
- Styling: Vanilla CSS (NO Tailwind, Bootstrap, etc. - use custom CSS or simple framework)
- Testing: Playwright E2E
- Containerization: Docker

**Deployment:**
- Docker for all services
- Azure App Service or AWS ECS Fargate
- Makefile for local development
- docker-compose.yml for local dev environment

---

## Standards to Follow

### API Standards
See `/dox-admin/governance/standards/API_STANDARDS.md` for:
- REST endpoint patterns
- Error response format
- Authentication & RBAC
- Versioning strategy

### Technology Standards
See `/dox-admin/governance/standards/TECHNOLOGY_STANDARDS.md` for:
- Locked technology stack per service
- Approved libraries and tools
- Dependency management

### Deployment Standards
See `/dox-admin/governance/standards/DEPLOYMENT_STANDARDS.md` for:
- Docker best practices
- AWS/Azure deployment patterns
- Configuration management

### Multi-Agent Coordination
See `/dox-admin/governance/standards/MULTI_AGENT_COORDINATION.md` for:
- Agent protocols
- File locking
- Status management
- Git workflow

---

## Important Files to Keep Synchronized

### From dox-tmpl-pdf-recognizer:
- Copy `AGENTS.md` exactly as-is (standard for all services)
- Copy `docs/agent-protocol/README.md` for agent protocol documentation

### From dox-admin/strategy:
- Reference all files in `standards/` folder
- Update `SERVICES_REGISTRY.md` with your service entry
- Add entry to `memory-banks/TEAM_[name].json`

---

## Common Customizations

### For Backend Services:
1. Update `app/app.py` with service-specific Flask routes
2. Create `app/[domain]/` folders for business logic
3. Update `requirements.txt` with service dependencies
4. Create integration tests in `tests/integration/`

### For Frontend Services:
1. Create `static/js/main.js` with vanilla JavaScript logic
2. Create `static/css/` for custom CSS styling
3. Create `app/templates/` for HTML pages
4. Use Playwright for E2E testing in `tests/`

### For Data Services:
1. Create `app/etl/` for ETL logic
2. Create `app/models/` for data models
3. Create migration scripts in `app/migrations/`

---

## Testing Requirements

### Minimum Test Coverage:
- **Backend**: 80%+ unit test coverage
- **Frontend**: Playwright E2E tests for all pages
- **Integration**: Integration tests with dependencies

### Running Tests:
```bash
make test              # Run all tests
make test-unit        # Unit tests only
make test-integration # Integration tests only
make coverage         # Coverage report
```

---

## Documentation Requirements

### Every Service Must Have:
1. **README.md** - Service overview and quick start
2. **docs/api.md** - Human-readable API documentation
3. **docs/openapi.yaml** - Machine-readable OpenAPI specification
4. **docs/ARCHITECTURE.md** - Design decisions and architecture
5. **docs/SETUP.md** - How to set up dev environment
6. **AGENTS.md** - Agent constraints (standard copy)

### Documentation Quality:
- Clear examples for every API endpoint
- Request/response examples
- Error cases documented
- Integration points specified

---

## Deployment Checklist

Before deploying to production, ensure:
- [ ] All tests passing (make test)
- [ ] Docker build successful (make build)
- [ ] API documentation complete
- [ ] Dockerfile optimized (multi-stage build if needed)
- [ ] Environment variables documented
- [ ] Secrets not committed to git (.gitignore)
- [ ] Health check endpoint implemented
- [ ] Logging configured
- [ ] Error handling complete

---

## Questions?

**Refer to:**
1. `/dox-admin/state/registry/SERVICES_REGISTRY.md` - Service specifications
2. `/dox-admin/governance/standards/` - Technology and API standards
3. `/dox-admin/governance/templates/SERVICE_TEMPLATE/CHECKLIST.md` - File checklist
4. `dox-tmpl-pdf-recognizer/` - Working example of a complete service

---

**Template Status**: ✅ READY FOR USE
**Last Updated**: 2025-10-31
**Version**: 1.0


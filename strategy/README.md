# Pact Platform: Strategy & Governance Directory

**Master Planning Hub for all 16+ Microservices**

**Location**: `/dox-admin/strategy/`

**Purpose**: Centralized governance, standards, and coordination for the complete Pact Platform development

---

## Quick Navigation

### 🎯 For New Teams/Developers

**Start here**:
1. Read `SERVICES_REGISTRY.md` - Understand all 20 services
2. Read `SERVICE_TEMPLATE/SERVICE_TEMPLATE_README.md` - Learn standard structure
3. Read `standards/TECHNOLOGY_STANDARDS.md` - Know locked tech stack
4. Read `standards/API_STANDARDS.md` - API patterns
5. Check your team's file in `memory-banks/TEAM_[name].json` - Get assignments

### 📋 Master Documents (START HERE)

| Document | Purpose | Who Uses It |
|----------|---------|-------------|
| **SERVICES_REGISTRY.md** | Master catalog of all 20 services | Everyone |
| **PLANNING_FILES_REGISTRY.md** | Master index of all planning documents | Teams, leads, supervisor |
| **REPO_MAPPING.md** | Map existing repos to Pact services | Core team |
| **SERVICE_TEMPLATE/** | Standard boilerplate for all repos | New service teams |

### 📚 Standards & Governance

| Document | Purpose |
|----------|---------|
| **standards/API_STANDARDS.md** | REST API patterns, security, versioning |
| **standards/TECHNOLOGY_STANDARDS.md** | Locked tech stack (FROZEN) |
| **standards/MULTI_AGENT_COORDINATION.md** | Agent protocol, file locking, memory banks |
| **standards/DEPLOYMENT_STANDARDS.md** | Docker, Azure, AWS deployment patterns |

### 🧠 Agent Coordination (Memory Banks)

| File | Purpose | Updated By |
|------|---------|------------|
| **memory-banks/SUPERVISOR.json** | Master coordination log | Supervisor Agent |
| **memory-banks/TEAM_[name].json** (7 files) | Team status & blockers | Team leads |
| **memory-banks/SERVICE_[name].json** (20 files) | Per-service tracking | Assigned agents |
| **memory-banks/API_CONTRACTS.json** | Versioned API specs | API owners |
| **memory-banks/BLOCKING_ISSUES.json** | Cross-team blockers | Supervisor |
| **memory-banks/TEST_REFRESH_LOG.json** | Test coordination | QA lead |
| **memory-banks/DEPLOYMENT_LOG.json** | Go-live timeline | DevOps |

### 📁 Subfolder Reference

```
/dox-admin/strategy/
│
├── README.md (this file)
├── SERVICES_REGISTRY.md          ⭐ Master service catalog
├── REPO_MAPPING.md               ⭐ Repo mapping & porting guide
│
├── SERVICE_TEMPLATE/             ⭐ Boilerplate for all 20 services
│   ├── SERVICE_TEMPLATE_README.md
│   ├── CHECKLIST.md
│   ├── README.md
│   ├── AGENTS.md
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── Makefile
│   ├── docs/
│   ├── app/
│   ├── tests/
│   └── deployments/
│
├── standards/                    ⭐ Governance standards (FROZEN)
│   ├── API_STANDARDS.md
│   ├── TECHNOLOGY_STANDARDS.md
│   ├── MULTI_AGENT_COORDINATION.md
│   ├── DEPLOYMENT_STANDARDS.md
│   └── [Reserved for others]
│
├── memory-banks/                 ⭐ Agent coordination (dynamic)
│   ├── SUPERVISOR.json
│   ├── TEAM_INFRASTRUCTURE.json
│   ├── TEAM_DOCUMENT.json
│   ├── TEAM_SIGNING.json
│   ├── TEAM_ACTIVATION.json
│   ├── TEAM_DATA.json
│   ├── TEAM_FRONTEND.json
│   ├── TEAM_AUTOMATION.json
│   ├── SERVICE_*.json (20 files per service)
│   ├── API_CONTRACTS.json
│   ├── BLOCKING_ISSUES.json
│   ├── TEST_REFRESH_LOG.json
│   └── DEPLOYMENT_LOG.json
│
├── service-specs/                # Service specifications (from PDFs)
│   ├── dox-core-store_SPEC.md
│   ├── dox-core-auth_SPEC.md
│   └── [18 more...]
│
├── team-coordination/            # Team planning docs
│   └── [To be populated]
│
└── reference/                    # Master PDFs for reference
    ├── Core API Specification.pdf
    ├── Database Schema Overview.pdf
    ├── Pact Full System Specification (v2).pdf
    ├── Pact Gateway_ Page Specification & Recommendations.pdf
    └── Gateway Sitemap.pdf
```

---

## Common Tasks

### I'm Starting a New Service

1. Copy entire `SERVICE_TEMPLATE/` folder
2. Use `CHECKLIST.md` to track file creation
3. Read `standards/API_STANDARDS.md` for REST patterns
4. Read `standards/TECHNOLOGY_STANDARDS.md` for locked tech
5. Create memory bank entry in `memory-banks/SERVICE_[name].json`
6. Register service in `SERVICES_REGISTRY.md`
7. Join your team's file: `TEAM_[name].json`

### I'm the Supervisor Agent

1. Monitor `memory-banks/SUPERVISOR.json`
2. Scan all agent status files in `.state/` directories
3. Check `memory-banks/BLOCKING_ISSUES.json` for blockers
4. Weekly: Review all `TEAM_*.json` files
5. Update `memory-banks/DEPLOYMENT_LOG.json` with milestones

### I'm a Team Lead

1. Read your team's file: `memory-banks/TEAM_[name].json`
2. Coordinate with team members
3. Update service status in `memory-banks/SERVICE_[name].json`
4. Report blockers to `BLOCKING_ISSUES.json`
5. Weekly sync: Check for cross-team dependencies

### I'm an Individual Contributor / Agent

1. Read `standards/MULTI_AGENT_COORDINATION.md` - Understand agent protocol
2. Check your service in `SERVICES_REGISTRY.md` - Know what you're building
3. Create status file in `.state/agent-[id]-status.json`
4. Acquire locks using file locking protocol
5. Update progress in `memory-banks/SERVICE_[name].json`
6. Report blockers to team lead

### I Need to Fix a Bug / Add a Feature

1. Check `SERVICES_REGISTRY.md` - Find your service
2. Check `SERVICE_TEMPLATE/CHECKLIST.md` - Know the structure
3. Read the service's `docs/ARCHITECTURE.md` - Understand design
4. Follow `standards/API_STANDARDS.md` for API changes
5. Follow code patterns from `standards/TECHNOLOGY_STANDARDS.md`
6. Add tests (target 80%+ coverage)
7. Update `docs/api.md` and `docs/openapi.yaml` if API changed
8. Create PR, follow git workflow from `MULTI_AGENT_COORDINATION.md`

---

## Key Principles

### Single Source of Truth

**All governance lives here**. No scattered documentation. If it's not in `/dox-admin/strategy/`, it's not official.

### Technology LOCKED

**No exceptions**: The technology stack is FROZEN per `standards/TECHNOLOGY_STANDARDS.md`. Any deviation requires documented justification and executive approval.

### Multi-Agent Coordination

**Agents work in parallel** on different services. File locking and memory banks prevent conflicts. See `standards/MULTI_AGENT_COORDINATION.md`.

### Standards Enforcement

**All 20 services follow identical patterns**:
- Same API format (API_STANDARDS.md)
- Same technology stack (TECHNOLOGY_STANDARDS.md)
- Same folder structure (SERVICE_TEMPLATE)
- Same deployment process (DEPLOYMENT_STANDARDS.md)

---

## Phase Timeline

### Phase 1: Foundation (Weeks 1-4)
- ✅ Governance documents created (you are here)
- ⏳ Fix Playwright tests (replace MDL)
- ⏳ Implement file validation (backend)
- ⏳ Onboard all 7 teams

### Phase 2: Infrastructure (Weeks 5-16)
- Weeks 5-7: dox-core-store (Infrastructure team)
- Weeks 6-8: dox-core-auth (Infrastructure team)
- Weeks 8-12: dox-tmpl-service, dox-tmpl-field-mapper (Document team)

### Phase 3: Business Services (Weeks 13-32)
- Parallel development by Signing, Activation, Data, Frontend, Automation teams

### Phase 4: Integration & Go-Live (Weeks 25-26)
- Full integration testing
- Production readiness verification
- Go/No-go decision

---

## File Update Schedule

**Synchronized Updates** (to prevent conflicts):

| File | Updated By | Frequency | Time |
|------|-----------|-----------|------|
| SUPERVISOR.json | Supervisor | Daily | 8 AM |
| TEAM_*.json | Team leads | Weekly | Monday 9 AM |
| SERVICE_*.json | Assigned agents | Daily | During work |
| memory-banks/* | Various | Real-time | As needed |
| BLOCKING_ISSUES.json | Supervisor | Daily | 8 AM |
| TEST_REFRESH_LOG.json | QA lead | Weekly | Friday 4 PM |
| DEPLOYMENT_LOG.json | DevOps | Per deployment | As scheduled |

---

## Standards Compliance Checklist

Every service must have:
- [ ] `docs/api.md` - Human-readable API documentation
- [ ] `docs/openapi.yaml` - Machine-readable OpenAPI 3.0 spec
- [ ] `docs/ARCHITECTURE.md` - Design decisions
- [ ] `docs/SETUP.md` - Development setup guide
- [ ] `Dockerfile` - Multi-stage, optimized
- [ ] `docker-compose.yml` - Local dev environment
- [ ] `Makefile` - Automation (`make test`, `make build`, `make deploy`)
- [ ] `README.md` - Service overview and quick start
- [ ] `AGENTS.md` - Agent constraints (copy from recognizer)
- [ ] `CHECKLIST.md` - File creation checklist
- [ ] Tests (target 80%+ coverage)
- [ ] Health check endpoint (`GET /health`)
- [ ] Error handling (follow API_STANDARDS.md format)
- [ ] Logging (JSON structured logging in production)

---

## Resources

**Read These First**:
1. `SERVICES_REGISTRY.md` - Master service list
2. `SERVICE_TEMPLATE/SERVICE_TEMPLATE_README.md` - How to use boilerplate
3. `standards/API_STANDARDS.md` - API patterns
4. `standards/TECHNOLOGY_STANDARDS.md` - Tech stack (FROZEN)

**Reference Often**:
- `standards/MULTI_AGENT_COORDINATION.md` - Agent protocol
- `standards/DEPLOYMENT_STANDARDS.md` - Deployment patterns
- `reference/` - Master PDF specifications

**Keep Updated**:
- `memory-banks/SUPERVISOR.json` - Weekly sync
- `memory-banks/TEAM_[name].json` - Your team status
- `memory-banks/SERVICE_[name].json` - Your service status

---

## Getting Help

**Questions about**:
- **API patterns** → See `standards/API_STANDARDS.md`
- **Technology choices** → See `standards/TECHNOLOGY_STANDARDS.md`
- **Agent coordination** → See `standards/MULTI_AGENT_COORDINATION.md`
- **Deployment** → See `standards/DEPLOYMENT_STANDARDS.md`
- **Service setup** → See `SERVICE_TEMPLATE/CHECKLIST.md`
- **Your specific service** → See `SERVICES_REGISTRY.md` + `memory-banks/SERVICE_[name].json`
- **Your team** → See `memory-banks/TEAM_[name].json`

**Escalate blockers**:
1. Document in `memory-banks/BLOCKING_ISSUES.json`
2. Alert your team lead
3. Alert Supervisor Agent

---

## Status

**Setup Date**: 2025-10-31
**Status**: ✅ ACTIVE & INITIALIZED
**Phase**: 1 (Foundation)
**Sprint**: 1

**Next Steps**:
1. Week 1: Fix Playwright tests, implement file validation
2. Week 2: Onboard Infrastructure team, begin dox-core-store design
3. Week 3: Onboard Document & Signing teams
4. Week 4: Phase 1 complete, full multi-agent coordination active

---

**For questions or issues**, see team lead or Supervisor Agent.

**Last Updated**: 2025-10-31
**Version**: 1.0


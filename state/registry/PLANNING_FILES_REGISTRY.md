# Pact Platform: PLANNING FILES REGISTRY

**Central Registry of All Internal Planning Documents**

**Location**: `/dox-admin/governance/` (Single Source of Truth)

**Last Updated**: 2025-10-31

**Purpose**: Centralize all sprint plans, task backlogs, roadmaps, and project planning documents across all Pact services

---

## Overview

This registry tracks all internal planning files (tasks, sprints, roadmaps, meeting notes) across the platform. Instead of scattered files in each service repo, all planning is centralized here for visibility and coordination.

---

## Planning Files Structure

```
/dox-admin/governance/
├── PLANNING_FILES_REGISTRY.md        ← This file (master index)
├── planning/                         ← All planning documents
│   ├── BACKLOG.md                   ← Cross-team backlog
│   ├── SPRINTS.md                   ← Sprint definitions
│   │
│   ├── service-plans/               ← Per-service planning
│   │   ├── dox-tmpl-pdf-recognizer-PLAN.md
│   │   ├── dox-tmpl-pdf-upload-PLAN.md
│   │   ├── dox-core-store-PLAN.md
│   │   └── [18 more services]
│   │
│   ├── team-plans/                  ← Per-team planning
│   │   ├── TEAM_INFRASTRUCTURE_PLAN.md
│   │   ├── TEAM_DOCUMENT_PLAN.md
│   │   ├── TEAM_SIGNING_PLAN.md
│   │   ├── TEAM_ACTIVATION_PLAN.md
│   │   ├── TEAM_DATA_PLAN.md
│   │   ├── TEAM_FRONTEND_PLAN.md
│   │   └── TEAM_AUTOMATION_PLAN.md
│   │
│   └── archive/                     ← Historical sprint planning
│       ├── sprint_1.md              ← Sprint 1 (multi-agent foundation)
│       ├── sprint_2.md              ← Sprint 2 (TBD)
│       └── [completed sprints]
```

---

## Current Planning Documents (ACTIVE)

### Phase 1: Foundation (Weeks 1-4)

#### Backlog

**Location**: `planning/BACKLOG.md` (to be created)

Current high-priority items:

| Task ID | Title | Priority | Status | Service | Target Week |
|---------|-------|----------|--------|---------|-------------|
| T01 | Formalize Agent Protocol | ✅ | Completed | dox-tmpl-pdf-recognizer | W1 |
| T02 | Implement Dashboard UI | ✅ | Completed | dox-tmpl-pdf-recognizer | W1 |
| T03 | Sprint Planning Documents | ✅ | Completed | dox-tmpl-pdf-recognizer | W1 |
| **T04** | **Fix Playwright E2E Tests** | 🔴 | **To Do** | dox-tmpl-pdf-recognizer | **W1** |
| T05 | Implement File Validation | 🔴 | To Do | All Services | W1-2 |
| T06 | Port dox-pact-manual-upload | 🟡 | Planned | dox-rtns-manual-upload | W2 |
| T07 | Onboard 7 Teams | 🟡 | Planned | Multi | W2-3 |
| T08 | Create Governance Standards | ✅ | Completed | dox-admin | W1 |

### Sprint 1: Multi-Agent Foundation

**Status**: In Progress
**Duration**: Weeks 1-4
**Goal**: Establish infrastructure for multi-agent collaboration

**Key Deliverables**:
- ✅ Agent protocol formalized
- ✅ Dashboard UI implemented
- ✅ Governance standards created
- ⏳ Test suite fixed (HIGH PRIORITY)
- ⏳ File validation implemented
- ⏳ Teams onboarded

**See**: `planning/archive/sprint_1.md`

---

## Service Planning Files (Centralized)

### Currently Operational Services

#### 1. dox-tmpl-pdf-recognizer

**Planning Location**: `planning/service-plans/dox-tmpl-pdf-recognizer-PLAN.md`

**Status**: v1.0.0 (Stable)

**Current Tasks**:
- T04: Fix Playwright E2E tests (HIGH PRIORITY) - `make test` broken
- UI Overlay Feature (medium priority)
- Recognition Profile improvements (medium priority)
- Production deployment optimization (low priority)

**Source**: `/dox-tmpl-pdf-recognizer/docs/tasks.md` → Consolidated here

**Backlog Items**:
- [ ] Fix Playwright TimeoutError on file inputs (MDL interference)
- [ ] Implement SVG template overlay
- [ ] Refine 70/30 scoring algorithm
- [ ] Build ML pipeline for recognition profiles
- [ ] Production deployment (Gunicorn + Nginx)
- [ ] Template management UI

#### 2. dox-tmpl-pdf-upload

**Planning Location**: `planning/service-plans/dox-tmpl-pdf-upload-PLAN.md`

**Status**: v1.0.0 (Minimal Docs)

**Current Tasks**:
- Document API endpoints (missing)
- Create architecture docs (missing)
- Plan integration with dox-core-store

**Backlog Items**:
- [ ] API documentation (docs/api.md)
- [ ] OpenAPI specification
- [ ] Architecture documentation
- [ ] Integration testing with recognizer
- [ ] Error handling standardization

#### 3. dox-admin

**Planning Location**: `planning/service-plans/dox-admin-PLAN.md`

**Status**: Active (Governance Hub)

**Current Tasks**:
- Maintain SERVICES_REGISTRY.md
- Update memory banks
- Coordinate teams
- Monitor blockers

---

## Team Planning Files (Centralized)

### Infrastructure Team

**Location**: `planning/team-plans/TEAM_INFRASTRUCTURE_PLAN.md`

**Responsible For**:
- dox-core-store (Database)
- dox-core-auth (Authentication)

**Phase**: 2 (Infrastructure)
**Timeline**: Weeks 5-8
**Members**: 2 agents

**Key Milestones**:
- Week 5-7: dox-core-store complete (schema, migrations, API)
- Week 6-8: dox-core-auth complete (B2C integration, JWT, RBAC)
- Week 8: Both services production-ready

### Document Team

**Location**: `planning/team-plans/TEAM_DOCUMENT_PLAN.md`

**Responsible For**:
- dox-tmpl-service (Template CRUD)
- dox-tmpl-field-mapper (Field detection)

**Phase**: 2 (Infrastructure)
**Timeline**: Weeks 8-12
**Members**: 2 agents

### Signing Team

**Location**: `planning/team-plans/TEAM_SIGNING_PLAN.md`

**Responsible For**:
- dox-esig-service (E-signature)
- dox-esig-webhook-listener (Webhook receiver)
- dox-rtns-manual-upload (Manual upload - to be ported)
- dox-rtns-barcode-matcher (Barcode processing)

**Phase**: 3 (Business Services)
**Timeline**: Weeks 13-18
**Members**: 2 agents

### [Other Teams]

- **Activation Team** - `planning/team-plans/TEAM_ACTIVATION_PLAN.md`
- **Data Team** - `planning/team-plans/TEAM_DATA_PLAN.md`
- **Frontend Team** - `planning/team-plans/TEAM_FRONTEND_PLAN.md`
- **Automation Team** - `planning/team-plans/TEAM_AUTOMATION_PLAN.md`

---

## Historical Sprint Planning

### Sprint 1: Multi-Agent Foundation

**Location**: `planning/archive/sprint_1.md`

**Duration**: Weeks 1-4

**Status**: In Progress

**Completed Tasks**:
- T01: Agent Protocol (✅)
- T02: Dashboard UI (✅)
- T03: Sprint Planning (✅)
- T08: Governance Standards (✅)

**In Progress**:
- T04: Fix Playwright Tests (⏳ HIGH PRIORITY)

**Backlog**:
- T05: File Validation
- T06: Port dox-pact-manual-upload
- T07: Team Onboarding

**See**: `/dox-tmpl-pdf-recognizer/docs/plans/sprint_1.md` (source, now consolidated)

### Future Sprints

- **Sprint 2** - Infrastructure foundation (dox-core-store, dox-core-auth)
- **Sprint 3-6** - Business services development
- **Sprint 7** - Integration & hardening

---

## How to Use This Registry

### As a Service Team

1. Find your service in `planning/service-plans/`
2. Check current tasks and backlog
3. Update progress regularly
4. Escalate blockers to team lead

### As a Team Lead

1. Find your team in `planning/team-plans/`
2. Review team assignments and timeline
3. Track cross-team dependencies
4. Update memory-banks/ with status

### As the Supervisor Agent

1. Check `BACKLOG.md` for priority items
2. Review `SPRINTS.md` for active sprints
3. Monitor all team plans for blockers
4. Update `planning/archive/` as sprints complete

### As the Planning Coordinator

1. Maintain this registry (updated weekly)
2. Consolidate sprint notes from teams
3. Update service and team planning files
4. Archive completed sprints

---

## Weekly Planning Ritual

**Monday 9 AM**: Supervisor reviews `BACKLOG.md`
**Tuesday 2 PM**: Teams review their `planning/team-plans/` file
**Wednesday 10 AM**: Cross-team sync on dependencies
**Thursday 4 PM**: Update service plans with progress
**Friday 4 PM**: Archive completed sprint, plan next sprint

---

## Integration with Central Coordination

**Linked From**:
- `memory-banks/SUPERVISOR.json` - Links to this registry
- `memory-banks/TEAM_*.json` - Each team file references their plan
- `SERVICES_REGISTRY.md` - Cross-references service plans

**Feeds Into**:
- Sprint scheduling (2-week sprints)
- Team capacity planning
- Dependency management
- Risk tracking (blockers)

---

## Current Priorities (Week 1)

### 🔴 CRITICAL (This Week)

1. **T04: Fix Playwright Tests**
   - Service: dox-tmpl-pdf-recognizer
   - Issue: E2E tests timeout on file inputs (MDL issue)
   - Solution: Replace MDL with vanilla HTML
   - Blocker: Critical for all frontend work

2. **T05: File Validation**
   - Service: All file-upload services
   - Priority: High (security)
   - Timeline: Week 1-2
   - Scope: Backend validation, rate limiting, virus scanning

### 🟡 HIGH (Next Week)

3. **T06: Port dox-pact-manual-upload**
   - To: dox-rtns-manual-upload
   - Timeline: Week 2
   - See: `REPO_MAPPING.md` for detailed porting guide

4. **T07: Onboard Teams**
   - All 7 teams ready to begin
   - Timeline: Week 2-3

---

## Files to Consolidate (From Existing Repos)

**From dox-tmpl-pdf-recognizer**:
- ✅ `/docs/tasks.md` → `planning/service-plans/dox-tmpl-pdf-recognizer-PLAN.md`
- ✅ `/docs/plans/sprint_1.md` → `planning/archive/sprint_1.md`
- ✅ `/docs/research.md` → `planning/dox-tmpl-pdf-recognizer-RESEARCH.md` (optional)

**From dox-pact-manual-upload**:
- ⏳ Any planning files → `planning/service-plans/dox-rtns-manual-upload-PLAN.md`

**From dox-admin**:
- ✅ `strategy/` → Central hub (already set up)

---

## Template for New Planning File

When creating a new service or team plan, use this template:

```markdown
# [Service or Team] Planning

**Location**: `/dox-admin/governance/planning/[service-or-team]-PLAN.md`

**Responsible Party**: [Team name or individual]

**Current Phase**: [Phase name and number]

**Timeline**: Weeks X-Y

## Current Tasks

| Task | Status | Notes |
|------|--------|-------|
| | | |

## Backlog

- [ ] Item 1
- [ ] Item 2

## Dependencies

- Upstream: [what we depend on]
- Downstream: [what depends on us]

## Key Milestones

- Week X: Deliverable
- Week Y: Deliverable

## Blockers

[Any current blockers]
```

---

## Status & Next Steps

**Registry Status**: ✅ Created (2025-10-31)

**Files to Create Next Week**:
- [ ] `planning/BACKLOG.md` - Master backlog
- [ ] `planning/SPRINTS.md` - Sprint definitions
- [ ] `planning/service-plans/*.md` - All 20 service plans
- [ ] `planning/team-plans/*.md` - All 7 team plans
- [ ] `planning/archive/sprint_1.md` - Archive from pdf-recognizer

**Integration Timeline**:
- Week 1: This registry + template
- Week 2: Service and team plans populated
- Week 3: Active planning with teams

---

## Related Documents

**See Also**:
- `SERVICES_REGISTRY.md` - Service catalog
- `memory-banks/SUPERVISOR.json` - Master coordination
- `standards/MULTI_AGENT_COORDINATION.md` - Agent protocol

---

**Owner**: Planning Coordinator / Supervisor Agent
**Status**: ✅ ACTIVE
**Last Updated**: 2025-10-31


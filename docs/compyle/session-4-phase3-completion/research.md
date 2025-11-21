# Research

## Summary

The task is to continue implementation based on Phase 1 & 2 completion (documented in `dox-admin/continuity/CONTINUITY_MEMORY.md`) and the hybrid implementation plan (`dox-admin/continuity/HYBRID_IMPLEMENTATION_PLAN.md`), specifically adding AGENTS.MD files to all repository directories.

**Current State:**
- 4 of 26 repositories have AGENTS.md files (DOX, dox-mcp-server, dox-pact-manual-upload, dox-tmpl-pdf-recognizer)
- 22 repositories missing AGENTS.md (including dox-admin itself)
- No AGENTS.md template exists in dox-admin or SERVICE_TEMPLATE

**Key Resources Found:**
- Comprehensive multi-agent coordination standard: `dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`
- Three AGENTS.md complexity patterns: Basic (32 lines), Service-Focused (35 lines), Comprehensive (319 lines)
- Service registry with all metadata: `dox-admin/strategy/SERVICES_REGISTRY.md`

**Implementation Path:**
1. Create master AGENTS.md in dox-admin (based on dox-mcp-server comprehensive pattern)
2. Distribute customized versions to 22 missing repositories
3. Add template to dox-admin/strategy/SERVICE_TEMPLATE/ for future services

**Next Phase:**
Ready for planning to determine customization level and distribution strategy.

---

## Repository: dox-admin

### Continuity and Planning Documents
**Location:** `dox-admin/continuity/`

**Key files:**
- `dox-admin/continuity/CONTINUITY_MEMORY.md` - Complete Phase 1 & 2 implementation history
- `dox-admin/continuity/HYBRID_IMPLEMENTATION_PLAN.md` - 4-phase hybrid implementation strategy

**How it works:**
- CONTINUITY_MEMORY.md tracks all completed work (Phase 1: Governance, Phase 2: Document services)
- Documents 22 services: 2 fully implemented, 2 partial, 18 placeholders
- Hybrid plan details local infrastructure + web interfaces approach (4-12 weeks)

**Status:**
- Phase 1 & 2 complete
- Next: Phase 3 hybrid implementation starting

### Multi-Agent Coordination Standard
**Location:** `dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`

**Key files:**
- `dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md` - Formal protocol for agent collaboration

**How it works:**
- Defines 7 teams + 1 supervisor structure
- File locking protocol with atomic operations
- Memory banks for coordination (SUPERVISOR.json, TEAM_*.json, SERVICE_*.json)
- Continuity update protocol (REQUIRED after significant work)
- Agent lifecycle: STARTUP → DECLARE → LOCK → WORK → TEST → COMMIT → UPDATE_CONTINUITY → SHUTDOWN

**Connections:**
- Referenced by all service AGENTS.md files
- Defines protocol for `/dox-admin/strategy/memory-banks/` coordination files

---

## AGENTS.md Files Across Repositories

### Current Distribution

**Repositories WITH AGENTS.md (4/26):**
1. `DOX/AGENTS.md` - Basic template with Jules capabilities
2. `dox-mcp-server/AGENTS.md` - Comprehensive service-specific protocol
3. `dox-pact-manual-upload/AGENTS.md` - (not read yet)
4. `dox-tmpl-pdf-recognizer/AGENTS.md` - (reading now)

**Repositories MISSING AGENTS.md (22/26):**
- dox-actv-listener
- dox-actv-service
- dox-admin ⚠️
- dox-auto-lifecycle-service
- dox-auto-workflow-engine
- dox-batch-assembly
- dox-core-auth
- dox-core-rec-engine
- dox-core-store
- dox-data-aggregation-service
- dox-data-distrib-service
- dox-data-etl-service
- dox-esig-service
- dox-esig-webhook-listener
- dox-gtwy-main
- dox-rtns-barcode-matcher
- dox-rtns-manual-upload
- dox-tmpl-field-mapper
- dox-tmpl-pdf-upload
- dox-tmpl-service
- jules-mcp
- test-jules

---

## Repository: DOX

### Component: Basic AGENTS.md Template
**Location:** `DOX/AGENTS.md:1-32`

**Key files:**
- `DOX/AGENTS.md` - Minimal agent protocol template

**How it works:**
- Basic agent capabilities section (memory, collaboration)
- JULES_BEST_PRACTICES section (managed by Jules, auto-updated)
- User-defined rules section (placeholder for project-specific rules)
- Emphasizes single-task-at-a-time, Git coordination

**Pattern:**
- Simplest template: 32 lines
- Generic, not service-specific
- Includes auto-updating best practices section

---

## Repository: dox-mcp-server

### Component: Comprehensive Service Protocol
**Location:** `dox-mcp-server/AGENTS.md:1-319`

**Key files:**
- `dox-mcp-server/AGENTS.md` - Full service-specific protocol (319 lines)

**How it works:**
- Service-specific architecture section (main.py, tools/, prompts/, resources/)
- Core technologies (FastMCP, FastAPI, httpx, Pydantic v2)
- MCP protocol compliance requirements
- Multi-agent coordination (references `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`)
- Development workflow (dependencies, testing, documentation, code quality)
- Service integration patterns (dox-tmpl-pdf-upload, dox-core-auth)
- Best practices with daily sync requirement
- Continuity updates (REQUIRED section)

**Pattern:**
- Most comprehensive: 319 lines
- Service-specific with detailed protocols
- Includes 2025 MCP best practices with external reference links
- Daily sync checklist with web references
- Mandatory continuity update protocol

---

## Repository: dox-tmpl-pdf-recognizer

### Component: Service Protocol with Tool Focus
**Location:** `dox-tmpl-pdf-recognizer/AGENTS.md:1-35`

**Key files:**
- `dox-tmpl-pdf-recognizer/AGENTS.md` - Service protocol focusing on PDF tools

**How it works:**
- Service objective and architecture (app.py, pdf_utils.py, static/, templates/, storage/)
- Core technologies (pdftk-java, poppler-utils, ghostscript)
- Multi-agent collaboration protocol reference (docs/agent-protocol/README.md)
- Development workflow (dependencies, testing, documentation)

**Pattern:**
- Medium complexity: 35 lines
- Tool-focused (PDF processing specifics)
- References local agent-protocol documentation
- Service-specific file structure rules

---

## AGENTS.md Pattern Analysis

### Common Sections Across All Files

1. **Objective/Purpose** - What the service/repo does
2. **Architecture & Key Files** - Critical files and their purposes
3. **Core Technologies** - Tech stack (frozen, no changes without justification)
4. **Multi-Agent Collaboration Protocol** - Reference to coordination standard
5. **Development Workflow** - Dependencies, testing, documentation

### Advanced Sections (dox-mcp-server only)

6. **Service Integration** - How it connects to other services
7. **Error Handling Standards** - Consistent error patterns
8. **Authentication & Security** - Security protocols
9. **Configuration Management** - Environment variables
10. **Health Monitoring** - Health check endpoints
11. **Best Practices & Sync Requirements** - 2025 standards with daily sync
12. **Continuity Updates** - REQUIRED protocol for session handoff

### Key Insights

**Three complexity levels:**
1. **Basic** (DOX): 32 lines, generic template
2. **Service-Focused** (dox-tmpl-pdf-recognizer): 35 lines, tool-specific
3. **Comprehensive** (dox-mcp-server): 319 lines, complete protocol with best practices

**All reference:**
- Multi-agent coordination protocol (either local or `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`)

**Critical requirement:**
- Continuity update protocol (dox-mcp-server example) - MUST update `/dox-admin/continuity/CONTINUITY_MEMORY.md`

---

## Task: Add AGENTS.MD to All Directories

### Source Template Options

**Option 1: Use dox-admin/AGENTS.MD**
- ❌ Does NOT exist yet
- Would need to be created first

**Option 2: Use DOX/AGENTS.md as base**
- ✅ Simple, generic template (32 lines)
- Good for repositories without specific protocols

**Option 3: Use dox-mcp-server/AGENTS.md as reference**
- ✅ Comprehensive protocol (319 lines)
- Service-specific sections need customization

**Option 4: Create template in dox-admin/strategy/SERVICE_TEMPLATE/**
- ❌ No AGENTS.md template exists in SERVICE_TEMPLATE/docs/
- Only has api.md template

### Recommended Approach

1. **Create master AGENTS.md in dox-admin/** (doesn't exist)
   - Based on comprehensive dox-mcp-server pattern
   - Generic enough for all services
   - References `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`

2. **Distribute to 22 missing repositories**
   - Customize service-specific sections (objective, architecture, core technologies)
   - Keep standard sections (multi-agent protocol, development workflow, continuity)

3. **Update dox-admin/strategy/SERVICE_TEMPLATE/**
   - Add AGENTS.md template for future services

---

## Additional Context

### Service Registry Information
**Location:** `dox-admin/strategy/SERVICES_REGISTRY.md`

**Contains:**
- Complete catalog of all 22 services
- Service dependencies and relationships
- Team assignments (7 teams: Infrastructure, Document, Signing, Activation, Data, Frontend, Automation)
- Technology stack per service
- API contracts and integration points

**Useful for:**
- Customizing AGENTS.md objective sections
- Identifying service-specific technologies
- Understanding service dependencies for integration sections

---

## Open Questions

1. Should dox-admin/AGENTS.MD be created first, or should we use an existing template?
2. What level of customization per service (basic vs comprehensive)?
3. Should jules-mcp and test-jules get AGENTS.md files (non-dox repos)?
4. Should AGENTS.md be added to dox-admin/strategy/SERVICE_TEMPLATE/ for future consistency?

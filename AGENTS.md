# Agent Protocol: dox-admin

## Objective

This document provides the specific protocols and conventions for working on the dox-admin service. All agents must adhere to these rules.

**Service Purpose**: Central coordination hub and specification repository for the Pact Platform ecosystem. This service governs all other services through standards, templates, memory-banks coordination, and continuity tracking.

**Primary Functions**:
- Maintain governance standards and service registry
- Coordinate multi-agent collaboration through memory-banks
- Track implementation continuity and session handoffs
- Provide templates and patterns for all services
- Manage strategic planning and roadmap execution

## Architecture & Key Files

**`strategy/SERVICES_REGISTRY.md`** - Master catalog of all 22 services with dependencies, technology stacks, and team assignments. This is the single source of truth for service metadata.

**`strategy/standards/`** - Frozen governance standards (no deviations allowed):
- `MULTI_AGENT_COORDINATION.md` - Formal protocol for agent collaboration
- `API_STANDARDS.md` - REST patterns and security requirements
- `TECHNOLOGY_STANDARDS.md` - Locked technology stack decisions
- `DEPLOYMENT_STANDARDS.md` - Deployment patterns and procedures

**`memory-banks/`** - Real-time coordination infrastructure (12+ JSON files):
- `SUPERVISOR.json` - Master coordination and oversight
- `TEAM_*.json` - Team-specific coordination (7 teams)
- `API_CONTRACTS.json` - Service API specifications
- `BLOCKING_ISSUES.json` - Critical blocker tracking
- Service-specific memory banks for inter-service coordination

**`continuity/`** - Implementation tracking and session handoff:
- `CONTINUITY_MEMORY.md` - Complete implementation history and current state
- `HYBRID_IMPLEMENTATION_PLAN.md` - Phase 3 strategy and roadmap

**`planning/`** - Centralized task management and strategic planning:
- `PLANNING_FILES_REGISTRY.md` - Master index of all planning documents
- Service-specific plans (20 templates ready)
- Team plans (7 templates ready)
- Archive structure for sprint planning

**`SERVICE_TEMPLATE/`** - Complete boilerplate for creating new services (13-phase checklist)

## Core Technologies

**Documentation Standards**:
- Markdown for all governance and planning documents
- JSON for memory-banks coordination data
- Structured formatting with consistent headers and sections

**Coordination Infrastructure**:
- File-based locking protocol for agent collaboration
- JSON memory-banks for real-time coordination
- Git-based version control for all governance documents

**Reference Management**:
- Cross-document linking with absolute paths (`/dox-admin/strategy/`)
- Standardized file naming conventions
- Hierarchical organization with clear navigation

**Validation Tools**:
- Markdown linting for consistency
- JSON schema validation for memory-banks
- Link checking for reference integrity

## Multi-Agent Collaboration Protocol

**CRITICAL**: All agents MUST read and adhere to the full protocol documented in `/dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md` before taking any action.

**Key Protocols for dox-admin**:

**File Locking**:
- Always check and update memory-banks/SUPERVISOR.json before starting work
- Declare work sessions and lock specific files/sections
- Update status from PLANNED → IN_PROGRESS → COMPLETE

**Continuity Updates**:
- REQUIRED after any significant work on dox-admin
- Update `continuity/CONTINUITY_MEMORY.md` with session details
- Include files modified, decisions made, and next steps

**Memory-Bank Coordination**:
- Update relevant TEAM_*.json files when affecting team coordination
- Record strategic decisions in memory-banks
- Track blockers and dependencies in BLOCKING_ISSUES.json

Failure to comply with the protocol may result in conflicting governance decisions and loss of implementation continuity.

## Development Workflow

**Governance Document Management**:

1. **Standards Updates**:
   - Any changes to `standards/` require supervisor approval
   - Must update all dependent services when standards change
   - Version all standards with change logs

2. **Service Registry Maintenance**:
   - Add new services to `SERVICES_REGISTRY.md` with complete metadata
   - Update service dependencies and integration points
   - Track service implementation status and milestones

3. **Memory-Bank Operations**:
   - All JSON files must validate against schemas
   - Update timestamps for all coordination changes
   - Maintain atomic operations for consistency

**Planning and Coordination**:

1. **Strategic Planning**:
   - Create and update plans in `planning/` directory
   - Use established templates for consistency
   - Archive completed plans with proper documentation

2. **Continuity Tracking**:
   - Update `CONTINUITY_MEMORY.md` after each implementation session
   - Include current state, blockers, and next session priorities
   - Maintain executive summary for quick handoffs

3. **Template Management**:
   - Keep `SERVICE_TEMPLATE/` updated with latest standards
   - Create new templates as patterns evolve
   - Ensure all templates include governance references

**Quality Assurance**:

1. **Document Validation**:
   - Check all Markdown links and references
   - Validate JSON syntax and schemas
   - Ensure consistent formatting and structure

2. **Integration Verification**:
   - Verify all service references are current
   - Check that memory-bank references are accurate
   - Validate planning documents align with standards

3. **Change Management**:
   - Document all governance decisions with rationale
   - Update affected services when standards change
   - Maintain change logs for all significant updates

## Adding New Features

**When adding governance features**:

1. Update relevant standards documents
2. Create memory-bank coordination rules
3. Update SERVICE_TEMPLATE with new patterns
4. Document in CONTINUITY_MEMORY.md
5. Communicate changes to all teams

**When adding new services**:

1. Add complete entry to `SERVICES_REGISTRY.md`
2. Create service-specific memory bank
3. Generate service plan from template
4. Assign team and update coordination files
5. Update CONTINUITY_MEMORY.md with addition

**When updating protocols**:

1. Update `MULTI_AGENT_COORDINATION.md`
2. Create migration guide for existing services
3. Update all AGENTS.md files across services
4. Test protocol changes with pilot services
5. Document protocol evolution in continuity

## Service Integration

**As the central coordination hub**, dox-admin integrates with all services:

**Governance Integration**:
- All services reference `standards/` for implementation guidance
- Services update memory-banks for coordination
- Service status tracked in SERVICES_REGISTRY.md

**Planning Integration**:
- Service teams use planning templates and structure
- Service plans linked from team coordination files
- Strategic roadmap coordinated through dox-admin

**Continuity Integration**:
- All service implementation sessions update CONTINUITY_MEMORY.md
- Service-specific continuity tracked in memory-banks
- Cross-service dependencies documented and managed

**Template Integration**:
- New services created from SERVICE_TEMPLATE
- Service-specific adaptations documented
- Template evolution based on service experience

## Configuration Management

**Governance Configuration**:
- All settings and standards in `standards/` directory
- Memory-bank schemas in `memory-banks/schemas/`
- Planning templates in `planning/templates/`

**Environment Variables**:
- No environment-specific configuration required
- All governance data stored in repository
- Coordination state managed through JSON files

**Version Control**:
- All governance documents under Git version control
- Tagged releases for stable governance versions
- Branch strategy for experimental changes

## Health Monitoring

**Governance Health Checks**:
- Validate all Markdown documents weekly
- Check JSON memory-bank consistency daily
- Verify service registry accuracy monthly

**Coordination Monitoring**:
- Monitor memory-bank update frequency
- Track agent collaboration patterns
- Identify governance conflicts early

**Continuity Monitoring**:
- Review CONTINUITY_MEMORY.md currency
- Validate planning document alignment
- Ensure template-service consistency

**Quality Metrics**:
- Document completeness and accuracy
- Link validation and reference integrity
- Template adoption and effectiveness

## Best Practices & Sync Requirements

**MANDATORY DAILY SYNC**: This document must be checked and updated if it's more than 1 day old to ensure best practices compliance.

### Governance Best Practices (2025 Standards)

**Documentation Standards**:
- ✅ **Single Source of Truth**: All governance in `/dox-admin/strategy/`
- ✅ **Version Control**: All changes tracked with Git history
- ✅ **Reference Integrity**: All links and cross-references validated
- ✅ **Template Consistency**: Standardized patterns across all services

**Coordination Standards**:
- ✅ **Memory-Bank Protocol**: Atomic operations with validation
- ✅ **Agent Collaboration**: File locking and status tracking
- ✅ **Continuity Updates**: Session handoff documentation
- ✅ **Team Coordination**: Structured communication protocols

**Quality Assurance**:
- ✅ **Document Validation**: Regular checks for accuracy and completeness
- ✅ **Schema Validation**: JSON memory-banks must validate
- ✅ **Change Management**: Documented rationale and impact analysis
- ✅ **Service Alignment**: Ensure all services reference current standards

### Daily Sync Checklist (REQUIRED)

**Every 24 hours, agents must**:
1. **Check Last Updated**: Verify this document's last updated date
2. **Review Governance Standards**: Ensure current implementation follows documented standards
3. **Validate Memory-Banks**: Check JSON consistency and currency
4. **Update Service Registry**: Verify service status and metadata accuracy
5. **Check Planning Alignment**: Ensure plans align with current standards and roadmap

**Weekly Coordination**:
1. **Review CONTINUITY_MEMORY.md**: Ensure currency and completeness
2. **Validate All References**: Check links and cross-document references
3. **Update Templates**: Reflect new patterns and lessons learned
4. **Team Sync Check**: Verify team coordination files are current
5. **Blocker Review**: Address any items in BLOCKING_ISSUES.json

## Continuity Updates

**REQUIRED**: After completing any significant work on dox-admin, agents must update `/dox-admin/continuity/CONTINUITY_MEMORY.md` with:

- **Governance Changes**: New standards, updated protocols, template modifications
- **Service Registry Updates**: New services, status changes, dependency updates
- **Memory-Bank Changes**: Coordination protocol updates, new memory banks
- **Planning Updates**: Strategic roadmap changes, new plans, completed initiatives
- **Template Evolution**: SERVICE_TEMPLATE updates, new patterns adopted
- **Continuity Impact**: How changes affect other services and future sessions
- **Next Session Priorities**: Critical items for next implementation session

**CRITICAL**: Always verify this AGENTS.md document is current with latest best practices before proceeding with any governance work.

This ensures proper handoff between agents and maintains governance consistency across the entire platform.

## Contact & Support

**Team**: Supervisor Agent
**Service Owner**: System Administrator
**Coordination**: Via `/dox-admin/strategy/memory-banks/SUPERVISOR.json`
**Standards**: `/dox-admin/strategy/standards/`
**Service Registry**: `/dox-admin/strategy/SERVICES_REGISTRY.md`
**Planning**: `/dox-admin/strategy/planning/`
**Templates**: `/dox-admin/strategy/SERVICE_TEMPLATE/`

**Governance Support**:
- Questions about standards: Reference `/dox-admin/strategy/standards/`
- Service coordination: Use memory-banks protocol
- Template usage: Follow SERVICE_TEMPLATE checklist
- Planning guidance: Use planning templates and structure

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-11-04
**Version**: 1.0
**Next Sync Check**: 2025-11-05 (24-hour requirement)
**Best Practices Compliance**: ✅ Current with 2025 standards
**Governance Scope**: ✅ All 22 services coordinated through dox-admin
**Continuity Protocol**: ✅ Session handoff via CONTINUITY_MEMORY.md
# Agent Protocol: dox-admin (The Nerve Center)

## Objective

This document provides the specific protocols and conventions for working on the `dox-admin` service. All agents, including the Supervisor and Worker (Jules), must adhere to these rules.

**Service Purpose**: Central coordination hub, governance repository, and visual dashboard for the Pact Platform ecosystem. This service governs all 22+ services.

**Primary Functions**:
- **Governance**: Define and enforce standards (`governance/`).
- **State**: Track the live status of the system (`state/`).
- **Visibility**: Provide a visual dashboard for humans and agents (`dashboard/`).
- **Coordination**: Assign and track tasks via the Worker Protocol (`workspace/`).

## Architecture & Directory Structure

```text
dox-admin/
├── governance/             # STATIC: The Laws & Reference
│   ├── standards/          # Frozen governance standards (API, Tech, etc.)
│   ├── templates/          # Service templates (e.g., SERVICE_TEMPLATE)
│   └── reference/          # Reference docs, PDFs, catalogs
├── state/                  # ACTIVE: The Living Memory
│   ├── memory-banks/       # Real-time coordination JSONs
│   ├── registry/           # Service & Team Registries
│   ├── tasks/              # Task queues (pending, active, completed)
│   └── CONTINUITY_MEMORY.md # Master continuity log
├── dashboard/              # VISUAL: The Supervisor UI
│   ├── public/             # GitHub Pages source (HTML/JS)
│   └── generator/          # Build scripts
├── workspace/              # ACTIVE: Jules' Workbench
│   ├── current_task/       # Symlink or active directory
│   └── snapshots/          # Visual artifacts from tasks
└── archive/                # HISTORY: Inactive sessions & reports
```

## Core Protocols

### 1. Governance Protocol
- **Single Source of Truth**: All standards live in `governance/standards/`.
- **Service Template**: All new services must clone `governance/templates/SERVICE_TEMPLATE`.
- **Changes**: Modifying governance requires a pull request and Supervisor approval.
- **Git Workflow**: Follow `governance/standards/GIT_WORKFLOW.md` for synchronization.

### 2. Memory-Bank Protocol
- **Location**: `state/memory-banks/`.
- **File Locking**: Check `SUPERVISOR.json` before starting work.
- **Updates**: Agents must update the relevant JSON files (e.g., `TEAM_*.json`) to reflect their progress.

### 3. Continuity Protocol
- **Master Log**: `state/CONTINUITY_MEMORY.md` is the implementation history.
- **Requirement**: You MUST update this file after every significant session.
- **Format**: Date, Session Goal, Changes Made, Next Steps.

### 4. Worker Protocol (Jules) - 🚀 AI-POWERED (Version 2.0)
- **MCP Server Integration**: Direct access to Google Jules API with 9 tools, 3 resources, 2 prompts
- **Multi-Worker Orchestration**: Deploy parallel AI workers for different specializations
- **Real-time Monitoring**: Background polling every 5 seconds for worker status
- **Task Assignment**: Deploy workers via MCP tools or assign tasks in `state/tasks/pending/`.
- **Execution**:
    1.  Deploy Jules worker using `jules_create_worker` tool with specific mission
    2.  Monitor worker progress via `workers://all` and `worker://{session_id}/status` resources
    3.  Review AI-generated plans and approve with `jules_approve_plan` tool
    4.  Send guidance using `jules_send_message` tool if needed
    5.  Workers execute specialized tasks (memory optimization, documentation, analysis)
    6.  Generate real-time activity logs via `worker://{session_id}/activities` resource
- **Learning Integration**: Workers learn project patterns and contribute to shared knowledge
- **Completion**:
    1.  Workers auto-update memory banks with discovered insights
    2.  Move task to `state/tasks/completed/`.
    3.  Update `state/memory-banks/SUPERVISOR.json` with AI-enhanced knowledge.
    4.  Workers contribute to `state/CONTINUITY_MEMORY.md` with learned patterns.

### Current AI Workforce Deployments
- **Worker Alpha**: Memory & Status Optimization Specialist
- **Worker Beta**: Project Site Enhancement Specialist
- **Worker Gamma**: Continuance Integration Specialist
- **Worker Delta**: PACT Platform Analysis Specialist

## Dashboard & Visualization
- The **Supervisor Dashboard** is hosted via GitHub Pages from `dashboard/public/`.
- It visualizes the data found in `state/`.
- Agents should ensure `state/` JSONs are valid to keep the dashboard green.

## Health Checks (Daily)
1.  **Validate Structure**: Ensure no files are floating in the root (except `README.md`, `AGENTS.md`, `PROPOSED_RESTRUCTURE.md`).
2.  **Check Continuity**: Is `state/CONTINUITY_MEMORY.md` up to date?
3.  **Review Blocker**: Check `state/memory-banks/BLOCKING_ISSUES.json`.

---

**Status**: ✅ ACTIVE
**Version**: 2.0 (Nerve Center Restructure)
**Last Updated**: 2025-11-10
** Governance Scope**: All 22 services.

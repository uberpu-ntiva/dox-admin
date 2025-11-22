# Pact Platform: MULTI-AGENT COORDINATION FRAMEWORK

**Formal Protocol for Agent Collaboration Across 16+ Microservices**

**Last Updated**: 2025-10-31
**Owner**: Supervisor Agent (System Owner)
**Status**: ACTIVE

---

## Overview

This document formalizes how multiple AI agents coordinate development across the Pact Platform's 16+ microservices without conflicts, race conditions, or resource contention.

**Key Principle**: Agents work in **parallel on different services**, coordinating through **shared state files** and **memory banks** with atomic file operations and explicit locking.

---

## Agent Organization

### Team Structure (7 Teams + 1 Supervisor)

```
Supervisor Agent (1)
  └─ Infrastructure Team (2 agents) → dox-core-store, dox-core-auth
  └─ Document Team (2 agents) → dox-tmpl-service, dox-tmpl-field-mapper
  └─ Signing Team (2 agents) → dox-esig-*, dox-rtns-*
  └─ Activation Team (2 agents) → dox-actv-*
  └─ Data Team (2 agents) → dox-data-*
  └─ Frontend Team (2 agents) → dox-gtwy-main
  └─ Automation Team (2 agents) → dox-auto-*
```

### Agent Lifecycle

Each agent follows this lifecycle:

```
1. STARTUP → Read coordination files
2. DECLARE → Create status file with intent
3. LOCK → Acquire locks on resources
4. WORK → Implement features/fixes
5. TEST → Run tests, verify quality
6. COMMIT → Push changes to git
7. UPDATE_CONTINUITY → Update continuity memory (REQUIRED)
8. SHUTDOWN → Update status as done
```

**NEW: Continuity Update Requirement** - All agents MUST update `/dox-admin/state/CONTINUITY_MEMORY.md` after completing significant work to ensure proper session-to-session handoff.

---

## File Structure for Coordination

### Central Coordination Hub

**Location**: `/dox-admin/governance/`

```
/dox-admin/governance/
├── SERVICES_REGISTRY.md              # Master service catalog
├── memory-banks/                     # Agent coordination files
│   ├── SUPERVISOR.json              # Master log
│   ├── TEAM_*.json                  # Team coordination (7 files)
│   ├── SERVICE_*.json               # Per-service status (20 files)
│   ├── API_CONTRACTS.json           # Versioned APIs
│   ├── BLOCKING_ISSUES.json         # Cross-team blockers
│   ├── TEST_REFRESH_LOG.json        # Test coordination
│   └── DEPLOYMENT_LOG.json          # Go-live timeline
```

### Service Repository Structure

**Location**: Each service repo `[service-name]/`

```
[service-name]/
├── .state/                          # EPHEMERAL agent status (git-ignored)
│   ├── agent-[id]-status.json
│   └── [locked-file-locks]/
├── memory-banks/                    # PERSISTENT agent knowledge
│   └── [auto-populated by agents]
└── [source code, tests, docs]
```

---

## State Management

### Agent Status File Schema

**Location**: `.state/agent-[agent-id]-status.json`

**Format**:
```json
{
  "agent_id": "agent-backend-20251031-120000",
  "timestamp": "2025-10-31T12:00:00Z",
  "task": {
    "id": "task-123",
    "title": "Implement PDF upload validation",
    "service": "dox-tmpl-pdf-recognizer",
    "priority": "high",
    "description": "Add file size and MIME type validation"
  },
  "status": "active",
  "locked_resources": [
    "/workspace/cmhfcgyd7045kojiqg150pqth/dox-tmpl-pdf-recognizer/app/app.py",
    "/workspace/cmhfcgyd7045kojiqg150pqth/dox-admin/state/memory-banks/SERVICE_dox-tmpl-pdf-recognizer.json"
  ],
  "proposed_branch": "feature/pdf-upload-validation",
  "git_commit_count": 2,
  "test_status": "passing",
  "last_activity": "2025-10-31T12:15:30Z",
  "heartbeat_expires_at": "2025-10-31T13:00:00Z"
}
```

**Status Values**:
- `active` - Agent is actively working
- `waiting_for_lock` - Agent waiting for resource lock
- `waiting_for_human` - Agent blocked, needs human decision
- `error` - Agent encountered error
- `done` - Agent completed task
- `stale` - Agent heartbeat expired (cleanup candidate)

---

## File Locking Protocol

### Lock Acquisition

**Goal**: Prevent conflicting edits to shared files

**Atomic Lock File Pattern**:

```python
def acquire_lock(file_path, agent_id, timeout_seconds=300):
    """Acquire exclusive lock on file."""
    lock_file = f"{file_path}.lock"

    # Atomic write-and-rename (no race condition)
    lock_content = {
        "agent_id": agent_id,
        "timestamp": iso8601_now(),
        "expires_at": iso8601_future(timeout_seconds)
    }

    # Write to temp file first
    temp_lock = f"{lock_file}.tmp"
    write_json(temp_lock, lock_content)

    # Atomic rename (platform dependent)
    os.rename(temp_lock, lock_file)  # Linux/Mac
    # os.replace(temp_lock, lock_file)  # Windows

    return True
```

### Lock Release

```python
def release_lock(file_path, agent_id):
    """Release lock on file."""
    lock_file = f"{file_path}.lock"

    # Verify we own the lock
    lock_data = read_json(lock_file)
    if lock_data["agent_id"] != agent_id:
        raise Exception("Lock owned by different agent")

    # Remove lock file
    os.remove(lock_file)
```

### Lock Waiting (Exponential Backoff)

```python
def wait_for_lock(file_path, max_wait_seconds=600):
    """Wait for lock to be released."""
    wait_time = 1  # Start at 1 second
    elapsed = 0

    while elapsed < max_wait_seconds:
        lock_file = f"{file_path}.lock"

        if not os.path.exists(lock_file):
            return True  # Lock acquired

        # Check if lock is stale (agent crashed)
        lock_data = read_json(lock_file)
        if iso8601_parse(lock_data["expires_at"]) < now():
            os.remove(lock_file)  # Force-release stale lock
            return True

        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        time.sleep(wait_time)
        elapsed += wait_time
        wait_time = min(wait_time * 2, 60)  # Max 60s between retries

    raise Exception(f"Lock timeout after {max_wait_seconds}s")
```

---

## Shared Memory Banks

### Service Status File

**Location**: `/dox-admin/state/memory-banks/SERVICE_[service-name].json`

**Schema**:
```json
{
  "service_name": "dox-core-store",
  "team": "Infrastructure",
  "status": "in_progress",
  "phase": 2,
  "timeline_weeks": "5-7",
  "current_sprint": 1,
  "assigned_agents": ["agent-1", "agent-2"],
  "current_tasks": [
    {
      "id": "task-1",
      "title": "Design MSSQL schema",
      "status": "in_progress",
      "agent": "agent-1",
      "completion_percent": 60
    }
  ],
  "completed_tasks": [
    {
      "id": "task-0",
      "title": "Research MSSQL best practices",
      "status": "completed",
      "agent": "agent-1"
    }
  ],
  "blockers": [
    {
      "id": "blocker-1",
      "title": "Waiting for Azure credentials",
      "blocking": true,
      "resolution": "HR to provision accounts"
    }
  ],
  "dependencies": [
    {
      "service": "dox-core-auth",
      "relationship": "upstream (depends on this)",
      "status": "on_schedule"
    }
  ],
  "test_coverage": "0%",
  "git_commits": 0,
  "last_update": "2025-10-31T12:00:00Z",
  "notes": "Initial schema design in progress"
}
```

### Team Coordination File

**Location**: `/dox-admin/state/memory-banks/TEAM_[team-name].json`

**Schema**:
```json
{
  "team_name": "Infrastructure",
  "members": [
    {
      "agent_id": "agent-backend-infra-1",
      "role": "Database Engineer",
      "services": ["dox-core-store"]
    },
    {
      "agent_id": "agent-backend-infra-2",
      "role": "Backend Engineer",
      "services": ["dox-core-auth"]
    }
  ],
  "services_owned": ["dox-core-store", "dox-core-auth"],
  "current_phase": 2,
  "sprint": 1,
  "sprint_goal": "Build core database and authentication",
  "team_blockers": [],
  "external_dependencies": [
    {
      "team": "Document Team",
      "service": "dox-tmpl-service",
      "dependency_type": "downstream (depends on us)",
      "expected_ready": "2025-11-28"
    }
  ],
  "test_pass_rate": "0%",
  "deployment_status": "not_started",
  "last_sync": "2025-10-31T12:00:00Z"
}
```

### API Contracts Registry

**Location**: `/dox-admin/state/memory-banks/API_CONTRACTS.json`

**Schema**:
```json
{
  "services": {
    "dox-core-store": {
      "version": "1.0.0",
      "endpoints": [
        {
          "method": "POST",
          "path": "/api/v1/templates",
          "status": "stable",
          "documentation": "dox-core-store/docs/api.md"
        }
      ],
      "breaking_changes": [],
      "last_updated": "2025-10-31T12:00:00Z"
    }
  },
  "cross_service_calls": [
    {
      "caller": "dox-gtwy-main",
      "called": "dox-core-store",
      "endpoint": "GET /api/v1/templates",
      "status": "active",
      "test_status": "passing"
    }
  ]
}
```

---

## Conflict Detection & Resolution

### Automatic Conflict Detection

The **Supervisor Agent** scans for conflicts:

```python
def detect_conflicts():
    """Detect file conflicts between agents."""

    # 1. Check for resource contention
    state_files = glob('.state/agent-*-status.json')
    for state1, state2 in combinations(state_files, 2):
        agent1 = load_json(state1)
        agent2 = load_json(state2)

        # Check for shared locked resources
        shared_resources = set(agent1['locked_resources']) & set(agent2['locked_resources'])
        if shared_resources:
            alert(f"Resource conflict: {shared_resources}")

    # 2. Check for stale locks (agent crashed)
    for status_file in state_files:
        agent = load_json(status_file)
        if iso8601_parse(agent['heartbeat_expires_at']) < now():
            alert(f"Stale lock detected: {agent['agent_id']}")

    # 3. Check for git merge conflicts
    git_conflicts = run_git('status | grep CONFLICT')
    if git_conflicts:
        alert(f"Git conflicts detected: {git_conflicts}")
```

### Conflict Resolution

**Automatic**:
- Stale locks: Supervisor forces release after timeout
- Non-overlapping changes: Auto-merge via git

**Manual**:
- Overlapping changes: Status set to `requires_human_intervention`
- API conflicts: Supervisor notifies teams, schedules sync meeting
- Scope expansion: Team lead prioritizes

---

## Git Workflow

### Branch Naming

```
feature/[service]/[description]    # New feature
bugfix/[service]/[description]     # Bug fix
refactor/[service]/[description]   # Refactoring
test/[service]/[description]       # Test additions
```

**Examples**:
- `feature/dox-core-store/multi-tenancy-schema`
- `bugfix/dox-tmpl-pdf-upload/file-validation`
- `test/dox-core-auth/jwt-token-validation`

### Commit Message Format

```
feat(service): Brief description

Detailed description of changes.
- Bullet point 1
- Bullet point 2

Closes #123
Agent: agent-backend-20251031-120000
```

**Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Build/tooling

### Pull Request Process

1. Agent commits changes locally
2. Agent creates PR with description
3. Supervisor Agent or team lead reviews
4. All tests must pass (CI/CD)
5. PR merged to main
6. Agent updates SERVICE status as complete

---

## Supervisor Agent Responsibilities

### Daily Tasks

- **Monitor health**: Check all agent status files
- **Detect stale locks**: Force-release after timeout
- **Alert on errors**: Notify teams of agent failures
- **Verify heartbeats**: Confirm all active agents are alive

### Weekly Tasks

- **Sync meeting**: Cross-team coordination
- **Progress review**: Check SERVICE_*.json for updates
- **Blocker resolution**: Escalate blockers
- **Test coordination**: Refresh failing tests

### Sprint Planning

- Assign services to teams
- Set weekly milestones
- Update SERVICES_REGISTRY.md
- Validate dependencies

---

## Memory Bank Update Protocol

### When Agent Starts

```python
# 1. Read current SERVICE status
current_status = read_json('memory-banks/SERVICE_[name].json')

# 2. Add self to current_agents list
current_status['assigned_agents'].append(agent_id)
current_status['current_tasks'].append({
    "id": task_id,
    "title": task_title,
    "status": "in_progress",
    "agent": agent_id,
    "completion_percent": 0
})

# 3. Update timestamp and write back (atomic)
current_status['last_update'] = iso8601_now()
write_json_atomic('memory-banks/SERVICE_[name].json', current_status)
```

### When Agent Completes Task

```python
# 1. Find task in current_tasks
task = find_task(task_id, current_status['current_tasks'])
task['status'] = 'completed'
task['completion_percent'] = 100

# 2. Move to completed_tasks
current_status['completed_tasks'].append(task)
current_status['current_tasks'].remove(task)

# 3. Commit and update
write_json_atomic('memory-banks/SERVICE_[name].json', current_status)
```

### When Agent Encounters Blocker

```python
current_status['blockers'].append({
    "id": blocker_id,
    "title": blocker_title,
    "blocking": true,
    "resolution": "Action required from team X"
})

# Set status to waiting_for_human
current_status['current_status'] = 'waiting_for_human'
write_json_atomic('memory-banks/SERVICE_[name].json', current_status)

# Alert Supervisor
alert_supervisor(f"Blocker in {service}: {blocker_title}")
```

---

## Continuity Memory Update Protocol (REQUIRED)

### Purpose

The continuity memory system ensures that implementation context is preserved across sessions. When the implementation context limit is reached or a session ends, the next session needs complete information about what was done.

### When to Update Continuity Memory

Agents **MUST** update `/dox-admin/state/CONTINUITY_MEMORY.md` when:

1. **Completing a major feature** - Service implementation, new endpoint, major refactor
2. **Completing a sprint milestone** - End of sprint, phase completion
3. **Before long pauses** - End of work session, before context switch
4. **After architectural decisions** - Technology choices, design patterns adopted
5. **When creating new services** - New repositories, new microservices
6. **After fixing critical bugs** - Important fixes that affect other services

### What to Include in Continuity Updates

```markdown
## What Was Implemented (Session N - YYYY-MM-DD)

### System/Service Name

**Location**: `/path/to/service/`

**Components Implemented**:
- ✅ Component 1 (file path)
- ✅ Component 2 (file path)
- ✅ Component 3 (file path)

**Key Features Delivered**:
- Feature 1 description
- Feature 2 description
- Feature 3 description

**Architectural Decisions**:
- Decision 1: Why it was made
- Decision 2: Trade-offs considered

**Dependencies Added**:
- Library 1: Purpose
- Library 2: Purpose

**Known Issues/Incomplete Work**:
- Issue 1: What needs to be done
- Issue 2: Blocker or limitation

**Total Files Created/Modified**: N files
```

### Update Process

```python
# 1. Read current continuity memory
continuity_doc = read_file('/dox-admin/state/CONTINUITY_MEMORY.md')

# 2. Add new session section after Executive Summary
new_section = f"""
## What Was Implemented (Session {session_num} - {date})

### {system_name}

**Location**: `{service_path}`

**Components Implemented**:
{component_list}

**Key Features Delivered**:
{feature_list}

**Total Files Created**: {file_count} files
"""

# 3. Update Executive Summary with latest status
update_executive_summary(latest_completion_info)

# 4. Update task status table (mark completed items)
update_task_status_table(completed_tasks)

# 5. Update repository status (if new repos added)
update_repository_list(new_repos)

# 6. Write back atomically
write_file_atomic('/dox-admin/state/CONTINUITY_MEMORY.md', updated_doc)
```

### Continuity Update Checklist

Before completing work, verify continuity update includes:

- [ ] Session date and number
- [ ] System/service name and location
- [ ] List of files created/modified
- [ ] Key features delivered
- [ ] Architectural decisions made
- [ ] Dependencies added/changed
- [ ] Known issues or incomplete work
- [ ] Updated Executive Summary
- [ ] Updated task status table
- [ ] Updated repository list

### Example Continuity Update

```markdown
## What Was Implemented (Session 2 - 2025-11-03)

### System 3: Document Team Services (Phase 2)

**Location**: `/dox-tmpl-pdf-upload/` and `/dox-mcp-server/`

**Service 1: dox-tmpl-pdf-upload** (COMPLETED):
- ✅ FastAPI application with async/await support (app/main.py)
- ✅ Comprehensive file validation pipeline (app/services/validation.py)
- ✅ Azure Blob Storage integration (app/services/storage.py)
- ✅ Complete API endpoints for CRUD operations

**Service 2: dox-mcp-server** (COMPLETED):
- ✅ FastMCP server implementation (app/main.py)
- ✅ MCP Tools: template_upload, template_search, template_validate, template_info
- ✅ MCP Prompts: analyze_template, field_detection
- ✅ MCP Resources: template_list, validation_report

**Key Features Delivered**:
- Multi-layer security validation
- AI-powered field detection
- Production-ready Docker configurations

**Total Files Created**: 40+ files
```

### Enforcement

- **Mandatory**: All agents must update continuity before marking work as complete
- **Verification**: Supervisor agent checks for continuity updates in review
- **Consequence**: Work without continuity updates is considered incomplete

---

## Communication Protocol

### Intra-Team Communication

**Via Memory Banks**: Teams coordinate via shared JSON files in memory-banks/

```json
// TEAM_SIGNING.json
{
  "message_to_data_team": "We need event API from dox-data-aggregation by W18",
  "message_from_data_team": "Confirmed, ETA W17"
}
```

### Cross-Team Communication

**Via Supervisor**: Supervisor Agent coordinates cross-team items

**Weekly Sync**:
- Monday 9 AM: Supervisor reads all TEAM_*.json files
- Monday 10 AM: Identifies conflicts and blockers
- Monday 11 AM: Posts coordination needs in Slack
- Tuesday 2 PM: Teams sync on critical items
- Friday 4 PM: Sprint review

---

## Scaling to 15+ Agents

### Load Balancing

- **Per Service**: Max 2 agents per service (prevents contention)
- **Per Team**: 2-3 services per team (manageable scope)
- **Phase Coordination**: Phases don't overlap (serial) OR teams don't share dependencies (parallel)

### Resource Management

- **Total agents**: 15 (7 teams × 2 agents + 1 supervisor)
- **Concurrent repos**: 7 (one per team)
- **Lock timeout**: 10 minutes (prevents deadlocks)
- **Heartbeat interval**: 5 minutes (dead agent detection)

### Bottleneck Prevention

- **Shared resources**: Only dox-admin/strategy files (coordinated via locks)
- **Database sharing**: NO (each service owns schema)
- **API versioning**: Prevents breaking changes
- **Parallel phases**: Phase 2 and Phase 3 can overlap (no dependencies)

---

## Emergency Procedures

### Agent Crash

1. Supervisor detects stale heartbeat
2. Supervisor forces-releases all locks
3. Supervisor rolls back unfinished work (git reset)
4. Supervisor alerts human operator
5. Operator restarts agent or reassigns work

### Deadlock

1. If two agents wait for each other's locks >10 minutes
2. Supervisor forcefully breaks circular dependency
3. One lock released, other agent retries
4. Teams notified of deadlock resolution

### Database Corruption

1. If SERVICE_*.json or memory banks corrupted
2. Restore from git (committed state)
3. Rebuild from commit history
4. Alert humans if significant loss

---

## Debugging Agent Issues

### Check Agent Status

```bash
# View all active agents
ls -lta .state/agent-*-status.json

# View specific agent status
cat .state/agent-backend-20251031-120000-status.json

# Check heartbeat (should be < 5 min old)
date vs timestamp in status file
```

### Check Locks

```bash
# View all locks
find . -name "*.lock" -type f

# Check who owns each lock
for lock in $(find . -name "*.lock"); do
  echo "$lock owned by:"
  cat "$lock"
done
```

### Check Memory Banks

```bash
# Verify memory bank integrity
cat /dox-admin/state/memory-banks/SERVICE_[name].json | python -m json.tool

# Check for stale data
grep "last_update" /dox-admin/state/memory-banks/SERVICE_*.json | sort
```

---

## References

**See Also**:
- `/dox-tmpl-pdf-recognizer/docs/agent-protocol/README.md` - Original protocol
- `/dox-admin/state/registry/SERVICES_REGISTRY.md` - Service catalog
- `/dox-admin/governance/standards/` - All standards

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-10-31
**Version**: 1.0


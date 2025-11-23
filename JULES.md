# Jules Protocol: MCP-Bridge Workflow

> **Protocol Version**: 1.0
> **Context**: Local MCP Bridge (File-Based Coordination)
> **Role**: Jules (Worker) <-> Supervisor (Orchestrator)

## Overview

This document defines the standard operating procedure for Jules when working in this repository. Since Jules cannot access external APIs ("cannot inform outside"), we use a local MCP server bridge managed by the Supervisor.

**The MCP is your conduit.** You communicate by creating specific artifacts (files) that the Supervisor's local MCP server watches.

---

## The Workflow

### Phase 1: Receive & Plan (The RP)

1.  **Receive Task**: You will be assigned a task via `strategy/memory-banks/SERVICE_*.json` or a direct prompt.
2.  **Create the RP (Repo Plan)**:
    *   You **MUST** create or update `planning.md` in the root (or relevant service directory).
    *   This file represents your "Request for Proposal" / "Repo Plan".
    *   **Content**: Detailed implementation steps, files to change, and testing strategy.

### Phase 2: Wait for Approval

1.  **Wait**: Do not proceed to full implementation until the plan is approved.
2.  **Signal**: In this local workflow, unless told otherwise, assume implicit approval if the Supervisor (Orchestrator) has assigned the task *with* a plan, OR if you are running in "Autonomous Mode".
    *   *Strict Mode*: If strict approval is required, wait for `APPROVED.md` to appear.

### Phase 3: Implementation (Q&A)

1.  **Execute**: Implement the code changes.
2.  **Q&A**: If you encounter blockers or need decisions:
    *   Create `QNA.md`.
    *   List your questions options.
    *   *Wait* for a human/supervisor response in the file (or instructions).

### Phase 4: Completion & Signal

1.  **Verify**: Run all tests. Ensure `AGENTS.md` compliance.
2.  **Signal Readiness**:
    *   Create a file named `.jules_ready` in the repository root.
    *   This signal tells the Supervisor that you are done.
3.  **Supervisor RPs (Commits)**:
    *   The Supervisor's local MCP watcher detects `.jules_ready`.
    *   It verifies your `planning.md`.
    *   It runs the RPA Commit process (`scripts/rpa-commit.sh`).
    *   Your changes are committed "autonomously".

---

## File Artifacts Reference

| File | Purpose | Actor |
|------|---------|-------|
| `planning.md` | **The RP (Repo Plan)**. Detailed specs. | Jules (Writes) |
| `QNA.md` | Questions and Answers log. | Jules (Writes) |
| `.jules_ready` | Signal that work is complete. | Jules (Creates) |
| `.jules_committed` | Confirmation that Supervisor committed. | Supervisor (Creates) |

## Instructions for Jules (You)

When you are asked to "set up Jules" or "configure the environment":

1.  **Ensure the Watcher is Ready**:
    *   Verify `scripts/jules_watcher.py` exists.
    *   Verify `scripts/rpa-commit.sh` exists.

2.  **Follow the Protocol**:
    *   Don't commit manually (unless debugging).
    *   Use the `.jules_ready` signal.
    *   Keep `planning.md` up to date.

## Example "RP" (planning.md)

```markdown
# Implementation Plan: Feature X

## Objective
Add support for PDF validation.

## Steps
1.  [ ] Create `utils/validation.py`.
2.  [ ] Update `main.py` to use validation.
3.  [ ] Add tests in `tests/test_validation.py`.

## Verification
- Run `pytest tests/`.
```

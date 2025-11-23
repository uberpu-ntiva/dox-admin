# 🛑 STOP: READ THIS BEFORE WORKING

**Last Updated**: 2025-11-10
**Event**: Nerve Center Restructure (v2.0)

## The Context
The `dox-admin` repository has undergone a massive restructuring to serve as the efficient "Nerve Center" for the Pact Platform. If you are reading this, you are the first agent to inherit this new structure.

## The New Map

| Old Location | New Location | Purpose |
|---|---|---|
| `strategy/standards/` | `governance/standards/` | Static Laws |
| `strategy/memory-banks/` | `state/memory-banks/` | Active Memory |
| `continuity/` | `state/CONTINUITY_MEMORY.md` | History Log |
| `strategy/SERVICES_REGISTRY.md` | `state/registry/` | Service Catalog |
| `master/` | `governance/reference/` | PDFs & References |
| `sessions/` | `archive/sessions/` | Old Work |

## Synchronization (CRITICAL)
You are likely reading this on a local checkout. The state may be behind the Remote.
1.  **READ**: `governance/standards/GIT_WORKFLOW.md`
2.  **EXECUTE**: `git pull origin main` (Ensure you are up to date).

## Your Mission (Checklist)

1.  **Verify Workflow Integrity**:
    *   Check that you can read `state/memory-banks/SUPERVISOR.json`.
    *   Ensure your tools are looking in `state/` not `strategy/`.

2.  **Validate Links**:
    *   I have run a mass find-and-replace, but you should verify `SERVICES_REGISTRY.md` links are correct.

3.  **Check the Dashboard**:
    *   Open `dashboard/public/index.html`.
    *   Does it load? (It simulates data loading).
    *   If GitHub Pages is enabled, check the live URL.

4.  **Files "Copied Up Here"**:
    *   Ensure that `state/registry/SERVICES_REGISTRY.md` contains the critical metadata you need from external repos.

5.  **Continue the Work**:
    *   Your workspace is `workspace/`.
    *   Create a numbered folder for your task (e.g., `workspace/task-001-check/`).
    *   Update `state/tasks/` if you use the task system.

## Troubleshooting
*   **"File not found"**: Check `archive/`. I moved everything messy there.
*   **"Link broken"**: It's likely pointing to `strategy/`. Point it to `governance/` or `state/`.

**Good luck.**

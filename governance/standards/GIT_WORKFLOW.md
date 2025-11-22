# Git Synchronization Workflow

**Purpose**: Ensure the Supervisor (Local), Jules (Worker), and the Dashboard (Cloud) remain in sync.

## The Problem
The "Nerve Center" exists in three states:
1.  **Remote (GitHub)**: The Source of Truth.
2.  **Supervisor (Local)**: The running process managing the system.
3.  **Jules (Worker)**: The agent executing tasks and pushing changes.

## The Protocol

### 1. The Cycle of Change
1.  **Jules** checks out a task-specific branch (e.g., `task-001/restructure`).
2.  **Jules** commits and pushes to **Remote**.
3.  **Supervisor** (or Human) reviews the PR on GitHub.
4.  **Supervisor** merges PR into `main`.
5.  **GitHub Actions** (Dashboard) detects the push to `main` and redeploys the website.
6.  **Supervisor (Local)** MUST run `git pull origin main` to update its local state.

### 2. The Dashboard (GitHub Pages)
*   The Dashboard workflow (`deploy-dashboard.yml`) runs on an **ephemeral runner** in the cloud.
*   It checks out the code fresh every time.
*   It **does not** conflict with the Supervisor's local checkout.
*   It reflects the state of the **Remote** `main` branch.

### 3. Conflict Resolution
If the Supervisor has uncommitted local changes:
1.  **Stash**: `git stash`
2.  **Pull**: `git pull origin main`
3.  **Pop**: `git stash pop`
4.  **Resolve**: Fix any merge conflicts manually.

**Rule**: The **Remote** `main` branch is the governing state. All agents must align to it.

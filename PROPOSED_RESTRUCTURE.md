# Pact Platform Nerve Center: Restructuring & Dashboard Proposal

## 1. Executive Summary

The **Pact Platform** has evolved into a complex multi-agent, multi-repo ecosystem. `dox-admin` acts as the "Nerve Center," but its current organization reflects organic growth rather than strategic design. To enable the Supervisor Agent and Worker Agent (Jules) to operate efficiently, we propose a comprehensive restructuring.

**Key Goals:**
*   **Centralization:** Make `dox-admin` the undeniable source of truth for Governance and State.
*   **Visibility:** Implement a web-based "Supervisor Dashboard" to visualize progress, health, and tasks.
*   **Automation:** Define a clear "Worker Protocol" for Jules to receive tasks and report results.
*   **Standardization:** Enforce a clean, uniform directory structure across all 22+ services.

---

## 2. Current State Assessment (The "Mess")

*   **Root Clutter:** High number of loose files in root (`app.py`, `*.md`, `scripts/`) makes navigation difficult.
*   **Mixed Concerns:** `strategy/` contains both static governance (standards) and active state (`memory-banks`).
*   **Inconsistent External Repos:** `dox-gtwy-main` has significant root clutter compared to `dox-rtns-barcode-matcher`.
*   **Hidden Context:** Critical context is buried in deep directory trees or PDF files in `master/`.

---

## 3. Proposed Directory Structure (The Cleanup)

We will reorganize `dox-admin` into clear domains:

```text
dox-admin/
├── .github/                # Workflows
├── governance/             # STATIC: The Laws & Reference
│   ├── standards/          # (Moved from strategy/standards)
│   ├── library/            # (Moved from master/ - PDFs, Reference docs)
│   └── templates/          # (Service templates)
├── state/                  # ACTIVE: The Living Memory (JSONs)
│   ├── memory-banks/       # (Moved from strategy/memory-banks)
│   ├── registry/           # (Services Registry & Mapping)
│   └── tasks/              # (New: Task queues for Jules)
├── workspace/              # ACTIVE: Jules' Workbench
│   ├── current_task/       # Symlink or active directory
│   └── snapshots/          # Visual artifacts
├── dashboard/              # VISUAL: The Supervisor UI
│   ├── public/             # HTML/JS/CSS (GitHub Pages source)
│   └── generator/          # Scripts to build the dashboard from state/
├── archive/                # HISTORY: Old sessions & docs
│   ├── sessions/           # (Moved from root)
│   └── legacy_plans/
├── scripts/                # UTILITIES: Maintenance & Automation
├── AGENTS.md               # The Primary Directive
└── README.md               # Human Entry Point
```

---

## 4. The Supervisor Dashboard (GitHub Pages)

A static web interface hosted on GitHub Pages, generated from the `state/` directory.

**Architecture:**
*   **Source:** `dashboard/public/index.html` (and JS/CSS).
*   **Data Feed:** The dashboard's JavaScript reads `../../state/memory-banks/*.json` (raw GitHub content or relative paths if deployed correctly).
*   **Build Process:** A Python script in `dashboard/generator/` aggregates JSON state into a `data.js` file for easy consumption by the static site.

**Features:**
1.  **System Health Tree:** Visual tree of all 22 services (Green/Red status based on `SERVICES_REGISTRY.md`).
2.  **Task Kanban:** View of `state/tasks/` (To Do, In Progress, Done).
3.  **Continuity Log:** Readable timeline of `CONTINUITY_MEMORY.md`.
4.  **Snapshots Gallery:** Visual browser for `workspace/snapshots/`.

---

## 5. The Worker (Jules) Protocol

Jules acts as the hands of the system. The protocol defines how work is assigned and executed.

**Workflow:**
1.  **Assignment:** Supervisor writes a task file to `state/tasks/pending/<task_id>.json`.
2.  **Pickup:** Jules reads the task, moves it to `state/tasks/active/`.
3.  **Execution:**
    *   Jules works in `workspace/<task_id>/`.
    *   Jules creates visual snapshots of web apps using the MCP.
    *   Snapshots are saved to `workspace/<task_id>/snapshots/`.
4.  **Completion:** Jules moves task to `state/tasks/completed/` and updates `state/memory-banks/SUPERVISOR.json`.

---

## 6. Standardization Strategy for External Repos

To fix the "mess" in other repos (like `dox-gtwy-main`), we will update the `governance/templates/SERVICE_TEMPLATE` to enforce:

```text
service-repo/
├── src/                    # Application Source Code
├── tests/                  # Tests
├── docs/                   # Documentation & Plans
├── config/                 # Configuration files
├── scripts/                # Deployment/Utility scripts
├── AGENTS.md               # Local Protocol
└── README.md               # Project Overview
```

**Migration Plan:**
1.  Update `dox-admin` first (Model the way).
2.  Update `SERVICE_TEMPLATE`.
3.  Create `MIGRATION_GUIDE.md` in `governance/standards/`.
4.  Systematically refactor external repos (starting with Gateway).

---

## 7. Immediate Next Steps

1.  **Approve this Plan:** Confirm this structure aligns with your vision.
2.  **Execute Cleanup:** I will create the directories and move files.
3.  **Build Dashboard V1:** I will generate a basic HTML dashboard to visualize `memory-banks`.
4.  **Update AGENTS.md:** Reflect the new "Nerve Center" architecture.

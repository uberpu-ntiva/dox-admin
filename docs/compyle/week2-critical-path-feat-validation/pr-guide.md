=== PULL REQUEST CREATION GUIDE ===

## PR #1: dox-tmpl-pdf-recognizer (T04 + T05)

**Title**: feat: Multi-layer file validation security and backend E2E tests (T04, T05)
**Base**: main
**Head**: feat/week2-validation
**Changes**: 870 lines across 14 files

Key changes:
- T05: Multi-layer file validation (6 security layers)
- T04: Backend E2E tests (11 test cases)
- Flask-Limiter integration for rate limiting
- ClamAV service in docker-compose.yml

## PR #2: dox-tmpl-pdf-upload (T09)

**Title**: docs: Add comprehensive service blueprint documentation (T09)
**Base**: main
**Head**: feat/week2-docs
**Changes**: 3,095 lines across 7 files

Documentation created:
- docs/architecture.md (268 lines)
- docs/api.md (287 lines)
- docs/openapi.yaml (486 lines)
- docs/integration.md (174 lines)
- docs/database.md (203 lines)
- docs/development.md (196 lines)

## Creation Methods

### Method 1: GitHub Web UI
1. Navigate to each repository
2. Click "Pull requests" → "New pull request"
3. Select main ← feat/week2-validation (or feat/week2-docs)
4. Use title and description from above

### Method 2: GitHub CLI


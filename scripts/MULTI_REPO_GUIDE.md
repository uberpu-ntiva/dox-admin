# Multi-Repository RPA Commit Guide

## Overview

The enhanced RPA commit workflow now supports managing multiple repositories from a single command, addressing the need to commit changes across services that are ahead of remote or have uncommitted work.

## Key Features Added

### 1. Repository Scanning
- **Command**: `./rpa-commit.sh scan`
- **Purpose**: Shows status of ALL repositories in workspace
- **Displays**: Repository name, current branch, uncommitted files, commits ahead of remote
- **Output**: Color-coded table (yellow = has changes)

### 2. Multi-Repository Commit
- **Command**: `./rpa-commit.sh multi "Commit message"`
- **Purpose**: Commit to ALL repositories with uncommitted changes
- **Features**:
  - Auto-detects which repos have changes
  - Works with current branch in each repo (no branch switching)
  - Auto-detects commit type and service for each repo
  - Runs pre-commit checks for each repo individually
  - Shows success/failure summary

### 3. Multi-Repository Commit with Push
- **Command**: `./rpa-commit.sh multi "Commit message" --push`
- **Purpose**: Commit AND push to remote in one operation
- **Benefits**: Streamlines workflow, triggers CI/CD immediately

### 4. Push All Ahead
- **Command**: `./rpa-commit.sh push-all`
- **Purpose**: Push ALL repositories that have commits ahead of remote
- **Use case**: After creating commits, push everything at once

## Workflow Examples

### Scenario 1: End of Day Commit

You've been working on a feature that spans multiple services. Time to commit everything:

```bash
# 1. Check what needs committing
./rpa-commit.sh scan

# Output shows:
# dox-tmpl-pdf-upload      main      8      0
# dox-mcp-server          main      5      0
# dox-admin               main      3      0

# 2. Commit to all repos with changes
./rpa-commit.sh multi "Implement validation layer across services"

# 3. Push everything
./rpa-commit.sh push-all
```

### Scenario 2: Cross-Cutting Feature

Implementing authentication changes across all services:

```bash
# Commit and push in one command
./rpa-commit.sh multi "Add JWT authentication middleware" --push
```

### Scenario 3: CI/CD Integration

In a CI/CD workflow, commit and trigger workflows:

```bash
# Commit to all repos with changes and push to trigger workflows
./rpa-commit.sh multi "Deploy configuration update" --push

# Workflows in each repository will be triggered automatically
```

### Scenario 4: Dependency Updates

Updated a shared library across multiple services:

```bash
# After updating dependencies in multiple repos
./rpa-commit.sh multi "chore: Update shared library to v2.0"

# Review commits
for repo in dox-*/; do
  cd "$repo"
  git log -1 --oneline
  cd ..
done

# Push all at once
./rpa-commit.sh push-all
```

## How It Works

### Repository Detection

The script scans the workspace for all git repositories:

```bash
# Finds all directories with .git in workspace root and subdirectories
find $WORKSPACE_ROOT -maxdepth 2 -name ".git" -type d
```

### Branch Awareness

For each repository:
- Uses `git branch --show-current` to get current branch
- Never switches branches
- Commits to whatever branch you're currently on
- Respects your workflow

### Ahead Detection

Checks if repository has commits not pushed to remote:

```bash
# Get remote tracking branch
remote_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{u})

# Count commits ahead
ahead=$(git rev-list --count "$remote_branch"..HEAD)
```

### Auto-Detection Per Repository

For each repository, independently determines:
- **Commit type**: feat, fix, docs, test, chore, refactor
- **Service name**: Based on files changed
- **Validation**: Python syntax checks

### Pre-commit Checks Per Repository

Each repository gets:
- Python syntax validation
- TODO/FIXME detection
- Git status verification
- Continuity check (for workspace-level changes)

## Command Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `scan` | Show status of all repos | Check what needs attention |
| `multi "msg"` | Commit to all with changes | End of work session, feature complete |
| `multi "msg" --push` | Commit and push all | Trigger CI/CD, deploy changes |
| `push-all` | Push all ahead repos | After manual commits |
| `interactive` | Single repo interactive | One service, need control |
| `quick "msg"` | Single repo quick commit | One service, fast commit |

## Best Practices

### When to Use Multi-Repo Mode

✅ **Good use cases**:
- End of day commits
- Cross-cutting features (logging, auth, config)
- Dependency updates across services
- Documentation updates
- Shared library updates
- Emergency fixes across services

❌ **Avoid for**:
- Unrelated changes in different repos
- Experimental work in one service
- When services need different commit messages
- When some repos need careful review

### Commit Message Guidelines

For multi-repo commits, use descriptive messages that apply to all repos:

✅ **Good messages**:
- "Add structured logging with correlation IDs"
- "Update to Python 3.11 and dependencies"
- "Implement rate limiting middleware"
- "Add Docker health checks to all services"

❌ **Avoid**:
- "Fix bug" (too vague)
- "Add feature to upload service" (single service)
- "WIP" (work in progress should be single-repo)

### Safety Features

The script includes safety checks:

1. **Confirmation prompt**: Always asks before committing to multiple repos
2. **Per-repo validation**: Each repo validated independently
3. **Failure isolation**: One repo failing doesn't stop others
4. **Summary report**: Shows successes and failures
5. **Rollback safe**: Each repo committed separately (can rollback individually)

## Integration with Workflows

### GitHub Actions

After pushing with `--push`, GitHub Actions workflows in each repository will trigger automatically:

```yaml
# .github/workflows/ci.yml in each repo
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

### Pre-commit Hooks

Compatible with pre-commit hooks in each repository:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: python-syntax
        name: Check Python Syntax
        entry: python3 -m py_compile
        language: system
        files: \.py$
```

### CI/CD Pipeline

Example integration in CI/CD:

```bash
#!/bin/bash
# deploy.sh

# Commit all changes
./dox-admin/scripts/rpa-commit.sh multi "Deploy ${VERSION}" --push

# Wait for workflows
echo "Waiting for CI/CD workflows..."
sleep 60

# Check workflow status
gh workflow list --all
```

## Troubleshooting

### Issue: Repos not detected

**Symptom**: `scan` doesn't show all repositories

**Solution**: Ensure repositories are in workspace root or one level deep:
```bash
/workspace/
  ├── dox-tmpl-pdf-upload/    # ✅ Detected
  ├── dox-mcp-server/          # ✅ Detected
  └── deep/
      └── nested-repo/         # ❌ Not detected (too deep)
```

### Issue: Push fails

**Symptom**: "Push failed (may need to set upstream)"

**Solution**: Set upstream branch for each repo:
```bash
cd dox-tmpl-pdf-upload
git push -u origin main
```

### Issue: Pre-commit checks fail

**Symptom**: "Pre-commit checks failed, skipping"

**Solution**: Fix issues in that repo:
```bash
cd failing-repo
./dox-admin/scripts/rpa-commit.sh check
# Fix the issues
```

### Issue: Wrong commit type detected

**Symptom**: Commit shows as "chore" but should be "feat"

**Solution**: Use single-repo mode for better control:
```bash
cd specific-repo
./dox-admin/scripts/rpa-commit.sh interactive
```

## Advanced Usage

### Selective Multi-Commit

Commit only to specific repositories:

```bash
# 1. See all repos
./rpa-commit.sh scan

# 2. Manually commit to selected repos
cd dox-tmpl-pdf-upload
./rpa-commit.sh quick "Update validation"
cd ../dox-mcp-server
./rpa-commit.sh quick "Update validation"

# 3. Push all at once
cd ../
./rpa-commit.sh push-all
```

### Dry Run

Check what would be committed without committing:

```bash
# Scan shows what has changes
./rpa-commit.sh scan

# Check each repo individually
for repo in dox-tmpl-pdf-upload dox-mcp-server; do
  cd "$repo"
  echo "=== $repo ==="
  git status --short
  cd ..
done
```

### Batch Operations

Combine with other git operations:

```bash
# Create feature branch in all repos
for repo in dox-*/; do
  cd "$repo"
  git checkout -b feature/new-validation
  cd ..
done

# Make changes...

# Commit to all
./rpa-commit.sh multi "Implement new validation"

# Push all
./rpa-commit.sh push-all
```

## Future Enhancements

Planned features:
- [ ] Filter repos by pattern (e.g., `--only dox-tmpl-*`)
- [ ] Exclude repos by pattern (e.g., `--exclude dox-admin`)
- [ ] Dry-run mode (`--dry-run`)
- [ ] Parallel commit execution
- [ ] Integration with PR creation (`gh pr create`)
- [ ] Rollback all commits in case of failures
- [ ] Custom commit message per repo type

---

**Status**: ✅ ACTIVE
**Last Updated**: 2025-11-03
**Version**: 2.0

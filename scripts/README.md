# Dox Platform - Development Scripts

Utility scripts for local development, testing, and automated workflows.

## Available Scripts

### 1. run-local.sh

**Purpose**: Run all Dox services locally with Docker Compose for development and testing.

**Usage**:
```bash
# Start all services
./run-local.sh start

# Start a specific service
./run-local.sh start dox-tmpl-pdf-upload

# Stop all services
./run-local.sh stop

# Restart a service
./run-local.sh restart dox-mcp-server

# Show status of all services
./run-local.sh status

# View logs for a service
./run-local.sh logs dox-tmpl-pdf-upload

# Run health checks
./run-local.sh health

# Show help
./run-local.sh help
```

**Features**:
- Automatic Docker availability check
- Environment file validation (.env setup)
- Infrastructure services startup (Redis, MSSQL)
- Service orchestration across multiple repositories
- Health check monitoring
- Colored console output for better readability

**Prerequisites**:
- Docker and Docker Compose installed
- .env files configured (will use .env.example if not found)
- Services cloned to workspace

**Services Managed**:
- dox-tmpl-pdf-upload (port 8080)
- dox-mcp-server (port 8081)
- dox-tmpl-pdf-recognizer (port 8082)
- Infrastructure (Redis, MSSQL, etc.)

---

### 2. rpa-commit.sh

**Purpose**: Automated commit workflow following RPA (Robotic Process Automation) standards with continuity tracking.

**Usage**:
```bash
# Interactive mode (prompts for details)
./rpa-commit.sh
./rpa-commit.sh interactive

# Quick commit with auto-detection
./rpa-commit.sh quick "Add PDF validation to upload service"

# Multi-repository commit (all repos with changes)
./rpa-commit.sh multi "Implement new feature"

# Multi-repository commit with auto-push
./rpa-commit.sh multi "Fix bug across services" --push

# Scan all repositories for changes and status
./rpa-commit.sh scan

# Push all repositories that are ahead of remote
./rpa-commit.sh push-all

# Check for uncommitted changes
./rpa-commit.sh check

# Show help
./rpa-commit.sh help
```

**Features**:
- **Multi-repository support**: Commit across all repos with changes at once
- **Branch detection**: Works with current branch in each repository
- **Ahead detection**: Identifies repos with unpushed commits
- Auto-detects commit type (feat/fix/docs/test/chore/refactor)
- Auto-detects service name from changed files
- Python syntax validation before commit
- Continuity file update verification
- Standardized commit message format
- Compyle attribution in commits
- Pre-commit checks for code quality
- Workflow integration ready

**Commit Message Format**:
```
<type>(<service>): <description>

Generated via RPA commit workflow.

Agent: <agent-id>
Timestamp: <timestamp>

🤖 Generated with Compyle

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Commit Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `chore`: Build/tooling changes
- `refactor`: Code refactoring

**Interactive Mode Example**:
```bash
$ ./rpa-commit.sh

[STEP] Current git status:
 M dox-tmpl-pdf-upload/app/main.py
 M dox-tmpl-pdf-upload/README.md

Commit type [feat/fix/docs/test/chore/refactor] (default: feat): feat
Service (default: dox-tmpl-pdf-upload):
Commit description: Add async lifespan management

Proceed with commit? [y/N]: y
[SUCCESS] Commit created successfully
```

**Quick Mode Example**:
```bash
$ ./rpa-commit.sh quick "Implement MCP server tools"

[INFO] Auto-detected: feat(dox-mcp-server)
[SUCCESS] Commit created successfully
```

**Pre-commit Checks**:
1. Python syntax validation for all .py files
2. Detection of new TODO/FIXME comments
3. Continuity file update verification (within last hour)
4. Git repository status check

**Known Issue**: The user mentioned there seems to be a bug with the RPA process in COMPYLE. This script implements defensive checks and validation to mitigate potential issues.

---

## Setup Instructions

### First Time Setup

1. **Make scripts executable**:
```bash
chmod +x dox-admin/scripts/*.sh
```

2. **Add scripts to PATH** (optional):
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/dox-admin/scripts"
```

3. **Configure environment files**:
```bash
# For each service, create .env from .env.example
cd dox-tmpl-pdf-upload && cp .env.example .env
cd ../dox-mcp-server && cp .env.example .env
# Edit .env files with your configuration
```

4. **Verify Docker installation**:
```bash
docker --version
docker-compose --version
```

---

## Workflow Examples

### Local Development Workflow

```bash
# 1. Start all services
./run-local.sh start

# 2. Check service status
./run-local.sh status

# 3. Run health checks
./run-local.sh health

# 4. Make code changes
vim ../dox-tmpl-pdf-upload/app/main.py

# 5. Restart affected service
./run-local.sh restart dox-tmpl-pdf-upload

# 6. View logs
./run-local.sh logs dox-tmpl-pdf-upload

# 7. Commit changes
./rpa-commit.sh quick "Fix async lifespan context"

# 8. Stop services when done
./run-local.sh stop
```

### Testing Workflow

```bash
# Start services
./run-local.sh start

# Wait for services to be ready
sleep 10

# Run health checks
./run-local.sh health

# Test API endpoints
curl http://localhost:8080/api/v1/health
curl http://localhost:8081/health

# View service logs
./run-local.sh logs dox-tmpl-pdf-upload

# Stop services
./run-local.sh stop
```

### Commit Workflow

```bash
# Check what has changed
./rpa-commit.sh check

# Option 1: Interactive commit
./rpa-commit.sh

# Option 2: Quick commit
./rpa-commit.sh quick "Your commit message"

# Push to remote
git push origin feature/your-branch

# Create pull request
gh pr create --title "Your PR title" --body "PR description"
```

---

## Troubleshooting

### Docker Issues

**Issue**: Docker daemon not running
```bash
# Start Docker Desktop or Docker service
sudo systemctl start docker  # Linux
open -a Docker              # macOS
```

**Issue**: Permission denied for Docker socket
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and log back in
```

### Service Issues

**Issue**: Service not starting
```bash
# Check logs
./run-local.sh logs SERVICE_NAME

# Check Docker Compose file
cd SERVICE_DIR
docker-compose config

# Rebuild containers
cd SERVICE_DIR
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Issue**: Port already in use
```bash
# Find process using port
lsof -i :8080
# Kill process or change port in .env
```

### Commit Issues

**Issue**: Python syntax errors preventing commit
```bash
# Check syntax manually
python3 -m py_compile path/to/file.py

# Fix errors and try again
```

**Issue**: Continuity file not updated warning
```bash
# Update continuity file
vi dox-admin/continuity/CONTINUITY_MEMORY.md

# Then commit
./rpa-commit.sh
```

---

## Configuration

### Environment Variables

Each script supports configuration via environment variables:

**run-local.sh**:
- `WORKSPACE_ROOT`: Root directory of all services (auto-detected)
- `DOCKER_COMPOSE`: docker-compose command to use (auto-detected)

**rpa-commit.sh**:
- `WORKSPACE_ROOT`: Root directory of all services (auto-detected)
- `CONTINUITY_FILE`: Path to continuity memory file

### Customization

To customize scripts:

1. Copy script to a new name
2. Modify variables at top of script
3. Keep original script as reference

---

## Best Practices

### Local Development
1. Always run health checks after starting services
2. Check logs if service doesn't respond
3. Stop services when not actively developing
4. Keep .env files up to date

### Committing
1. Update continuity file for significant changes
2. Review git status before committing
3. Use descriptive commit messages
4. Run health checks before committing
5. Create pull requests for review

### Multi-Service Development
1. Start only services you need
2. Use `status` command to monitor services
3. Restart individual services instead of all
4. Check service dependencies before stopping

---

## Script Maintenance

### Adding New Services

To add a new service to run-local.sh:

1. Add service to `services` array:
```bash
local services=("dox-tmpl-pdf-upload" "dox-mcp-server" "new-service")
```

2. Add health check endpoint:
```bash
if curl -s http://localhost:PORT/health > /dev/null 2>&1; then
    print_success "new-service: healthy"
fi
```

3. Document in README

### Updating RPA Workflow

To modify commit workflow:

1. Edit commit type detection in `determine_commit_type()`
2. Add service patterns in `determine_service()`
3. Customize commit message in `generate_commit_message()`
4. Add pre-commit checks in `run_pre_commit_checks()`

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review continuity documentation: `dox-admin/continuity/`
- Check agent protocol: `dox-admin/strategy/standards/MULTI_AGENT_COORDINATION.md`
- Contact Document Team

---

**Last Updated**: 2025-11-03
**Maintained By**: Document Team
**Status**: ✅ ACTIVE

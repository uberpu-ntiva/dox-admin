#!/bin/bash
# Dox Platform - RPA Commit Workflow
# Automated commit process following RPA standards

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOX_ADMIN="$WORKSPACE_ROOT/dox-admin"
CONTINUITY_FILE="$DOX_ADMIN/continuity/CONTINUITY_MEMORY.md"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
AGENT_ID="rpa-$(date +%Y%m%d-%H%M%S)"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${MAGENTA}[STEP]${NC} $1"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    print_success "Git repository detected"
}

# Function to check for uncommitted changes
check_uncommitted_changes() {
    if [ -z "$(git status --porcelain)" ]; then
        print_warning "No uncommitted changes found"
        return 1
    fi
    print_success "Uncommitted changes detected"
    return 0
}

# Function to show git status
show_git_status() {
    print_step "Current git status:"
    echo ""
    git status --short
    echo ""
}

# Function to determine commit type
determine_commit_type() {
    local changes=$(git status --porcelain)

    # Check what was changed
    if echo "$changes" | grep -q "^A.*\.py$\|^M.*\.py$"; then
        if echo "$changes" | grep -q "dox-tmpl-pdf-upload\|dox-mcp-server"; then
            echo "feat"
        elif echo "$changes" | grep -q "test"; then
            echo "test"
        else
            echo "feat"
        fi
    elif echo "$changes" | grep -q "README\|AGENTS\|\.md$"; then
        echo "docs"
    elif echo "$changes" | grep -q "Dockerfile\|docker-compose\|requirements\.txt"; then
        echo "chore"
    else
        echo "chore"
    fi
}

# Function to determine service name from changes
determine_service() {
    local changes=$(git status --porcelain)

    if echo "$changes" | grep -q "dox-tmpl-pdf-upload"; then
        echo "dox-tmpl-pdf-upload"
    elif echo "$changes" | grep -q "dox-mcp-server"; then
        echo "dox-mcp-server"
    elif echo "$changes" | grep -q "dox-tmpl-pdf-recognizer"; then
        echo "dox-tmpl-pdf-recognizer"
    elif echo "$changes" | grep -q "dox-admin"; then
        echo "dox-admin"
    else
        echo "multiple"
    fi
}

# Function to generate commit message
generate_commit_message() {
    local commit_type=$1
    local service=$2
    local description=$3

    cat << EOF
$commit_type($service): $description

Generated via RPA commit workflow.

Agent: $AGENT_ID
Timestamp: $TIMESTAMP

🤖 Generated with Compyle

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
}

# Function to check continuity update
check_continuity_update() {
    if [ ! -f "$CONTINUITY_FILE" ]; then
        print_warning "Continuity file not found: $CONTINUITY_FILE"
        return 1
    fi

    # Check if continuity was updated recently (within last hour)
    local last_modified=$(stat -c %Y "$CONTINUITY_FILE" 2>/dev/null || stat -f %m "$CONTINUITY_FILE" 2>/dev/null)
    local current_time=$(date +%s)
    local time_diff=$((current_time - last_modified))

    if [ $time_diff -gt 3600 ]; then
        print_warning "Continuity file not updated in the last hour"
        print_warning "Please update $CONTINUITY_FILE before committing"
        return 1
    fi

    print_success "Continuity file recently updated"
    return 0
}

# Function to run pre-commit checks
run_pre_commit_checks() {
    print_step "Running pre-commit checks..."

    # Check for Python syntax errors
    local python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
    if [ -n "$python_files" ]; then
        print_info "Checking Python syntax..."
        for file in $python_files; do
            if [ -f "$file" ]; then
                python3 -m py_compile "$file" 2>/dev/null || {
                    print_error "Syntax error in $file"
                    return 1
                }
            fi
        done
        print_success "Python syntax check passed"
    fi

    # Check for TODO/FIXME comments in new code
    local new_todos=$(git diff --cached | grep "^+.*TODO\|^+.*FIXME" || true)
    if [ -n "$new_todos" ]; then
        print_warning "New TODO/FIXME comments detected:"
        echo "$new_todos"
    fi

    print_success "Pre-commit checks passed"
    return 0
}

# Function to stage all changes
stage_all_changes() {
    print_step "Staging all changes..."
    git add -A
    print_success "All changes staged"
}

# Function to create commit
create_commit() {
    local commit_message=$1

    print_step "Creating commit..."
    echo "$commit_message" | git commit -F -

    if [ $? -eq 0 ]; then
        print_success "Commit created successfully"
        return 0
    else
        print_error "Failed to create commit"
        return 1
    fi
}

# Function to show commit summary
show_commit_summary() {
    print_step "Commit summary:"
    echo ""
    git log -1 --stat
    echo ""
}

# Function to suggest next steps
suggest_next_steps() {
    local current_branch=$(git branch --show-current)

    cat << EOF
${GREEN}========================================${NC}
${GREEN}Commit completed successfully!${NC}
${GREEN}========================================${NC}

Current branch: ${BLUE}$current_branch${NC}

${YELLOW}Suggested next steps:${NC}

1. Review your commit:
   ${BLUE}git log -1 --stat${NC}

2. If satisfied, push to remote:
   ${BLUE}git push origin $current_branch${NC}

3. If working on a feature branch, create a pull request:
   ${BLUE}gh pr create --title "Your PR title" --body "PR description"${NC}

4. Update continuity if not done:
   ${BLUE}vi $CONTINUITY_FILE${NC}

5. Check service status:
   ${BLUE}$DOX_ADMIN/scripts/run-local.sh status${NC}

EOF
}

# Interactive mode - ask user for commit details
interactive_commit() {
    print_step "=== Interactive RPA Commit Workflow ==="
    echo ""

    # Show status
    show_git_status

    # Determine defaults
    local default_type=$(determine_commit_type)
    local default_service=$(determine_service)

    # Ask for commit type
    echo -ne "${BLUE}Commit type${NC} [feat/fix/docs/test/chore/refactor] (default: $default_type): "
    read commit_type
    commit_type=${commit_type:-$default_type}

    # Ask for service
    echo -ne "${BLUE}Service${NC} (default: $default_service): "
    read service
    service=${service:-$default_service}

    # Ask for description
    echo -ne "${BLUE}Commit description${NC}: "
    read description

    if [ -z "$description" ]; then
        print_error "Description is required"
        exit 1
    fi

    # Confirm
    echo ""
    print_step "Commit preview:"
    echo -e "${MAGENTA}Type:${NC} $commit_type"
    echo -e "${MAGENTA}Service:${NC} $service"
    echo -e "${MAGENTA}Description:${NC} $description"
    echo ""
    echo -ne "${YELLOW}Proceed with commit?${NC} [y/N]: "
    read confirm

    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_warning "Commit cancelled"
        exit 0
    fi

    # Generate commit message
    local commit_message=$(generate_commit_message "$commit_type" "$service" "$description")

    # Stage changes
    stage_all_changes

    # Run pre-commit checks
    run_pre_commit_checks || {
        print_error "Pre-commit checks failed"
        exit 1
    }

    # Check continuity
    check_continuity_update || {
        print_warning "Consider updating continuity file"
    }

    # Create commit
    create_commit "$commit_message" || {
        print_error "Commit failed"
        exit 1
    }

    # Show summary
    show_commit_summary

    # Suggest next steps
    suggest_next_steps
}

# Quick commit mode - auto-determine everything
quick_commit() {
    local description=$1

    if [ -z "$description" ]; then
        print_error "Description required for quick commit"
        echo "Usage: $0 quick \"Your commit description\""
        exit 1
    fi

    print_step "=== Quick RPA Commit ==="
    echo ""

    # Auto-determine type and service
    local commit_type=$(determine_commit_type)
    local service=$(determine_service)

    print_info "Auto-detected: $commit_type($service)"
    echo ""

    # Show status
    show_git_status

    # Generate commit message
    local commit_message=$(generate_commit_message "$commit_type" "$service" "$description")

    # Stage changes
    stage_all_changes

    # Run pre-commit checks
    run_pre_commit_checks || {
        print_error "Pre-commit checks failed"
        exit 1
    }

    # Create commit
    create_commit "$commit_message" || {
        print_error "Commit failed"
        exit 1
    }

    # Show summary
    show_commit_summary

    print_success "Quick commit completed!"
}

# Function to show help
show_help() {
    cat << EOF
Dox Platform - RPA Commit Workflow

Automated commit process following RPA standards and best practices.

Usage: $0 [MODE] [OPTIONS]

Modes:
    interactive     Interactive mode - prompts for commit details (default)
    quick "msg"     Quick mode - auto-detect type/service, use provided message
    check           Check if there are changes to commit
    help            Show this help message

Examples:
    $0                                          # Interactive mode
    $0 interactive                              # Interactive mode (explicit)
    $0 quick "Add PDF validation to upload"     # Quick commit with message
    $0 check                                    # Check for uncommitted changes

Features:
    • Auto-detects commit type (feat/fix/docs/etc.)
    • Auto-detects service name from changed files
    • Runs Python syntax checks
    • Checks continuity file updates
    • Generates standardized commit messages
    • Adds Compyle attribution

Commit Message Format:
    <type>(<service>): <description>

    Generated via RPA commit workflow.

    Agent: <agent-id>
    Timestamp: <timestamp>

    🤖 Generated with Compyle

    Co-Authored-By: Claude <noreply@anthropic.com>

Commit Types:
    feat        New feature
    fix         Bug fix
    docs        Documentation changes
    test        Test additions/changes
    chore       Build/tooling changes
    refactor    Code refactoring

EOF
}

# Main script logic
main() {
    local mode=${1:-interactive}

    # Check git repository
    check_git_repo

    # Check for changes
    if ! check_uncommitted_changes; then
        if [ "$mode" != "check" ]; then
            exit 0
        fi
    fi

    case "$mode" in
        interactive|"")
            interactive_commit
            ;;
        quick)
            quick_commit "$2"
            ;;
        check)
            check_uncommitted_changes
            if [ $? -eq 0 ]; then
                show_git_status
                print_success "Ready to commit"
            else
                print_info "No changes to commit"
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown mode: $mode"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

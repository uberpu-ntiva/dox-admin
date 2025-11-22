#!/bin/bash
# Dox Platform - Local Development Runner
# Run all services locally with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOX_ADMIN="$WORKSPACE_ROOT/dox-admin"
LOG_DIR="$DOX_ADMIN/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        print_error "docker-compose is not available. Please install it."
        exit 1
    fi
    print_success "Using: $DOCKER_COMPOSE"
}

# Function to check .env files
check_env_files() {
    local services=("dox-tmpl-pdf-upload" "dox-mcp-server" "dox-tmpl-pdf-recognizer")

    for service in "${services[@]}"; do
        local service_dir="$WORKSPACE_ROOT/$service"
        if [ -d "$service_dir" ]; then
            if [ ! -f "$service_dir/.env" ]; then
                if [ -f "$service_dir/.env.example" ]; then
                    print_warning "$service: .env not found, copying from .env.example"
                    cp "$service_dir/.env.example" "$service_dir/.env"
                else
                    print_warning "$service: .env not found (and no .env.example)"
                fi
            else
                print_success "$service: .env exists"
            fi
        fi
    done
}

# Function to start infrastructure services
start_infrastructure() {
    print_info "Starting infrastructure services (Redis, MSSQL, etc.)..."

    # Check if infrastructure docker-compose exists
    if [ -f "$DOX_ADMIN/docker/infrastructure.yml" ]; then
        cd "$DOX_ADMIN/docker"
        $DOCKER_COMPOSE -f infrastructure.yml up -d
        print_success "Infrastructure services started"
    else
        print_warning "No infrastructure.yml found, skipping infrastructure startup"
    fi
}

# Function to start a specific service
start_service() {
    local service_name=$1
    local service_dir="$WORKSPACE_ROOT/$service_name"

    if [ ! -d "$service_dir" ]; then
        print_warning "$service_name not found at $service_dir, skipping"
        return
    fi

    print_info "Starting $service_name..."
    cd "$service_dir"

    if [ -f "docker-compose.yml" ]; then
        $DOCKER_COMPOSE up -d
        print_success "$service_name started"
    else
        print_warning "$service_name has no docker-compose.yml, skipping"
    fi
}

# Function to show service status
show_status() {
    print_info "Service Status:"
    echo ""

    local services=("dox-tmpl-pdf-upload" "dox-mcp-server" "dox-tmpl-pdf-recognizer")

    for service in "${services[@]}"; do
        local service_dir="$WORKSPACE_ROOT/$service"
        if [ -d "$service_dir" ]; then
            cd "$service_dir"
            if [ -f "docker-compose.yml" ]; then
                echo -e "${BLUE}=== $service ===${NC}"
                $DOCKER_COMPOSE ps
                echo ""
            fi
        fi
    done
}

# Function to show service logs
show_logs() {
    local service_name=$1
    local service_dir="$WORKSPACE_ROOT/$service_name"

    if [ ! -d "$service_dir" ]; then
        print_error "$service_name not found"
        exit 1
    fi

    cd "$service_dir"
    if [ -f "docker-compose.yml" ]; then
        $DOCKER_COMPOSE logs -f
    else
        print_error "$service_name has no docker-compose.yml"
        exit 1
    fi
}

# Function to stop all services
stop_all() {
    print_info "Stopping all services..."

    local services=("dox-tmpl-pdf-upload" "dox-mcp-server" "dox-tmpl-pdf-recognizer")

    for service in "${services[@]}"; do
        local service_dir="$WORKSPACE_ROOT/$service"
        if [ -d "$service_dir" ] && [ -f "$service_dir/docker-compose.yml" ]; then
            print_info "Stopping $service..."
            cd "$service_dir"
            $DOCKER_COMPOSE down
        fi
    done

    # Stop infrastructure
    if [ -f "$DOX_ADMIN/docker/infrastructure.yml" ]; then
        print_info "Stopping infrastructure services..."
        cd "$DOX_ADMIN/docker"
        $DOCKER_COMPOSE -f infrastructure.yml down
    fi

    print_success "All services stopped"
}

# Function to restart a service
restart_service() {
    local service_name=$1
    local service_dir="$WORKSPACE_ROOT/$service_name"

    if [ ! -d "$service_dir" ]; then
        print_error "$service_name not found"
        exit 1
    fi

    print_info "Restarting $service_name..."
    cd "$service_dir"

    if [ -f "docker-compose.yml" ]; then
        $DOCKER_COMPOSE restart
        print_success "$service_name restarted"
    else
        print_error "$service_name has no docker-compose.yml"
        exit 1
    fi
}

# Function to run health checks
run_health_checks() {
    print_info "Running health checks..."
    echo ""

    # dox-tmpl-pdf-upload
    print_info "Checking dox-tmpl-pdf-upload..."
    if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
        print_success "dox-tmpl-pdf-upload: healthy"
    else
        print_error "dox-tmpl-pdf-upload: not responding"
    fi

    # dox-mcp-server
    print_info "Checking dox-mcp-server..."
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        print_success "dox-mcp-server: healthy"
    else
        print_error "dox-mcp-server: not responding"
    fi

    # dox-tmpl-pdf-recognizer (if present)
    print_info "Checking dox-tmpl-pdf-recognizer..."
    if curl -s http://localhost:8082/health > /dev/null 2>&1; then
        print_success "dox-tmpl-pdf-recognizer: healthy"
    else
        print_warning "dox-tmpl-pdf-recognizer: not responding"
    fi
}

# Function to show help
show_help() {
    cat << EOF
Dox Platform - Local Development Runner

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    start [SERVICE]     Start all services or a specific service
    stop                Stop all services
    restart SERVICE     Restart a specific service
    status              Show status of all services
    logs SERVICE        Show logs for a specific service
    health              Run health checks on all services
    help                Show this help message

Services:
    dox-tmpl-pdf-upload         PDF template upload service
    dox-mcp-server              MCP server for AI integration
    dox-tmpl-pdf-recognizer     PDF recognition service

Examples:
    $0 start                          # Start all services
    $0 start dox-tmpl-pdf-upload     # Start only pdf-upload service
    $0 logs dox-mcp-server           # Show MCP server logs
    $0 restart dox-tmpl-pdf-upload   # Restart pdf-upload service
    $0 stop                          # Stop all services
    $0 health                        # Check health of all services

EOF
}

# Main script logic
main() {
    local command=${1:-help}
    local service=$2

    # Always check Docker first
    check_docker
    check_docker_compose

    case "$command" in
        start)
            check_env_files
            if [ -z "$service" ]; then
                print_info "Starting all services..."
                start_infrastructure
                start_service "dox-tmpl-pdf-upload"
                start_service "dox-mcp-server"
                start_service "dox-tmpl-pdf-recognizer"
                echo ""
                show_status
                echo ""
                print_info "Waiting 5 seconds for services to start..."
                sleep 5
                run_health_checks
            else
                start_service "$service"
            fi
            ;;
        stop)
            stop_all
            ;;
        restart)
            if [ -z "$service" ]; then
                print_error "Please specify a service to restart"
                echo "Usage: $0 restart SERVICE"
                exit 1
            fi
            restart_service "$service"
            ;;
        status)
            show_status
            ;;
        logs)
            if [ -z "$service" ]; then
                print_error "Please specify a service"
                echo "Usage: $0 logs SERVICE"
                exit 1
            fi
            show_logs "$service"
            ;;
        health)
            run_health_checks
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

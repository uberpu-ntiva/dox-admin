.PHONY: help install dev run test build push deploy-azure deploy-aws clean logs lint format

# Variables
SERVICE_NAME := [service-name]
REGISTRY := [registry.azurecr.io or ecr.aws.com]
IMAGE := $(REGISTRY)/$(SERVICE_NAME)
VERSION := 1.0.0
PYTHON := python3
VENV := venv

help:
	@echo "Pact Platform - $(SERVICE_NAME)"
	@echo ""
	@echo "Available targets:"
	@echo "  install         - Install development dependencies"
	@echo "  dev             - Start local development environment"
	@echo "  run             - Run application locally"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration- Run integration tests only"
	@echo "  test-e2e        - Run E2E tests only"
	@echo "  coverage        - Generate coverage report"
	@echo "  lint            - Run code linting (flake8)"
	@echo "  format          - Format code (black, isort)"
	@echo "  build           - Build Docker image"
	@echo "  push            - Push Docker image to registry"
	@echo "  deploy-azure    - Deploy to Azure App Service"
	@echo "  deploy-aws      - Deploy to AWS ECS Fargate"
	@echo "  docker-up       - Start docker-compose services"
	@echo "  docker-down     - Stop docker-compose services"
	@echo "  logs            - View application logs"
	@echo "  clean           - Clean up temporary files"
	@echo "  swagger         - Start Swagger UI for API docs"

# Development Setup
install:
	@echo "Installing dependencies..."
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -r app/requirements.txt
	@echo "✓ Dependencies installed"

dev: docker-up
	@echo "Development environment started"
	@echo "Access service at: http://localhost:5000"

run:
	@echo "Starting $(SERVICE_NAME) locally..."
	. $(VENV)/bin/activate && export FLASK_ENV=development && \
	export FLASK_DEBUG=True && cd app && flask run --host=0.0.0.0 --port=5000

# Testing
test:
	@echo "Running all tests..."
	. $(VENV)/bin/activate && pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:
	@echo "Running unit tests..."
	. $(VENV)/bin/activate && pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	. $(VENV)/bin/activate && pytest tests/integration/ -v

test-e2e:
	@echo "Running E2E tests..."
	. $(VENV)/bin/activate && pytest tests/e2e/ -v

coverage:
	@echo "Generating coverage report..."
	. $(VENV)/bin/activate && pytest tests/ --cov=app --cov-report=html
	@echo "Coverage report generated: htmlcov/index.html"

# Code Quality
lint:
	@echo "Running linting checks..."
	. $(VENV)/bin/activate && flake8 app/ tests/ --max-line-length=100
	@echo "✓ Lint check passed"

format:
	@echo "Formatting code..."
	. $(VENV)/bin/activate && black app/ tests/
	. $(VENV)/bin/activate && isort app/ tests/
	@echo "✓ Code formatted"

# Docker
build:
	@echo "Building Docker image: $(IMAGE):$(VERSION)"
	docker build -t $(IMAGE):$(VERSION) .
	docker tag $(IMAGE):$(VERSION) $(IMAGE):latest
	@echo "✓ Docker image built"

push: build
	@echo "Pushing Docker image to registry..."
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest
	@echo "✓ Docker image pushed"

docker-up:
	@echo "Starting docker-compose environment..."
	docker-compose up -d
	@echo "✓ Services running"
	@echo "  App: http://localhost:5000"
	@echo "  DB: localhost:5432"
	@echo "  Redis: localhost:6379"

docker-down:
	@echo "Stopping docker-compose environment..."
	docker-compose down
	@echo "✓ Services stopped"

docker-logs:
	@docker-compose logs -f app

docker-shell:
	@docker-compose exec app /bin/bash

docker-db-shell:
	@docker-compose exec db psql -U pact -d $(SERVICE_NAME)

# Deployment
deploy-azure:
	@echo "Deploying to Azure App Service..."
	@echo "Make sure you have Azure CLI installed: az"
	az webapp deployment source config-zip \
		--resource-group [resource-group] \
		--name [app-service-name] \
		--src-path deployment.zip
	@echo "✓ Deployed to Azure"

deploy-aws:
	@echo "Deploying to AWS ECS Fargate..."
	@echo "Make sure you have AWS CLI installed: aws"
	aws ecs update-service \
		--cluster [cluster-name] \
		--service $(SERVICE_NAME) \
		--force-new-deployment
	@echo "✓ Deployed to AWS"

# Utilities
logs:
	@docker-compose logs -f app

swagger:
	@echo "Starting Swagger UI..."
	@echo "Open: http://localhost:8080"
	docker run -p 8080:8080 \
		-e SWAGGER_JSON=/swagger/openapi.yaml \
		-v $(PWD)/docs:/swagger:ro \
		swaggerapi/swagger-ui

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/ dist/ *.egg-info
	docker-compose down --volumes
	@echo "✓ Cleanup complete"

# Git helpers
git-status:
	@git status

git-branch-current:
	@git rev-parse --abbrev-ref HEAD

# Quick start
quick-start: install docker-up test
	@echo "✓ Quick start complete!"
	@echo "  1. Development environment running"
	@echo "  2. All tests passing"
	@echo "  3. Ready to start development"

# Watch file changes and run tests
watch-tests:
	@echo "Watching for changes and running tests..."
	. $(VENV)/bin/activate && ptw

# Environment info
info:
	@echo "Pact Platform - $(SERVICE_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Registry: $(REGISTRY)"
	@echo "Image: $(IMAGE)"
	@echo ""
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"


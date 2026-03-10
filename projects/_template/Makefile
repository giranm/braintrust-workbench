# Makefile for {{Project Name}}
# Unified command interface for Docker-based development

.PHONY: help setup build up down logs shell test clean rebuild

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "{{Project Name}} - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup
setup: ## Create .env file from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file. Please edit it with your API keys."; \
	else \
		echo "✗ .env file already exists."; \
	fi

# Docker commands
build: ## Build Docker images
	docker compose build

up: ## Start containers in foreground
	docker compose up

up-d: ## Start containers in background (detached)
	docker compose up -d

down: ## Stop and remove containers
	docker compose down

down-v: ## Stop and remove containers and volumes
	docker compose down -v

restart: ## Restart containers
	docker compose restart

stop: ## Stop containers without removing
	docker compose stop

# Logs
logs: ## Show logs (follow mode)
	docker compose logs -f

logs-backend: ## Show backend logs only
	docker compose logs -f backend

logs-frontend: ## Show frontend logs only
	docker compose logs -f frontend

# Development
shell-backend: ## Open shell in backend container
	docker compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend /bin/sh

python: ## Open Python REPL in backend container
	docker compose exec backend python

# Testing
test: ## Run all tests
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend: ## Run backend tests
	docker compose exec backend pytest

test-frontend: ## Run frontend tests
	docker compose exec frontend npm test

# Maintenance
clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi all
	docker system prune -f

rebuild: ## Rebuild from scratch
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

rebuild-up: ## Rebuild and start in foreground
	docker compose down -v
	docker compose build --no-cache
	docker compose up

# Monitoring
ps: ## Show running containers
	docker compose ps

stats: ## Show container resource usage
	docker stats

health: ## Check container health
	@echo "Backend health:"
	@docker compose ps backend --format json | jq -r '.[0].Health // "N/A"'
	@echo "Frontend health:"
	@docker compose ps frontend --format json | jq -r '.[0].Health // "N/A"'

# Local development (non-Docker)
local-install-backend: ## Install backend dependencies locally with UV
	cd backend && uv sync

local-install-frontend: ## Install frontend dependencies locally
	cd frontend && npm install

local-run-backend: ## Run backend locally
	cd backend && uv run uvicorn src.main:app --reload

local-run-frontend: ## Run frontend locally
	cd frontend && npm run dev

local-test-backend: ## Run backend tests locally
	cd backend && uv run pytest

local-test-frontend: ## Run frontend tests locally
	cd frontend && npm test

# Database (if applicable)
db-shell: ## Open database shell
	docker compose exec backend python -c "from src.db import get_session; print('Database connection ready')"

# Backup and restore
backup: ## Backup application data
	@mkdir -p backups
	docker run --rm \
		-v {{project-name}}_backend-data:/data \
		-v $(PWD)/backups:/backup \
		alpine tar czf /backup/data-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✓ Backup created in backups/"

restore: ## Restore application data (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: Please specify BACKUP_FILE=path/to/backup.tar.gz"; \
		exit 1; \
	fi
	docker run --rm \
		-v {{project-name}}_backend-data:/data \
		-v $(PWD)/backups:/backup \
		alpine tar xzf /backup/$(BACKUP_FILE) -C /data
	@echo "✓ Backup restored"

# Production
prod-build: ## Build production images
	docker compose build --no-cache

prod-up: ## Start in production mode
	ENVIRONMENT=production docker compose up -d

prod-down: ## Stop production containers
	docker compose down

# Documentation
docs: ## Open documentation in browser
	@echo "Opening documentation..."
	@if command -v open > /dev/null; then \
		open README.md; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open README.md; \
	else \
		echo "Please open README.md manually"; \
	fi

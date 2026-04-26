# Makefile for {{Project Name}}
# Unified command interface for Docker-based development

.PHONY: help setup build up down logs shell test clean rebuild

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "{{Project Name}} - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create .env file from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi

build: ## Build Docker images
	docker compose build

up: ## Start containers in foreground
	docker compose up

up-d: ## Start containers in background
	docker compose up -d

down: ## Stop and remove containers
	docker compose down

down-v: ## Stop and remove containers and volumes
	docker compose down -v

restart: ## Restart containers
	docker compose restart

stop: ## Stop containers without removing
	docker compose stop

logs: ## Show logs
	docker compose logs -f

logs-backend: ## Show backend logs only
	docker compose logs -f backend

logs-frontend: ## Show frontend logs only
	docker compose logs -f frontend

shell-backend: ## Open shell in backend container
	docker compose exec backend /bin/bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend /bin/sh

python: ## Open Python REPL in backend container
	docker compose exec backend python

test: ## Run all tests
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend: ## Run backend tests
	docker compose exec backend pytest

test-frontend: ## Run frontend tests
	docker compose exec frontend pnpm test

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

ps: ## Show running containers
	docker compose ps

stats: ## Show container resource usage
	docker stats

health: ## Check container health
	@echo "Backend health:"
	@docker compose ps backend --format json | jq -r '.[0].Health // \"N/A\"'
	@echo "Frontend health:"
	@docker compose ps frontend --format json | jq -r '.[0].Health // \"N/A\"'

local-install-backend: ## Install backend dependencies locally with UV
	cd backend && uv sync

local-install-frontend: ## Install frontend dependencies locally
	cd frontend && pnpm install

local-run-backend: ## Run backend locally
	cd backend && uv run uvicorn src.main:app --reload

local-run-frontend: ## Run frontend locally
	cd frontend && pnpm dev

local-test-backend: ## Run backend tests locally
	cd backend && uv run pytest

local-test-frontend: ## Run frontend tests locally
	cd frontend && pnpm test

db-shell: ## Open database shell
	docker compose exec backend python -c "from src.db import get_session; print('Database connection ready')"

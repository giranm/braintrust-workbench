# Makefile for Weather Chat Demo

.PHONY: help setup build up down logs shell test clean rebuild

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Weather Chat Demo - Make Commands"
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

logs-app: ## Show app logs only
	docker compose logs -f app

# Development
shell: ## Open shell in app container
	docker compose exec app /bin/bash

python: ## Open Python REPL in container
	docker compose exec app uv run python

test: ## Run tests in container
	docker compose exec app uv run pytest

test-weather: ## Test weather tool
	docker compose exec app uv run python -c "\
		import asyncio; \
		from src.tools.weather import get_weather_for_city, format_weather_response; \
		weather = asyncio.run(get_weather_for_city('London')); \
		print(format_weather_response(weather))"

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
	docker compose ps app --format json | jq -r '.[0].Health'

# Local development (non-Docker)
local-install: ## Install dependencies locally with UV
	uv sync

local-run: ## Run app locally with UV
	uv run reflex run

local-test: ## Run tests locally
	uv run pytest

local-weather: ## Test weather tool locally
	uv run python -c "\
		import asyncio; \
		from src.tools.weather import get_weather_for_city, format_weather_response; \
		weather = asyncio.run(get_weather_for_city('Tokyo')); \
		print(format_weather_response(weather))"

# Production
prod-build: ## Build production image
	docker compose -f docker-compose.yml build --target prod

prod-up: ## Start in production mode
	REFLEX_ENV=prod docker compose up -d

# Backup and restore
backup: ## Backup Reflex database
	@mkdir -p backups
	docker run --rm \
		-v multi-agent-chat-demo_reflex-db:/data \
		-v $(PWD)/backups:/backup \
		alpine tar czf /backup/reflex-db-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✓ Backup created in backups/"

restore: ## Restore Reflex database (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: Please specify BACKUP_FILE=path/to/backup.tar.gz"; \
		exit 1; \
	fi
	docker run --rm \
		-v multi-agent-chat-demo_reflex-db:/data \
		-v $(PWD)/backups:/backup \
		alpine tar xzf /backup/$(BACKUP_FILE) -C /data
	@echo "✓ Backup restored"

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

docker-docs: ## Open Docker documentation
	@if command -v open > /dev/null; then \
		open DOCKER.md; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open DOCKER.md; \
	else \
		echo "Please open DOCKER.md manually"; \
	fi

.PHONY: help install setup setup-automations run cli eval test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install mise tools and Python dependencies
	mise install
	mise trust
	uv sync

setup: ## Create .env from template (if not exists)
	@test -f .env || (cp .env.example .env && echo "Created .env — edit it with your API keys")
	@test -f .env && echo ".env already exists"

setup-automations: ## Provision Braintrust online scoring automations
	uv run python src/automations.py

run: ## Run the scripted demo scenario
	uv run python src/main.py

cli: ## Start the interactive CLI client
	uv run python src/cli.py

cli-verbose: ## Start the CLI with verbose output (shows routing and tool calls)
	uv run python src/cli.py --verbose

eval: ## Run the offline Braintrust evaluation suite
	uv run braintrust eval src/eval.py

test: ## Run pytest
	uv run pytest

lint: ## Run ruff linter
	uv run ruff check src/ tests/

clean: ## Remove build artifacts and caches
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

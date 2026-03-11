.PHONY: help setup build deploy-infra deploy-lambda deploy test logs logs-recent logs-errors clean destroy

# Load .env and auto-export TF_VAR_ aliases so users only configure values once
define LOAD_ENV
set -a && . ./.env && set +a && \
export TF_VAR_AWS_PROFILE="$$AWS_PROFILE" && \
export TF_VAR_AWS_REGION="$$AWS_REGION" && \
export TF_VAR_BRAINTRUST_API_KEY="$$BRAINTRUST_API_KEY" && \
export TF_VAR_BRAINTRUST_PROJECT_ID="$$BRAINTRUST_PROJECT_ID" && \
export TF_VAR_OPENAI_API_KEY="$$OPENAI_API_KEY" && \
export TF_VAR_ENVIRONMENT="$$ENVIRONMENT" && \
export TF_VAR_PROJECT_NAME="$$PROJECT_NAME" && \
export TF_VAR_FUNCTION_NAME="$$FUNCTION_NAME" && \
export TF_VAR_OWNER="$$OWNER"
endef

# Default target
help:
	@echo "Braintrust Multi-Turn Lambda Tracing - Makefile Commands"
	@echo ""
	@echo "Setup & Configuration:"
	@echo "  make setup          - Install runtime versions and initialize project"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build          - Build Lambda function"
	@echo "  make deploy-infra   - Deploy AWS infrastructure with Terraform"
	@echo "  make deploy-lambda  - Deploy Lambda function code"
	@echo "  make deploy         - Build and deploy Lambda (after infra exists)"
	@echo ""
	@echo "Testing & Debugging:"
	@echo "  make start-client   - Run Python client for testing"
	@echo "  make logs           - Tail Lambda CloudWatch logs (live)"
	@echo "  make logs-recent    - Show last 10 minutes of logs"
	@echo "  make logs-errors    - Show only error logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make destroy        - Destroy all AWS infrastructure"

# Install runtime versions and initialize project
setup:
	@echo "Installing runtime versions with mise..."
	mise install
	@echo "Installing Python dependencies with uv..."
	uv sync
	@echo "Installing Lambda dependencies..."
	cd lambda && npm install
	@echo "Initializing Terraform..."
	cd terraform && terraform init
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make deploy-infra' to create AWS resources"
	@echo "  2. Run 'make deploy-lambda' to deploy Lambda code"
	@echo "  3. Run 'make start-client' to start the conversation client"

# Build Lambda function
build:
	@echo "Building Lambda function..."
	cd lambda && npm run build
	@echo "✓ Build complete!"

# Deploy AWS infrastructure
deploy-infra:
	@echo "Deploying AWS infrastructure..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Copy .env.example to .env and configure it."; \
		exit 1; \
	fi
	@echo "Loading environment variables from .env..."
	@$(LOAD_ENV) && cd terraform && terraform plan
	@echo ""
	@read -p "Apply this plan? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(LOAD_ENV) && cd terraform && terraform apply; \
	else \
		echo "Deployment cancelled."; \
	fi

# Deploy Lambda function code
deploy-lambda:
	@echo "Deploying Lambda function code..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Copy .env.example to .env and configure it."; \
		exit 1; \
	fi
	@echo "Building TypeScript..."
	cd lambda && npm run build
	@echo "Creating deployment package with dependencies..."
	rm -f lambda/function.zip
	cd lambda && zip -rq function.zip node_modules/
	cd lambda/dist && zip -rq ../function.zip .
	@echo "Uploading to Lambda..."
	@$(LOAD_ENV) && cd lambda && aws lambda update-function-code \
		--function-name $$(cd ../terraform && terraform output -raw lambda_function_name) \
		--zip-file fileb://function.zip \
		--profile $$AWS_PROFILE \
		--no-cli-pager
	@echo "✓ Lambda deployed!"

# Build and deploy Lambda
deploy: build deploy-lambda

# Run Python client for testing
start-client:
	@echo "Starting conversation client..."
	@echo "(Type 'exit' to quit, 'reset' for new conversation, 'info' for details)"
	@echo ""
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Copy .env.example to .env and configure it."; \
		exit 1; \
	fi
	@$(LOAD_ENV) && uv run client.py \
		--function $$(cd terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "dev-braintrust-multi-turn-conversation-lambda") \
		--profile $$AWS_PROFILE \
		--region $$AWS_REGION

# View Lambda CloudWatch logs (recent)
logs:
	@echo "Fetching recent Lambda logs..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found."; \
		exit 1; \
	fi
	@$(LOAD_ENV) && \
	aws logs tail /aws/lambda/$$(cd terraform && terraform output -raw lambda_function_name) \
		--follow \
		--profile $$AWS_PROFILE \
		--region $$AWS_REGION \
		--format short

# View Lambda logs (last 10 minutes, no follow)
logs-recent:
	@echo "Fetching Lambda logs from last 10 minutes..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found."; \
		exit 1; \
	fi
	@$(LOAD_ENV) && \
	aws logs tail /aws/lambda/$$(cd terraform && terraform output -raw lambda_function_name) \
		--since 10m \
		--profile $$AWS_PROFILE \
		--region $$AWS_REGION \
		--format short

# View Lambda errors only
logs-errors:
	@echo "Fetching Lambda error logs..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found."; \
		exit 1; \
	fi
	@$(LOAD_ENV) && \
	aws logs tail /aws/lambda/$$(cd terraform && terraform output -raw lambda_function_name) \
		--since 10m \
		--profile $$AWS_PROFILE \
		--region $$AWS_REGION \
		--format short \
		--filter-pattern "ERROR"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf lambda/dist
	rm -f lambda/function.zip
	rm -rf lambda/node_modules
	cd terraform && rm -f lambda_placeholder.zip
	cd terraform && rm -rf placeholder
	@echo "✓ Clean complete!"

# Destroy all infrastructure
destroy:
	@echo "⚠️  WARNING: This will destroy all AWS resources!"
	@echo "Resources to be destroyed:"
	@cd terraform && terraform show 2>/dev/null | grep "resource" || echo "  - Lambda function"
	@echo "  - DynamoDB table"
	@echo "  - IAM roles and policies"
	@echo "  - CloudWatch Log Groups"
	@echo ""
	@read -p "Are you sure you want to destroy everything? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		cd terraform && terraform destroy; \
		echo "✓ Infrastructure destroyed!"; \
	else \
		echo "Destroy cancelled."; \
	fi

# Show Terraform outputs
outputs:
	@if [ -f .env ]; then \
		$(LOAD_ENV) && cd terraform && terraform output; \
	else \
		cd terraform && terraform output; \
	fi

# Validate Terraform configuration
validate:
	@echo "Validating Terraform configuration..."
	@if [ -f .env ]; then \
		$(LOAD_ENV) && cd terraform && terraform validate; \
	else \
		cd terraform && terraform validate; \
	fi
	@echo "✓ Terraform configuration is valid!"

# Format Terraform files
format:
	@echo "Formatting Terraform files..."
	cd terraform && terraform fmt -recursive
	@echo "✓ Formatting complete!"

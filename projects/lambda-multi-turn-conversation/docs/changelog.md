# Changelog - Lambda Multi-Turn Conversation

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No unreleased changes._

---

## [1.2.0] - 2026-03-10

### Changed
- Migrated from `sandbox` to `braintrust-workbench/projects/lambda-multi-turn-conversation/`
- Consolidated 5 source markdown files (PLAN.md, CHANGES.md, ENV-SETUP-GUIDE.md, NAMING-CONVENTION.md, README.md) into workbench `docs/` structure
- Rewrote `CLAUDE.md` with actual tech stack and Braintrust patterns
- Created project-level `.gitignore` for terraform state and deploy artifacts
- Updated project structure to include `docs/` directory

---

## [1.1.0] - 2026-03-10

### Added
- Real OpenAI API integration using `gpt-4o-mini` model
- `wrapOpenAI()` from Braintrust for automatic LLM call tracing
- `OPENAI_API_KEY` environment variable and Terraform variable
- OpenAI dependency in `lambda/package.json` (`openai@^4.77.0`)

### Changed
- Replaced mock `callLLM()` function with real OpenAI API calls
- Token counts now reflect actual OpenAI usage
- Updated `.env.example` with OpenAI configuration
- Updated Terraform Lambda environment variables to include `OPENAI_API_KEY`

---

## [1.0.0] - 2026-03-10

### Added
- **Lambda Function** (Node.js 20/TypeScript)
  - Multi-turn conversation handler with Braintrust tracing
  - `initLogger({ asyncFlush: false })` for reliable Lambda flushing
  - `traced()` with `parent` parameter for cross-invocation span linking
  - `span.export()` for state persistence via DynamoDB
  - Root "conversation" span with nested turn spans
- **DynamoDB Table**
  - Conversation state storage (conversation_id, root_span_export, message_count)
  - PAY_PER_REQUEST billing, TTL, encryption, point-in-time recovery
- **Terraform Infrastructure**
  - Lambda function, IAM role/policies, CloudWatch log group
  - DynamoDB table with consistent tagging
  - Placeholder zip for initial `terraform apply`
  - Environment-prefixed resource naming (`{env}-{name}`)
- **Python CLI Client**
  - Interactive console with send, reset, info, exit commands
  - boto3 Lambda invocation with error handling
  - Token usage display per message
- **Makefile Automation**
  - `setup`, `build`, `deploy-infra`, `deploy-lambda`, `test`
  - `logs`, `logs-recent`, `logs-errors` for CloudWatch
  - `clean`, `destroy`, `validate`, `format`, `outputs`
- **Configuration**
  - `.mise.toml` with Node.js 20, Python 3.12, Terraform 1.7, uv
  - `.env.example` with all required variables
  - `terraform.tfvars.example` with Terraform variable template
  - `deploy.sh` for Lambda code deployment
  - `terraform/load-env.sh` for environment loading

---

## Links

- [Braintrust Dashboard](https://www.braintrust.dev/app)
- [Braintrust Documentation](https://www.braintrust.dev/docs)

---

**Last Updated**: 2026-03-10

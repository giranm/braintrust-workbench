# Implementation Notes - Lambda Multi-Turn Conversation

## Overview

This document tracks implementation decisions, technical notes, and architecture for the multi-turn Lambda tracing project.

**Last Updated**: 2026-03-10

## Implementation Log

### 2026-03-10 - Initial Implementation

Full implementation of all 5 phases from PLAN.md:

1. **Project Setup**: `.mise.toml`, `.env.example`, README
2. **Terraform Infrastructure**: Lambda, DynamoDB, IAM, CloudWatch with consistent tagging
3. **Lambda Function**: TypeScript handler with multi-turn tracing via `traced()` + `span.export()`
4. **Python CLI Client**: Interactive console with conversation management
5. **Automation**: Makefile with setup/build/deploy/test/clean/destroy targets

**Key Design Decision**: Root "conversation" span created on first message, all subsequent turns link back to it via `parent: state.root_span_export`. This creates a flat hierarchy under one root rather than a chain.

---

### 2026-03-10 - OpenAI Integration

Replaced mock LLM calls with real OpenAI API integration:

- Added `openai` dependency to `lambda/package.json`
- Used `wrapOpenAI()` from Braintrust for automatic LLM call tracing
- Model: `gpt-4o-mini` (fast, cheap: $0.15/$0.60 per 1M tokens)
- Temperature: 0.7
- Added `OPENAI_API_KEY` to Lambda environment variables via Terraform
- Token counts now reflect real OpenAI usage

**Key Benefit**: `wrapOpenAI()` automatically creates child spans for every OpenAI API call, showing full request/response details and token metrics in Braintrust.

---

### 2026-03-10 - Migration to braintrust-workbench

Migrated from `sandbox` to `braintrust-workbench/projects/lambda-multi-turn-conversation/`:

- Copied all functional code (21 files) as-is
- Consolidated 5 source markdown files into workbench `docs/` structure
- Created project-level `.gitignore` for terraform state and deploy artifacts
- Rewrote `CLAUDE.md` and `README.md` for workbench conventions

---

## Architecture Decisions

### Runtime: Node.js 20

**Status**: Decided

**Rationale**: Faster cold starts than Python, more async-native, smaller package sizes. The Braintrust TypeScript SDK has full support for `initLogger`, `traced`, and `wrapOpenAI`.

### State Storage: DynamoDB

**Status**: Decided

**Rationale**: Fast lookups by `conversation_id`, automatic scaling with PAY_PER_REQUEST, TTL for automatic cleanup, server-side encryption. Item size limit (400KB) is sufficient for storing exported span strings.

### Infrastructure as Code: Terraform

**Status**: Decided

**Rationale**: Declarative, consistent tagging across all resources. Uses **local state** for demonstration simplicity - production deployments should use a remote backend (e.g., S3). All resources use `{environment}-{name}` prefix pattern. See the S3 backend comment in `terraform/main.tf` for a starting point.

### LLM: OpenAI gpt-4o-mini via wrapOpenAI()

**Status**: Decided

**Rationale**: Cheap for testing ($0.15/$0.60 per 1M tokens), `wrapOpenAI()` provides automatic tracing without manual span creation for LLM calls.

---

## Environment Setup

There are 4 options for loading environment variables for Terraform:

### Option 1: Use Makefile (Recommended)

The Makefile automatically loads `.env` before running Terraform commands:
```bash
cp .env.example .env
# Edit .env with your values
make deploy-infra
```

### Option 2: Create terraform.tfvars

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform.tfvars with your values
cd terraform && terraform plan
```

### Option 3: Use Helper Script

```bash
cd terraform
./load-env.sh plan
./load-env.sh apply
```

### Option 4: Source .env Manually

```bash
set -a && source .env && set +a
cd terraform && terraform plan
```

**Note**: When using the Makefile (Option 1), `TF_VAR_` exports are derived automatically from plain `.env` variables via the `LOAD_ENV` macro. You never need to set `TF_VAR_` prefixes manually. Options 2-4 are available for running Terraform directly outside the Makefile.

---

## Naming Convention

### Pattern

All AWS resources use the format: `{environment}-{base_name}`

### Examples (environment = "dev")

| Resource | Name |
|----------|------|
| Lambda Function | `dev-braintrust-multi-turn-conversation-lambda` |
| DynamoDB Table | `dev-braintrust-multi-turn-conversation-conversations` |
| IAM Role | `dev-braintrust-multi-turn-conversation-lambda-role` |
| IAM Policy | `dev-braintrust-multi-turn-conversation-dynamodb-policy` |
| CloudWatch Logs | `/aws/lambda/dev-braintrust-multi-turn-conversation-lambda` |

### Configuration Variables

| .env Variable | Terraform Variable (auto-exported) | Example |
|---------------|-------------------------------------|---------|
| `ENVIRONMENT` | `TF_VAR_ENVIRONMENT` | `dev` |
| `PROJECT_NAME` | `TF_VAR_PROJECT_NAME` | `braintrust-multi-turn-conversation` |
| `FUNCTION_NAME` | `TF_VAR_FUNCTION_NAME` | `braintrust-multi-turn-conversation-lambda` |

Multiple environments (dev, staging, prod) can coexist in the same AWS account without naming conflicts.

---

## Braintrust Integration Notes

### Logger Configuration

```typescript
const logger = initLogger({
  projectId: process.env.BRAINTRUST_PROJECT_ID!,
  apiKey: process.env.BRAINTRUST_API_KEY!,
  asyncFlush: false,  // CRITICAL: ensures flush before Lambda terminates
});
```

### Span Hierarchy

- **First message**: Creates root `conversation` span (type: task), nests `turn-1` inside
- **Subsequent messages**: Creates `turn-N` span with `parent: state.root_span_export`
- **OpenAI calls**: Auto-traced by `wrapOpenAI()` as child spans of each turn

### Explicit Flush

`await logger.flush()` is called after every span operation to ensure data reaches Braintrust before Lambda terminates. This prevents the "1 message delay" issue.

---

**Maintained By**: Claude Code
**Last Updated**: 2026-03-10

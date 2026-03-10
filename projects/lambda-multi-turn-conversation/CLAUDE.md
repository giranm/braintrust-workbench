# Lambda Multi-Turn Conversation - Claude Code Guide

## Project Overview

This project demonstrates multi-turn conversation tracing for AWS Lambda using Braintrust. A Node.js Lambda handles conversation messages, creates hierarchical traces via `span.export()` + `parent`, stores state in DynamoDB, and uses OpenAI gpt-4o-mini for real LLM responses. A Python CLI client drives testing.

**Status**: Implemented
**Focus**: Observability - Multi-turn tracing across stateless Lambda invocations

## Technology Stack

- **Lambda Runtime**: Node.js 20 / TypeScript
- **LLM**: OpenAI gpt-4o-mini via `wrapOpenAI()` (auto-traced)
- **Braintrust SDK**: v3.3.0 (`initLogger`, `traced`, `wrapOpenAI`)
- **State Storage**: DynamoDB (conversation state with span exports)
- **IaC**: Terraform 1.7 (Lambda, DynamoDB, IAM, CloudWatch)
- **CLI Client**: Python 3.12 with boto3
- **Package Management**: npm (Lambda), uv (Python client)
- **Version Management**: mise (node 20, python 3.12, terraform 1.7)

## Project Structure

```
lambda-multi-turn-conversation/
├── .gitignore               # Terraform state, deploy artifacts
├── .mise.toml               # Runtime versions
├── .env.example             # Environment variables template
├── CLAUDE.md                # This file
├── README.md                # Project documentation
├── Makefile                 # Build/deploy/test automation
├── deploy.sh                # Lambda deployment script
├── client.py                # Python CLI test client
├── pyproject.toml           # Python config (boto3)
├── uv.lock                  # Python lockfile
│
├── lambda/                  # Lambda function
│   ├── src/
│   │   ├── index.ts         # Main handler with multi-turn tracing
│   │   ├── conversation.ts  # DynamoDB state management
│   │   └── types.ts         # TypeScript interfaces
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   └── .nvmrc
│
├── terraform/               # Infrastructure as Code
│   ├── main.tf              # Provider configuration
│   ├── variables.tf         # Input variables & tags
│   ├── outputs.tf           # Output values
│   ├── dynamodb.tf          # DynamoDB table
│   ├── lambda.tf            # Lambda, IAM, CloudWatch
│   ├── load-env.sh          # Helper for env loading
│   └── terraform.tfvars.example
│
└── docs/                    # Development documentation
    ├── planning.md          # Goals and implementation strategy
    ├── implementation.md    # Technical decisions and architecture
    ├── issues.md            # Known issues and troubleshooting
    └── changelog.md         # Version history
```

## Braintrust Integration Patterns

### Key SDK Patterns Used

1. **`initLogger({ asyncFlush: false })`** - Critical for Lambda: ensures logs flush before termination
2. **`traced(fn, { name, type, parent })`** - Creates spans; `parent` links to exported root span for multi-turn
3. **`wrapOpenAI(new OpenAI(...))`** - Auto-traces all OpenAI API calls as nested spans
4. **`span.export()`** - Serializes span for cross-invocation persistence via DynamoDB

### Trace Hierarchy

```
conversation (type: task)          ← Root span, created on first message
├── turn-1 (type: llm)            ← Nested inside root span
│   └── OpenAI chat.completions   ← Auto-traced by wrapOpenAI
├── turn-2 (type: llm)            ← parent: root_span_export
│   └── OpenAI chat.completions
└── turn-3 (type: llm)            ← parent: root_span_export
    └── OpenAI chat.completions
```

### References
- **Braintrust Docs**: https://www.braintrust.dev/docs
- **Braintrust Cookbook**: https://github.com/braintrustdata/braintrust-cookbook

## Setup and Running

### Prerequisites

```bash
cd projects/lambda-multi-turn-conversation
mise install && mise trust
```

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# AWS
AWS_PROFILE=sandbox
AWS_REGION=us-east-1

# API Keys (REQUIRED)
BRAINTRUST_API_KEY=your_api_key_here
BRAINTRUST_PROJECT_ID=your_project_id_here
OPENAI_API_KEY=your_openai_api_key_here

# Terraform config
ENVIRONMENT=dev
PROJECT_NAME=braintrust-multi-turn-conversation
FUNCTION_NAME=braintrust-multi-turn-conversation-lambda
OWNER=admin@example.com
```

No `TF_VAR_` prefixes needed - the Makefile's `LOAD_ENV` macro auto-exports them.

### Common Commands

```bash
make setup          # Install all dependencies
make deploy-infra   # Deploy AWS infrastructure (Terraform)
make deploy-lambda  # Build and deploy Lambda code
make start-client   # Run interactive CLI client
make logs           # Tail CloudWatch logs
make clean          # Remove build artifacts
make destroy        # Tear down all AWS resources
```

## Development Workflow

1. **Before coding**: Read `docs/planning.md` and `docs/issues.md`
2. **During development**: Update `docs/implementation.md` with decisions
3. **After changes**: Update `docs/changelog.md` and resolve issues in `docs/issues.md`

### Key Files to Modify

| Change | File(s) |
|--------|---------|
| Lambda handler logic | `lambda/src/index.ts` |
| DynamoDB operations | `lambda/src/conversation.ts` |
| Type definitions | `lambda/src/types.ts` |
| Lambda dependencies | `lambda/package.json` |
| Infrastructure | `terraform/*.tf` |
| Test client | `client.py` |
| Python dependencies | `pyproject.toml` |

### Build/Deploy Cycle

```bash
# After modifying Lambda code:
make build          # Compile TypeScript
make deploy-lambda  # Deploy to AWS
make start-client   # Test interactively

# After modifying Terraform:
make validate       # Check configuration
make deploy-infra   # Apply changes
```

## Notes for Claude Code

- This project is **fully implemented** - all components are working
- Lambda code is in TypeScript, client is in Python
- The Makefile auto-exports `TF_VAR_` aliases from plain `.env` variables (via `LOAD_ENV` macro) - users never set `TF_VAR_` prefixes manually
- `asyncFlush: false` on the Braintrust logger is critical - do not change
- `wrapOpenAI()` provides automatic LLM tracing - OpenAI calls show as child spans
- All turn spans (except turn-1) use `parent: state.root_span_export` to link to root
- The `docs/` folder contains detailed context - read before making changes

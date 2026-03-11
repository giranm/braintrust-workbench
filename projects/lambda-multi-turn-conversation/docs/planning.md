# Planning - Lambda Multi-Turn Conversation

## Overview

**Project**: Lambda Multi-Turn Conversation
**Status**: Implemented
**Focus**: Multi-turn conversation tracing across stateless Lambda invocations using Braintrust

## Context

This project validates the multi-turn conversation tracing approach for AWS Lambda architectures using Braintrust. It demonstrates how to create a single hierarchical trace across multiple stateless Lambda invocations, where each user message in a conversation becomes a child span under a shared root trace.

**Problem Solved:**
- Each Lambda invocation is stateless and would normally create independent traces
- This solution creates a single trace with all conversation messages as nested child spans
- Uses `span.export()` and the `parent` parameter to link spans across Lambda invocations

**Key Technical Challenge:**
Lambda functions are stateless, so conversation state (exported span strings) must be persisted between invocations using DynamoDB.

## Architecture

```
User → Python CLI Client → Lambda Function (Node.js) → DynamoDB (State) → Braintrust
                                 ↓
                         OpenAI gpt-4o-mini (via wrapOpenAI)
```

**Components:**
1. **Lambda Function (Node.js/TypeScript)**: Handles conversation messages, creates traced spans, manages parent/child relationships
2. **DynamoDB Table**: Stores conversation state (root_span_export, last_span_export)
3. **Python CLI Client**: Interactive console for testing conversations
4. **Terraform**: Provisions all AWS resources with consistent tagging
5. **Mise**: Manages runtime versions (Node.js 20, Python 3.12, Terraform 1.7)

## Implementation Plan

### Phase 1: Project Setup & Configuration - [x] Complete

- [x] Create `.mise.toml` with Node.js 20, Python 3.12, Terraform 1.7
- [x] Create `.env.example` with AWS, Braintrust, OpenAI variables
- [x] Create `README.md` with setup and usage instructions

### Phase 2: Terraform Infrastructure - [x] Complete

- [x] `terraform/main.tf` - Provider and backend configuration
- [x] `terraform/variables.tf` - Input variables with defaults, tag configuration
- [x] `terraform/outputs.tf` - Export Lambda ARN, table name, deployment summary
- [x] `terraform/dynamodb.tf` - Conversation state table (PAY_PER_REQUEST, TTL, encryption)
- [x] `terraform/lambda.tf` - Lambda function, IAM role, CloudWatch logs, placeholder zip

### Phase 3: Lambda Function Implementation - [x] Complete

- [x] `lambda/src/index.ts` - Main handler with multi-turn tracing logic
- [x] `lambda/src/conversation.ts` - DynamoDB state management (get/save)
- [x] `lambda/src/types.ts` - TypeScript interfaces
- [x] `lambda/package.json` - Dependencies (braintrust, aws-sdk, openai)
- [x] `lambda/tsconfig.json` - TypeScript configuration
- [x] `deploy.sh` - Lambda deployment script

### Phase 4: Python CLI Client - [x] Complete

- [x] `client.py` - Interactive console with conversation management
- [x] `pyproject.toml` - Python dependencies (boto3)
- [x] Commands: send message, reset, info, exit

### Phase 5: Supporting Files & Automation - [x] Complete

- [x] `Makefile` - setup, build, deploy-infra, deploy-lambda, test, logs, clean, destroy
- [x] `.gitignore` - Terraform state, build artifacts
- [x] `terraform/load-env.sh` - Helper for loading .env into terraform
- [x] `terraform/terraform.tfvars.example` - Variable template

## Verification

### Infrastructure
```bash
make outputs
# lambda_function_name = "dev-braintrust-multi-turn-conversation-lambda"
# dynamodb_table_name = "dev-braintrust-multi-turn-conversation-conversations"
```

### Conversation Test
```bash
make start-client
# Have a 3+ message conversation
# Verify each turn shows token counts
```

### Braintrust UI
1. Open dashboard → project → Logs
2. Find conversation trace
3. Verify: single root trace with turn-1, turn-2, turn-3 as children
4. Verify: OpenAI API calls auto-traced as nested spans

## Cost Estimation

**Expected Costs (per month for light testing):**
- Lambda: $0.00 (free tier: 1M requests, 400K GB-seconds)
- DynamoDB: $0.00 (free tier: 25 GB storage, 25 RCU/WCU)
- CloudWatch Logs: $0.00 (free tier: 5 GB ingestion)
- OpenAI API: ~$0.005 per 100 messages (gpt-4o-mini)

**Total estimated cost: ~$0.00** (within AWS free tier)

## Rollback Plan

```bash
# Destroy infrastructure
make destroy

# Clean up local artifacts
make clean
```

## References

**Key Braintrust SDK Features:**
- `span.export()`: Serialize span for cross-invocation passing
- `parent` parameter: Link child spans to parent trace
- `asyncFlush: false`: Critical for Lambda to ensure logs flush before termination
- `wrapOpenAI()`: Auto-trace OpenAI API calls

**Documentation:**
- Braintrust Docs: https://www.braintrust.dev/docs
- Braintrust Cookbook: https://github.com/braintrustdata/braintrust-cookbook
- AWS Lambda Best Practices: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html

---

**Last Updated**: 2026-03-10
**Status**: Implemented

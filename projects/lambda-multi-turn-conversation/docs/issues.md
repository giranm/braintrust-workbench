# Issues & Troubleshooting - Lambda Multi-Turn Conversation

## Overview

This document tracks known issues, resolved problems, and troubleshooting guidance.

**Last Updated**: 2026-03-10

---

## Open Issues

_No open issues._

---

## Resolved Issues

### Lambda Deployment Fails - "Function not found"

**Error**: `ResourceNotFoundException: Function not found`
**Cause**: Trying to deploy Lambda code before infrastructure exists
**Resolution**: Run `make deploy-infra` first, then `make deploy-lambda`

### Terraform Apply Fails - "ResourceInUseException"

**Error**: `Error creating DynamoDB Table: ResourceInUseException`
**Cause**: Table already exists from a previous deployment
**Resolution**: Either:
1. Import: `terraform import aws_dynamodb_table.conversations dev-braintrust-multi-turn-conversation-conversations`
2. Or destroy and recreate: `make destroy && make deploy-infra`

### Client Cannot Invoke Lambda - "AccessDeniedException"

**Error**: `AccessDeniedException` when running `make test`
**Cause**: AWS credentials missing or insufficient permissions
**Resolution**:
```bash
aws sts get-caller-identity --profile sandbox
# Verify lambda:InvokeFunction permission
```

### No Traces in Braintrust

**Symptoms**: Conversation works but no traces appear in Braintrust UI
**Possible Causes**:
1. Invalid `BRAINTRUST_API_KEY` - check `.env`
2. Wrong `BRAINTRUST_PROJECT_ID` - verify in Braintrust dashboard
3. Logs not flushed - check CloudWatch logs for flush errors
**Resolution**: Check Lambda CloudWatch logs with `make logs`

### Traces Not Linked (Separate Instead of Nested)

**Symptoms**: Each message shows as an independent trace, not nested under root
**Cause**: `parent` parameter not being passed correctly, or DynamoDB state missing `root_span_export`
**Resolution**:
1. Check DynamoDB state has `root_span_export` field
2. Verify `parent: state.root_span_export` is passed to `traced()` in `index.ts`
3. Check Lambda logs for "hasRootParent: true"

### Terraform Variables Not Loading - "No value for required variable"

**Error**: `Error: No value for required variable` on `terraform plan`
**Cause**: `.env` not loaded, or running Terraform directly without `TF_VAR_` exports
**Resolution**:
- Use `make deploy-infra` (auto-loads `.env` and exports `TF_VAR_` aliases via `LOAD_ENV` macro)
- If running Terraform directly outside the Makefile, you must manually export `TF_VAR_` prefixed variables (see `docs/implementation.md` Options 2-4)

### OpenAI - "Incorrect API key provided"

**Cause**: `OPENAI_API_KEY` not set or incorrect in Lambda environment
**Resolution**:
1. Check `.env` has correct key
2. Ensure `OPENAI_API_KEY` is set in `.env`
3. Redeploy: `make deploy-infra` (updates Lambda env vars)

### OpenAI - "You exceeded your current quota"

**Cause**: No payment method or insufficient credits on OpenAI account
**Resolution**:
1. Add payment method: https://platform.openai.com/account/billing
2. Check usage limits: https://platform.openai.com/account/limits
3. New accounts may need 24 hours after adding payment

### OpenAI - "Rate limit exceeded"

**Cause**: Too many requests in short time (5 RPM on free tier)
**Resolution**: Wait 60 seconds between test conversations, or upgrade to paid tier

---

## Known Limitations

### Cold Start Latency

**Description**: First Lambda invocation after a period of inactivity includes cold start time (SDK initialization, DynamoDB client creation).
**Impact**: First request may take 3-5 seconds vs <1 second for warm invocations.
**Workaround**: Use provisioned concurrency for production use cases.

### DynamoDB Item Size Limit

**Description**: DynamoDB items are limited to 400KB. Exported span strings are typically small, but very long conversations could approach this.
**Impact**: Extremely long conversations might fail to save state.
**Workaround**: Implement conversation length limits or state pruning for production.

### Concurrent Modification Risk

**Description**: Two Lambda invocations for the same conversation ID running simultaneously could create race conditions on DynamoDB state.
**Impact**: State corruption, lost span exports.
**Workaround**: The CLI client sends messages sequentially. For production, implement DynamoDB conditional writes or optimistic locking.

---

## Technical Debt

- [ ] **Retry logic**: Add exponential backoff for DynamoDB and OpenAI transient failures
- [ ] **Input validation**: Validate request body schema before processing
- [ ] **Circuit breaker**: Add circuit breaker for OpenAI API calls
- [ ] **Monitoring**: Set up CloudWatch alarms for errors and latency
- [ ] **Conversation TTL**: Add TTL attribute to DynamoDB items for automatic cleanup

---

**Maintained By**: Claude Code
**Last Updated**: 2026-03-10

# Implementation Notes - Support Desk Investigator

**Last Updated**: 2026-02-17

This doc captures technical decisions and a checklist for implementation.

---

## Current State
The repo currently contains:
- `src/main.py` — simple single-process demo runner
- `src/eval.py` — simple evaluation example

Target state is a multi-service Docker Compose deployment with:
- Frappe Helpdesk
- Qdrant
- backend service
- ADK agent service
- OpenTelemetry tracing exported to Braintrust

---

## Intended Architecture

### Backend service
Responsibilities:
- receive Frappe webhooks (`POST /webhooks/frappe`)
- normalize into a “case file” JSON
- trigger an investigation run (sync or async)
- expose tool endpoints for the agent:
  - `GET /tools/ticket/{id}`
  - `POST /tools/logs/query`
  - `POST /tools/incidents/search`
  - `GET /tools/deploys/recent`
  - `GET /tools/customer/{id}`
- post results back to Frappe ticket:
  - internal note
  - customer reply draft
  - tags/status updates

### Agent service (ADK)
Responsibilities:
- define the investigation workflow
- call backend tool endpoints
- call LLM provider (OpenAI/Anthropic)
- emit OTel spans per step and tool call

---

## OpenTelemetry → Braintrust
- instrument backend and agent
- propagate trace context between services
- export spans to Braintrust via Braintrust OTel SDK integration

Reference:
https://www.braintrust.dev/docs/integrations/sdk-integrations/opentelemetry

---

## Variants (Bad vs Good)

### Baseline (`VARIANT=baseline`)
- minimal schema
- shallow retrieval
- no tool requirements
- no confidence gate

### Improved (`VARIANT=improved`)
- strict JSON schema output:
  - `customer_reply`
  - `internal_notes`
  - `evidence[]`
  - `actions[]`
  - `confidence`
- tool-call requirements:
  - if error signature present → must query logs
- better retrieval:
  - query rewriting + higher top-k
- confidence gating:
  - low confidence → request info or escalate

---

## Evaluation Plan
Start with deterministic scorers:
- schema validity
- evidence presence
- tool usage correctness

Then add LLM-as-judge scorers:
- helpfulness
- tone/empathy
- internal notes clarity

---

## Docker Compose Notes
Minimum services:
- Frappe Helpdesk (+ its dependencies)
- Qdrant
- backend
- agent

Optional:
- redis + worker
- demo-logs service

---

## Implementation Checklist
- [ ] Add docker-compose.yml
- [ ] Backend skeleton + webhook route
- [ ] Frappe API client helper
- [ ] Tool API routes (ticket/logs/incidents/deploys/customer)
- [ ] Qdrant collection + ingestion script
- [ ] ADK agent workflow + tool bindings
- [ ] OTel instrumentation + Braintrust exporter
- [ ] Variants (baseline vs improved)
- [ ] Offline regression runner + scorers
- [ ] Demo tickets + record/replay fixtures
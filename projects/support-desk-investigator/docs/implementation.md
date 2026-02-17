# Implementation Notes - Support Desk Investigator

**Last Updated**: 2026-02-17

This doc captures technical decisions and a checklist for implementation.

---

## Implementation Progress

### ✅ Day 1: Frappe Infrastructure Setup (COMPLETED)

**Date**: 2026-02-17

**What was implemented**:
- Simplified Frappe Docker setup based on official Helpdesk Docker repo
- Frappe Bench v16 with development setup
- MariaDB 11.8 with persistent database storage
- Redis 6.2 for caching
- Qdrant v1.7.4 vector database (profile: tools, ready for Day 4)
- Automated initialization script for first-run setup
- Frappe site created: support-desk.localhost
- Admin access configured (Administrator / admin123)

**Files created**:
- `docker-compose.yml` - Simplified 3-service architecture (mariadb, redis, frappe)
- `scripts/init.sh` - Automated initialization script
- `.env.example` - Configuration with DB password and port settings
- `scripts/start.sh` - Service startup helper
- `scripts/stop.sh` - Clean shutdown helper
- `scripts/logs.sh` - Log viewer helper
- `QUICKSTART.md` - Getting started guide

**Technical decisions**:
- Used frappe/bench:latest (official development image)
- Platform: linux/amd64 for ARM64 Mac compatibility
- Simplified architecture: mariadb + redis + frappe (development mode)
- Database persistence only (bench is ephemeral, reinitializes on container restart)
- Init script handles: bench creation, app installation, site setup
- Network isolation via support-desk-net bridge
- Qdrant ready but behind `--profile tools` until needed

**Service Architecture**:
```
frappe (bench) → web server (port 8000) + socketio (port 9000)
                 ↓
         db (MariaDB) + redis (cache/queue)
```

**Service endpoints**:
- Frappe UI: http://localhost:8080
- Frappe Socketio: ws://localhost:9000
- Qdrant API: http://localhost:6333 (when --profile tools enabled)

**Testing**:
- ✅ All 3 services start successfully
- ✅ Automated initialization completes (~5-10 minutes first run)
- ✅ Site created: support-desk.localhost
- ✅ Frappe UI accessible at http://localhost:8080
- ✅ Login working: Administrator / admin123
- ✅ Helpdesk module installed and accessible
- ✅ Apps installed: Frappe v16, Telephony, Helpdesk

**Implementation approach**:
- Based on official Frappe Helpdesk Docker setup: https://github.com/frappe/helpdesk/blob/develop/docker
- Init script checks if bench exists, runs full initialization if not
- First startup: ~5-10 minutes (clones repos, installs apps, creates site)
- Subsequent startups: ~30 seconds (bench already exists in container)
- Database persists across restarts (MariaDB volume)

**Known characteristics**:
- Bench is ephemeral (recreated on container restart, but fast after first init)
- Database persists (ticket data, users, settings remain)
- Development mode enabled for easy debugging
- No Host header required (works directly at localhost:8080)

**Next steps (Day 2)**:
- Create backend service (FastAPI) with webhook receiver
- Configure Frappe webhooks for ticket events
- Implement CaseFile schema and storage
- Build tool API routes (ticket/logs/incidents/deploys/customer)

---

## Current State
The repo currently contains:
- ✅ **Docker Compose stack** with Frappe Helpdesk running
- ✅ **Persistent storage** for Frappe data
- ✅ **Helper scripts** for local development
- `src/main.py` — simple single-process demo runner (to be replaced)
- `src/eval.py` — simple evaluation example (to be evolved)

Target state is a multi-service Docker Compose deployment with:
- ✅ Frappe Helpdesk (DONE)
- ✅ Qdrant (READY, not yet used)
- ⏳ Backend service (Day 2)
- ⏳ ADK agent service (Day 3)
- ⏳ OpenTelemetry tracing exported to Braintrust (Day 5)

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

### Infrastructure (Day 1)
- [x] Add docker-compose.yml
- [x] Frappe Helpdesk service with auto-init
- [x] MariaDB + Redis dependencies
- [x] Qdrant service (profile: tools)
- [x] Persistent volumes for all data
- [x] Helper scripts (start/stop/logs)
- [x] Quick start documentation

### Backend Service (Day 2)
- [ ] Backend skeleton (FastAPI)
- [ ] Webhook endpoint: `POST /webhooks/frappe`
- [ ] CaseFile schema and storage
- [ ] Frappe API client helper
- [ ] Add backend to docker-compose
- [ ] Configure Frappe webhook in UI

### Tool System (Day 2-4)
- [ ] Tool API routes (ticket/logs/incidents/deploys/customer)
- [ ] Qdrant collection + ingestion script
- [ ] Mock logs/deploys/customer data
- [ ] Tool endpoint testing

### Agent Service (Day 3)
- [ ] ADK agent skeleton
- [ ] Investigation workflow (triage/gather/verify/finalize)
- [ ] Tool bindings (HTTP clients)
- [ ] LLM provider integration (OpenAI/Anthropic)
- [ ] Add agent to docker-compose
- [ ] Backend → Agent invocation

### Observability (Day 5)
- [ ] OTel instrumentation (backend)
- [ ] OTel instrumentation (agent)
- [ ] Braintrust exporter configuration
- [ ] Trace context propagation
- [ ] Span attributes for debugging

### Evaluation (Day 6)
- [ ] Variants (baseline vs improved)
- [ ] Test dataset creation
- [ ] Deterministic scorers (schema/evidence/tools)
- [ ] LLM-as-judge scorers (tone/helpfulness)
- [ ] Offline regression runner
- [ ] Demo tickets + record/replay fixtures
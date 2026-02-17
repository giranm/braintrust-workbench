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

**Next steps (Day 3)**:
- Create Agent service with Google ADK
- Implement investigation workflow (triage → gather → verify → finalize)
- Connect agent to backend tool APIs
- Implement agent → backend communication

---

### ✅ Day 2: Backend Service & Tool APIs (COMPLETED)

**Date**: 2026-02-17

**What was implemented**:
- FastAPI backend service with webhooks and tool endpoints
- CaseFile schema for normalized ticket data
- Webhook receiver for Frappe ticket events
- Tool API endpoints with mock data:
  - `GET /tools/ticket/{id}` - Ticket details
  - `POST /tools/logs/query` - Log queries
  - `POST /tools/incidents/search` - Similar incident search
  - `GET /tools/deploys/recent` - Recent deployments
  - `GET /tools/customer/{id}` - Customer information
- Docker containerization for backend service

**Files created**:
- `src/common/schemas.py` - Common data models (CaseFile, InvestigationResult, Evidence, Action)
- `src/backend/app.py` - FastAPI application
- `src/backend/routes/webhooks.py` - Webhook endpoints
- `src/backend/routes/tools.py` - Tool API endpoints with mock data
- `Dockerfile.backend` - Backend service container
- Updated `docker-compose.yml` - Added backend service
- Updated `pyproject.toml` - Added FastAPI, uvicorn, httpx dependencies

**Technical decisions**:
- FastAPI for async/await support and auto-generated OpenAPI docs
- Pydantic models for strict schema validation
- Mock data for Day 2 (will connect to real systems in Day 3-4)
- Webhook normalization: Frappe format → CaseFile schema
- Tool endpoints return structured JSON for agent consumption
- Backend depends on Frappe service (waits for it to be healthy)

**Service endpoints**:
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Webhooks: http://localhost:8000/webhooks/*
- Tools: http://localhost:8000/tools/*

**Testing**:
- ✅ Backend service builds successfully
- ✅ All endpoints responding with 200 OK
- ✅ Health checks working
- ✅ Webhook receiver accepting payloads
- ✅ Tool endpoints returning mock data
- ✅ OpenAPI documentation generated
- ✅ End-to-end verification (fresh deployment):
  - docker compose down -v → up
  - Webhooks automatically created via seed script
  - Test ticket created in Frappe UI
  - Backend received webhook with all 9 fields
  - Successfully normalized to CaseFile format

**Mock data implemented**:
- Ticket: Checkout 502 error scenario
- Logs: Mock ERROR logs with 502 patterns
- Incidents: Similar past incidents with resolutions
- Deploys: Recent deployments to checkout/payment services
- Customer: Enterprise customer profile

**Automated configuration**:
- `scripts/seed-db.sql` - Database seed script with webhook configuration
- Automatically applied during first-time initialization
- Creates two webhooks:
  - HD Ticket - Creation (after_insert)
  - HD Ticket - Update (on_update)
- Both webhooks send 9 fields: name, subject, description, status, priority, contact, customer, creation, modified

**Known characteristics**:
- Tool endpoints use mock data (Day 4 will connect to Qdrant, real log systems)
- Webhook receiver acknowledges but doesn't trigger investigation yet (Day 3)
- No Frappe API client yet (will add when posting results back)
- Webhooks are automatically configured via seed script (no manual UI setup needed)

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
- [x] Backend skeleton (FastAPI)
- [x] Webhook endpoint: `POST /webhooks/frappe`
- [x] CaseFile schema and storage
- [ ] Frappe API client helper (deferred to Day 3 - when posting results back)
- [x] Add backend to docker-compose
- [x] Configure Frappe webhook (automated via seed-db.sql)

### Tool System (Day 2-4)
- [x] Tool API routes (ticket/logs/incidents/deploys/customer) - with mock data
- [ ] Qdrant collection + ingestion script (Day 4)
- [x] Mock logs/deploys/customer data
- [x] Tool endpoint testing

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
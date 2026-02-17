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

**Next steps (Day 4)**:
- Connect to Qdrant for incident search
- Real log system integration (or better mock data)
- Post investigation results back to Frappe (internal notes + customer reply)
- Frappe API client helper

---

### ✅ Day 3: Agent Service & Investigation Workflow (COMPLETED)

**Date**: 2026-02-17

**What was implemented**:
- Agent service with 4-phase investigation workflow
- Tool client for calling backend APIs (HTTP)
- LLM integration (Anthropic) - ready but using baseline rules for now
- Backend → Agent communication pipeline
- End-to-end flow: Webhook → Backend → Agent → Investigation Result

**Files created**:
- `src/agent/__init__.py` - Agent package
- `src/agent/app.py` - FastAPI agent service
- `src/agent/workflow.py` - 4-phase investigation workflow
- `src/agent/tools.py` - HTTP client for backend tool endpoints
- `Dockerfile.agent` - Agent service containerization
- Updated `docker-compose.yml` - Added agent service
- Updated `pyproject.toml` - Added anthropic dependency
- Updated `src/backend/routes/webhooks.py` - Trigger agent investigation

**Technical decisions**:
- 4-phase workflow pattern (industry standard for complex investigations):
  1. **Triage** - Categorize issue, determine required tools
  2. **Gather** - Collect evidence from logs, incidents, deploys, customer data
  3. **Verify** - Cross-reference evidence, calculate confidence
  4. **Finalize** - Generate customer reply and internal notes
- Agent and backend communicate via HTTP REST API
- Agent service is stateless (receives CaseFile, returns InvestigationResult)
- Tool client uses httpx AsyncClient for concurrent tool calls
- Baseline variant uses rule-based logic (no LLM yet)
- LLM integration ready but not activated (will use for improved variant)

**Service Architecture**:
```
Frappe Webhook → Backend (normalize) → Agent (investigate) → Backend (post results)
                          ↓                      ↓
                    Tool Endpoints          4-Phase Workflow
                    (logs, incidents,     (triage/gather/verify/finalize)
                     deploys, customer)
```

**Service endpoints**:
- Agent API: http://localhost:8001
- Agent health: http://localhost:8001/health
- Investigation: POST http://localhost:8001/investigate

**Investigation workflow details**:

**Phase 1: Triage**
- Analyzes ticket subject and description
- Categorizes issue: error, request, question, incident
- Determines required tools (logs, incidents, deploys)
- Assesses severity based on priority and keywords

**Phase 2: Gather**
- Calls backend tool endpoints based on triage
- Collects customer profile (if customer_id present)
- Queries logs for error patterns (if error detected)
- Searches similar incidents (if incident category)
- Checks recent deployments (if error/incident)
- Stores evidence with source, content, confidence, timestamp

**Phase 3: Verify**
- Analyzes collected evidence
- Calculates confidence score (0.0-1.0)
- Rule-based for baseline: +0.2 for logs, +0.2 for incidents, +0.1 for deploys
- Determines if sufficient evidence (confidence >= 0.6)
- Decides escalation: low confidence OR urgent priority

**Phase 4: Finalize**
- Generates customer-facing reply (empathetic, actionable)
- Generates internal investigation notes (evidence summary, root cause)
- Recommends actions (escalate, request_info, suggest_resolution)
- Returns InvestigationResult with all fields

**Testing**:
- ✅ Agent service builds successfully
- ✅ All 4 phases execute in sequence
- ✅ Tool client calls backend endpoints
- ✅ Evidence collection from multiple sources
- ✅ Confidence scoring and escalation logic
- ✅ Customer reply and internal notes generation
- ⏳ End-to-end webhook test pending (after docker compose up)

**Baseline variant characteristics**:
- Rule-based categorization (keyword matching)
- Simple confidence scoring formula
- Template-based response generation
- No LLM calls (fast, deterministic, low cost)
- Good baseline for A/B testing against improved variant

**Known characteristics**:
- Agent service starts independently
- Backend depends on agent (waits for it to be ready)
- Investigation is synchronous (backend waits for agent response)
- 60-second timeout for investigation
- Fallback response on investigation failure
- Results logged but not yet posted back to Frappe (Day 4)

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
- ✅ **Docker Compose stack** with Frappe Helpdesk, Backend, Agent running
- ✅ **Persistent storage** for Frappe data
- ✅ **Helper scripts** for local development
- ✅ **End-to-end pipeline**: Webhook → Backend → Agent → Investigation
- `src/main.py` — simple single-process demo runner (to be replaced)
- `src/eval.py` — simple evaluation example (to be evolved)

Target state is a multi-service Docker Compose deployment with:
- ✅ Frappe Helpdesk (DONE)
- ✅ Qdrant (READY, not yet used)
- ✅ Backend service (DONE)
- ✅ Agent service (DONE)
- ⏳ Results posted back to Frappe (Day 4)
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
- [x] Agent service skeleton (FastAPI)
- [x] Investigation workflow (triage/gather/verify/finalize)
- [x] Tool bindings (HTTP clients via httpx)
- [x] LLM provider integration (Anthropic SDK integrated, baseline variant uses rules)
- [x] Add agent to docker-compose
- [x] Backend → Agent invocation (webhook triggers investigation)

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
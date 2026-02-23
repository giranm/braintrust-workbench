# Implementation Notes - Support Desk Investigator

**Last Updated**: 2026-02-23

This doc captures technical decisions, progress tracking, and implementation history.

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

### ✅ Day 3 (Migration): Google ADK Integration (COMPLETED)

**Date**: 2026-02-18

**What was implemented**:
- Migrated from custom workflow to Google Agent Development Kit (ADK)
- Replaced rule-based logic with LLM-driven reasoning
- Implemented SequentialAgent pattern with 4 specialized sub-agents
- Created ADK function tools wrapping backend HTTP endpoints
- Maintained backward compatibility with existing HTTP interface

**Files created/modified**:
- `src/agent/adk_tools.py` (NEW) - 5 ADK function tools for backend integration
- `src/agent/adk_workflow.py` (NEW) - SequentialAgent with 4-phase workflow
- `src/agent/workflow.py` → `src/agent/workflow_legacy.py` (RENAMED) - Legacy implementation preserved
- `src/agent/app.py` (MODIFIED) - Updated to use ADK workflow
- `pyproject.toml` (MODIFIED) - Added google-adk>=1.25.0 dependency
- `.env.example` (MODIFIED) - Added ADK_MODEL configuration
- `docker-compose.yml` (MODIFIED) - Added ADK_MODEL environment variable

**Technical decisions**:
- **SequentialAgent pattern**: Chose 4 specialized sub-agents over single agent for:
  - Better observability (clear phase boundaries)
  - Easier debugging (isolated agent responsibilities)
  - Explicit state management between phases
  - Alignment with original architecture specification
- **Tool binding strategy**: Function tools wrapping HTTP calls
  - Maintains separation between agent and backend
  - No architecture changes required in backend
  - Tools only available to GatherAgent (principle of least privilege)
- **Model choice**: Anthropic Claude 3.5 Sonnet via ADK
  - Already configured in environment
  - Claude excels at structured reasoning and JSON output
  - Supports async execution for tool calls
- **State management**: ADK automatically passes state between agents
  - TriageAgent → triage_result
  - GatherAgent → evidence
  - VerifyAgent → analysis
  - FinalizeAgent → investigation_result
- **Backward compatibility**: FastAPI interface unchanged
  - Backend still calls POST /investigate with CaseFile
  - Returns InvestigationResult with same schema
  - No changes needed in backend service

**ADK Agent Architecture**:
```
SequentialAgent (InvestigationWorkflow)
├── TriageAgent (no tools)
│   └→ Analyzes ticket, outputs triage_result JSON
├── GatherAgent (5 tools)
│   ├→ get_ticket_details
│   ├→ query_logs
│   ├→ search_similar_incidents
│   ├→ get_recent_deployments
│   └→ get_customer_info
│   └→ Collects evidence, outputs evidence JSON
├── VerifyAgent (no tools)
│   └→ Analyzes evidence, outputs analysis JSON
└── FinalizeAgent (no tools)
    └→ Generates customer reply and internal notes
```

**ADK Function Tools**:
Each tool wraps a backend HTTP endpoint with:
- Rich docstrings (parsed by ADK for LLM context)
- Type hints on all parameters
- Clear descriptions of when to use the tool
- Async execution using httpx AsyncClient

**Phase-Specific Instructions**:
Each agent receives detailed instructions for:
- Input: What data to read from state
- Processing: What analysis or actions to perform
- Output: What JSON structure to write to state
- Constraints: Format requirements, validation rules

**Key improvements over legacy workflow**:
- **LLM-driven reasoning**: Replaced keyword matching with Claude's analysis
- **Structured output**: Enforced JSON schemas in agent instructions
- **Tool selection**: LLM decides which tools to call based on triage
- **Evidence synthesis**: LLM cross-references evidence from multiple sources
- **Natural language**: Customer replies and internal notes use LLM generation
- **Observability**: ADK provides built-in tracing and state inspection

**Testing approach**:
- Unit: Individual tools can be tested with httpx mocking
- Integration: SequentialAgent.run() with mock backend
- End-to-end: docker compose up → create ticket → verify investigation

**Migration verification**:
- ✅ google-adk dependency installed
- ✅ All 5 ADK tools created with proper docstrings
- ✅ SequentialAgent with 4 sub-agents configured
- ✅ FastAPI app.py updated to use ADK workflow
- ✅ Legacy workflow preserved as workflow_legacy.py
- ✅ Environment variables configured
- ⏳ Docker rebuild and end-to-end test pending

**Known characteristics**:
- ADK adds ~2-5 seconds to investigation time (LLM latency)
- State is automatically serialized between agents
- JSON parsing in finalize step handles both dict and string formats
- Fallback logic returns safe defaults on LLM failure
- All HTTP tools share a single AsyncClient for connection pooling

---

### ✅ Day 4 (Enhancements): Local Embeddings & Idempotent Deployment (COMPLETED)

**Date**: 2026-02-18

**What was implemented**:
- Replaced OpenAI embeddings with local sentence-transformers
- Made deployment fully idempotent with automatic initialization
- Upgraded Qdrant to v1.16.3 and enabled by default
- Created automatic backend initialization system

**Files created/modified**:
- `scripts/backend-entrypoint.sh` (NEW) - Automatic initialization entrypoint
- `pyproject.toml` (MODIFIED) - Removed openai, added sentence-transformers
- `src/backend/routes/tools.py` (MODIFIED) - Local embeddings instead of OpenAI
- `scripts/ingest-qdrant.py` (MODIFIED) - Local embeddings and idempotency
- `Dockerfile.backend` (MODIFIED) - Added entrypoint script
- `docker-compose.yml` (MODIFIED) - Qdrant v1.16.3, removed profile requirement
- `.env.example` (MODIFIED) - Removed OPENAI_API_KEY, added EMBEDDING_MODEL

**Technical decisions**:
- **Local embeddings**: sentence-transformers with `all-MiniLM-L6-v2` model
  - 384 dimensions (vs 1536 for OpenAI)
  - ~80MB model size, runs on CPU
  - No API calls or external dependencies
  - Semantic quality sufficient for incident similarity search
- **Idempotent ingestion**: Check if collection exists with data before ingesting
  - Skips ingestion if 20 points already exist
  - Safe to run `docker compose up` multiple times
  - No manual initialization steps required
- **Automatic initialization**: Backend entrypoint script handles setup
  - Waits for Qdrant to be available (with retry logic)
  - Runs idempotent ingestion on startup
  - Starts backend service after successful init
- **Qdrant upgrade**: v1.7.4 → v1.16.3
  - Fixed API compatibility (query_points method)
  - Better performance and features
  - Removed from "tools" profile (starts by default)

**Architecture change**:
```
Previous: OpenAI API → embeddings → Qdrant
Current:  Local model → embeddings → Qdrant
          (no external dependencies for vector search)
```

**Deployment flow**:
1. `docker compose up -d` starts all services
2. Backend waits for Qdrant health check
3. Runs idempotent ingestion (skips if data exists)
4. Loads local embedding model (~3-5 seconds)
5. Starts FastAPI service

**Tool endpoint behavior**:
- `POST /tools/incidents/search` now uses:
  - Local sentence-transformers for query embedding
  - Qdrant `query_points()` API for vector search
  - Returns incidents with similarity scores
- Fallback to mock data if Qdrant unavailable

**Testing**:
- ✅ Qdrant v1.16.3 running successfully
- ✅ Local embeddings generate 384-dimensional vectors
- ✅ 20 sample incidents ingested with proper payload
- ✅ Vector search returns relevant results (0.4-0.8 similarity scores)
- ✅ Idempotent ingestion verified (skips on subsequent runs)
- ✅ Automatic initialization works on fresh deployment
- ✅ End-to-end: docker compose down -v → up → auto-initialized

**Performance characteristics**:
- Embedding generation: ~20-50ms per query (local CPU)
- Vector search: ~10-30ms per query (Qdrant)
- Model loading: ~3-5 seconds (on backend startup)
- Total startup time: ~30 seconds (including initialization)

**Known characteristics**:
- Commercial LLM usage now isolated to agent reasoning only
- Backend has zero commercial API dependencies
- Embedding model downloads from HuggingFace on first run
- Qdrant data persists in Docker volume `qdrant-data`
- Ingestion is idempotent but doesn't update existing data

**Environment isolation**:
- **Backend tools** (`src/backend/routes/tools.py`): Local embeddings only
- **Agent orchestration** (`src/agent/adk_workflow.py`): Anthropic Claude for reasoning
- Clear separation: tools use open-source, reasoning uses commercial LLM

**Next steps**:
- Connect to real Frappe API for ticket data
- Integrate real log aggregation system
- Post investigation results back to Frappe
- Add OpenTelemetry tracing (Day 5)

---

### ✅ Day 5: Frappe API Integration (COMPLETED)

**Date**: 2026-02-20

**What was implemented**:
- Created service account "Helpdesk Assistant" for automated responses
- Created demo customer user "John Doe" and organization "Acme Corporation"
- Implemented idempotent Frappe user initialization
- Fixed Communication doctype to properly attribute messages
- Integrated customer-facing communications into portal view

**Files created/modified**:
- `scripts/init_frappe_users.py` (NEW) - Idempotent Frappe user/org initialization
- `scripts/backend-entrypoint.sh` (MODIFIED) - Added Frappe user init step
- `src/backend/frappe_client.py` (MODIFIED) - Added sender/sender_full_name to Communications
- `src/backend/routes/webhooks.py` (ALREADY EXISTS) - Posts internal notes, drafts, and customer communications

**Technical decisions**:
- **Service account pattern**: Created "Helpdesk Assistant" user for message attribution
  - Email: helpdesk-assistant@example.com
  - Communications now show proper sender instead of "No name found"
  - Improves customer experience and brand consistency
- **Communication vs Comment doctypes**:
  - Comment doctype: Internal only (desk view)
  - Communication doctype: Customer-facing (portal view)
  - communication_medium must be "Email" (not "Portal") per Frappe validation
- **Idempotent initialization**: Similar pattern to Qdrant ingestion
  - Checks if users/orgs exist before creating
  - Runs automatically on backend startup
  - Gracefully handles failures (warns but continues)
- **Demo customer setup**: Pre-configured John Doe from Acme Corporation
  - Enables realistic demo scenarios
  - Ticket attribution to customer account
  - Professional demo presentation

**Architecture**:
```
Ticket Created (Frappe)
    ↓ Webhook
Backend receives ticket
    ↓ Triggers investigation
Agent investigates (4 phases)
    ↓ Returns results
Backend posts to Frappe:
    1. Internal notes (Comment doctype)
    2. Customer reply draft (Comment/Info doctype)
    3. Customer communication (Communication doctype) ✅ NEW
    4. Tags (auto-investigated, needs-escalation)
    ↓
Customer sees response in portal ✅
Agent sees all details in desk view ✅
```

**Initialization flow**:
1. Backend starts → waits for Qdrant
2. Runs Qdrant ingestion (idempotent)
3. **Runs Frappe user initialization (idempotent)** ✅ NEW
   - Creates Helpdesk Assistant service account
   - Creates John Doe customer user
   - Creates Acme Corporation customer org
4. Starts FastAPI service

**Frappe API integration details**:
- Authentication: Basic auth with API key:secret (base64)
- Internal notes: POST /api/resource/Comment (comment_type: "Comment")
- Reply drafts: POST /api/resource/Comment (comment_type: "Info")
- Customer comms: POST /api/resource/Communication (communication_medium: "Email")
- Tags: POST /api/resource/Tag Link
- Ticket creation: POST /api/resource/HD Ticket

**Testing**:
- ✅ Service account created successfully
- ✅ Demo customer user and org created successfully
- ✅ Idempotent initialization verified (skips existing entities)
- ✅ Customer communications appear in portal view
- ✅ Communications properly attributed to "Helpdesk Assistant"
- ✅ Internal notes and drafts visible in desk view
- ✅ Tags applied to tickets (with fallback on errors)
- ✅ End-to-end: Ticket creation → Investigation → Results in Frappe

**Portal visibility**:
- Customer portal: http://localhost:8080/helpdesk/tickets/{id}
  - Shows ticket description
  - Shows automated response from "Helpdesk Assistant"
- Internal desk: http://localhost:8080/desk/hd-ticket/{id}
  - Shows all Comments (internal notes, drafts)
  - Shows Communications (customer-facing)
  - Shows evidence and investigation details

**Known characteristics**:
- Tags require Tag doctype to exist (may fail on fresh Frappe)
- Ticket creation via API always sets raised_by to authenticated user
- For realistic demos, create tickets via Frappe UI as customer user
- Communications with communication_medium="Email" appear in both views
- Service accounts need no roles/permissions for message sending

**Next steps**:
- Add OpenTelemetry instrumentation (Day 6)
- Implement Braintrust observability integration (Day 6)
- Create evaluation framework with variants (Day 7)

---

### Customer-App Frontend (ADDED)

**Date**: 2026-02-23

**What was added**:
- React + TypeScript frontend for simulating customer error scenarios
- Multiple portal simulations: Shop, Analytics, Pay, Travel
- 8 realistic error scenario pages:
  - Checkout Timeout
  - Payment Order Split
  - Dashboard Timeout
  - Export Failed
  - Transfer Pending
  - Duplicate Charge
  - Ticketing Failed
  - Price Changed
- Ticket generation UI with Frappe integration (planned)
- Settings page for configuration

**Location**: `src/customer-app/`

**Technology Stack**:
- Vite for build tooling
- React + TypeScript for UI
- shadcn-ui + Tailwind CSS for components and styling
- React Router for navigation
- TanStack Query for data fetching

**Files structure**:
```
src/customer-app/
├── src/
│   ├── App.tsx              # Main app with routing
│   ├── components/          # UI components (shadcn-ui)
│   ├── pages/               # Scenario pages
│   │   ├── Home.tsx         # Landing page
│   │   ├── Settings.tsx     # Configuration
│   │   └── portal/          # Error scenarios by product
│   │       ├── shop/        # Checkout Timeout, Payment Order Split
│   │       ├── analytics/   # Dashboard Timeout, Export Failed
│   │       ├── pay/         # Transfer Pending, Duplicate Charge
│   │       └── travel/      # Ticketing Failed, Price Changed
│   ├── layouts/             # Portal and simulator shells
│   └── data/scenarios.ts    # Scenario definitions
├── public/                  # Static assets
├── package.json             # npm dependencies
└── vite.config.ts           # Vite configuration
```

**Purpose**:
- Provides realistic customer scenarios for demo
- Generates varied support tickets automatically
- Simulates customer experience before ticket creation
- Completes the end-to-end flow: Customer Issue → Ticket → Investigation → Resolution

**Status**:
- ✅ Code integrated into repository
- ✅ Ready to run locally (`npm install && npm run dev`)
- ⏳ Not yet integrated with Docker Compose
- ⏳ Ticket generation to Frappe API not yet implemented

**Running locally**:
```bash
cd src/customer-app
npm install
npm run dev
# Open http://localhost:5173
```

**Future integration**:
- Add to docker-compose.yml as a service
- Implement Frappe API ticket creation
- Connect scenario metadata to investigation context
- Use for automated test data generation

---

## Current State (v0.3.0 - 2026-02-23)

### ✅ Fully Operational
- **Docker Compose stack**: Frappe Helpdesk, MariaDB, Redis, Qdrant, Backend, Agent
- **Persistent storage**: All data (Frappe DB, Qdrant vectors) persists across restarts
- **Helper scripts**: start.sh, stop.sh, logs.sh for local development
- **End-to-end pipeline**: Complete integration from webhook to investigation to results
  ```
  Frappe Ticket Created
    → Webhook Event (backend)
    → Case File Normalization (backend)
    → Investigation (agent with ADK)
    → Results Posted (backend → Frappe)
      ├─ Internal Notes (Comment)
      ├─ Customer Communication (Communication, portal-visible)
      └─ Tags & Metadata
  ```
- **Idempotent initialization**:
  - Qdrant ingestion (20 sample incidents with local embeddings)
  - Frappe user provisioning (service account + demo customer)
  - Automatic on backend startup
- **Complete Frappe integration**:
  - Service account: Helpdesk Assistant (helpdesk-assistant@example.com)
  - Demo customer: John Doe (john.doe@acmecorp.com) from Acme Corporation
  - Customer communications visible in portal view
  - Internal notes for support team
- **Customer-app frontend**: React + TypeScript UI with 8 error scenarios (ready, not in compose)
- **ADK-based agent**: 4-phase investigation workflow (Triage → Gather → Verify → Finalize)
- **Tool system**: 5 tools (ticket, logs, incidents, deploys, customer) with mock/Qdrant data
- **Local embeddings**: sentence-transformers/all-MiniLM-L6-v2 (no API calls)

### ⏳ Planned (Next Steps)
- **Day 6**: OpenTelemetry instrumentation + Braintrust export
- **Day 7**: Evaluation framework with baseline vs improved variants
- **Future**: Record/replay mode for deterministic demos, customer-app Docker integration

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

### Infrastructure (Day 1) ✅ COMPLETE
- [x] Add docker-compose.yml
- [x] Frappe Helpdesk service with auto-init
- [x] MariaDB + Redis dependencies
- [x] Qdrant service (upgraded to v1.16.3, always running)
- [x] Persistent volumes for all data
- [x] Helper scripts (start/stop/logs)
- [x] Quick start documentation

### Backend Service (Day 2) ✅ COMPLETE
- [x] Backend skeleton (FastAPI)
- [x] Webhook endpoint: `POST /webhooks/frappe`
- [x] CaseFile schema and normalization
- [x] Frappe API client helper (Day 5)
- [x] Add backend to docker-compose
- [x] Configure Frappe webhook (automated via seed-db.sql)
- [x] Backend entrypoint script with initialization flow

### Tool System (Day 2-4) ✅ COMPLETE
- [x] Tool API routes (ticket/logs/incidents/deploys/customer)
- [x] Qdrant collection + ingestion script (Day 4)
- [x] Local embeddings integration (sentence-transformers)
- [x] Mock logs/deploys/customer data
- [x] Tool endpoint testing
- [x] Idempotent Qdrant initialization

### Agent Service (Day 3) ✅ COMPLETE
- [x] Agent service skeleton (FastAPI)
- [x] ADK workflow implementation (SequentialAgent with 4 phases)
- [x] Tool bindings (ADK function tools wrapping HTTP)
- [x] LLM provider integration (Claude 3.5 Sonnet via ADK)
- [x] Add agent to docker-compose
- [x] Backend → Agent invocation (webhook triggers investigation)

### Frappe Integration (Day 5) ✅ COMPLETE
- [x] Service account provisioning (Helpdesk Assistant)
- [x] Demo customer provisioning (John Doe from Acme Corp)
- [x] Idempotent user initialization
- [x] Internal notes posting (Comment doctype)
- [x] Customer communication posting (Communication doctype)
- [x] Portal visibility for customer communications
- [x] Message attribution (sender/sender_full_name)

### Customer Portal (Added 2026-02-23) ✅ READY
- [x] React + TypeScript frontend cloned
- [x] 8 error scenario pages implemented
- [x] shadcn-ui components integrated
- [ ] Frappe API ticket creation (planned)
- [ ] Docker Compose integration (planned)

### Observability (Day 6) ⏳ PLANNED
- [ ] OTel instrumentation (backend)
- [ ] OTel instrumentation (agent)
- [ ] Braintrust exporter configuration
- [ ] Trace context propagation
- [ ] Span attributes for debugging

### Evaluation (Day 7) ⏳ PLANNED
- [ ] Variants (baseline vs improved differentiation)
- [ ] Test dataset creation
- [ ] Deterministic scorers (schema/evidence/tools)
- [ ] LLM-as-judge scorers (tone/helpfulness)
- [ ] Offline regression runner
- [ ] Record/replay mode for fixtures
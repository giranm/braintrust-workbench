# Quick Start Guide

Get the Support Desk Investigator demo running in minutes.

## Prerequisites

- Docker and Docker Compose installed
- 4GB+ RAM available
- Ports 8080, 8000, 8001, 6333, 6334 free

## Step 1: Start Services

```bash
# From the project directory
./scripts/start.sh
```

This will:
- Start Frappe Helpdesk, MariaDB, Redis
- Start Qdrant vector database
- Start Backend API service (with automatic Qdrant initialization)
- Start Agent service
- Initialize Frappe bench and install apps (first run takes 5-10 minutes)
- Create site and configure admin user

**First startup**: The initialization takes 5-10 minutes as it clones Frappe, installs dependencies, and sets up the Helpdesk app. Backend will automatically initialize Qdrant with sample data. You can monitor progress with:

```bash
# Watch Frappe initialization
docker compose logs -f frappe

# Watch backend initialization (Qdrant ingestion)
docker compose logs -f backend
```

Look for these messages:
- Frappe: `✅ Initialization complete!` followed by web server starting
- Backend: `✅ Initialization complete!` followed by backend service starting

**Subsequent startups**: Much faster (~30 seconds) as the bench and Qdrant data already exist.

## Step 2: Access Frappe Helpdesk

Open your browser to: **http://localhost:8080**

**Default credentials:**
- Username: `Administrator`
- Password: `admin123`

## Step 3: Create a Test Ticket

### Using Demo Customer Account

1. Navigate to "Helpdesk" in the sidebar
2. Click "New Ticket"
3. Fill in:
   - **Contact**: john.doe@acmecorp.com (pre-configured demo customer)
   - **Subject**: "Checkout page returning 502 errors"
   - **Description**: "Customers are reporting intermittent 502 errors on the checkout page since 9:30 AM. Several failed transactions reported."
   - **Priority**: High
4. Save

The system will automatically:
- Trigger webhook to backend
- Run 4-phase ADK investigation (Triage → Gather → Verify → Finalize)
- Post results back to ticket:
  - Internal notes with evidence summary (Comment doctype)
  - Customer communication (Communication doctype, visible in portal)
  - Confidence score and escalation decision

### View Results

- **Internal view** (desk): http://localhost:8080/desk/hd-ticket/{ticket-id}
- **Customer view** (portal): http://localhost:8080/helpdesk/tickets/{ticket-id}

The customer communication will be attributed to **Helpdesk Assistant** (service account).

## What's Running

- **Frappe Bench** (`http://localhost:8080`) - Development server with Helpdesk app
  - Web server: Port 8080
  - Socketio: Port 9000
  - Includes: Frappe v16, Telephony app, Helpdesk app
  - Auto-configured accounts:
    - Admin: Administrator / admin123
    - Service: Helpdesk Assistant (helpdesk-assistant@example.com)
    - Demo Customer: John Doe (john.doe@acmecorp.com) from Acme Corporation
- **Backend API** (`http://localhost:8000`) - FastAPI service for webhooks and tools
  - Webhook receiver: POST /webhooks/frappe
  - Tool endpoints: /tools/* (incident search, logs, deploys, customer)
  - Frappe API client: Full integration for tickets, comments, communications
  - API docs: http://localhost:8000/docs
  - Automatic initialization:
    - Waits for Qdrant (health checks)
    - Ingests 20 sample incidents
    - Creates Frappe users and customer organization
- **Agent Service** (`http://localhost:8001`) - ADK-based investigation workflow
  - Investigation endpoint: POST /investigate
  - 4-phase workflow: Triage → Gather → Verify → Finalize
  - Uses Claude 3.5 Sonnet via Google ADK
  - LiteLLM provider abstraction
  - API docs: http://localhost:8001/docs
- **Qdrant v1.16.3** (`http://localhost:6333`) - Vector database for incident similarity search
  - Automatically initialized with 20 sample incidents
  - Uses local sentence-transformers embeddings (all-MiniLM-L6-v2, no API calls)
  - Dashboard: http://localhost:6333/dashboard
- **MariaDB 11.8** - Persistent database storage for Frappe
- **Redis 6.2** - Cache and queue backend for Frappe

## Useful Commands

```bash
# View logs
./scripts/logs.sh frappe
./scripts/logs.sh all

# Stop services
./scripts/stop.sh

# Restart services (fast - bench already initialized)
docker compose restart frappe

# Start fresh (delete database, reinitialize everything)
docker compose down -v
./scripts/start.sh

# Access Frappe bench shell (for bench commands)
docker compose exec frappe bash

# Run bench commands directly
docker compose exec frappe bench --help
docker compose exec frappe bench --site support-desk.localhost console
```

## Troubleshooting

### Initialization taking too long
First-time initialization takes 5-10 minutes. Monitor progress:
```bash
docker compose logs -f frappe
```

Look for these stages:
1. `📦 Creating new bench...`
2. `⚙️ Configuring services...`
3. `📥 Installing apps...` (telephony, helpdesk)
4. `🏗️ Creating site...`
5. `✅ Initialization complete!`
6. `web.1 | Running on http://127.0.0.1:8000`

### Services won't start
```bash
# Check if ports are in use
lsof -i :8080
lsof -i :9000

# View detailed logs
docker compose logs frappe
```

### Initialization fails or hangs
```bash
# Reset and start fresh
docker compose down -v
./scripts/start.sh
```

### Can't login
- Default password is `admin123`
- Ensure initialization completed (check for "✅ Initialization complete!" in logs)
- Check logs: `./scripts/logs.sh frappe`

## Next Steps

### Current State (v0.3.0)

The system is **fully operational** with:
- ✅ Frappe Helpdesk with automated initialization (Day 1)
- ✅ Backend service with webhook integration and tool APIs (Day 2)
- ✅ Agent service with Google ADK 4-phase workflow (Day 3)
- ✅ Qdrant vector DB with local embeddings (Day 4)
- ✅ Complete Frappe API integration with service accounts (Day 5)
- ✅ Customer-app frontend (available in src/customer-app/)

### Upcoming Work

- **Day 6**: OpenTelemetry instrumentation + Braintrust integration
- **Day 7**: Evaluation framework with baseline vs improved variants
- **Future**: Record/replay mode, customer-app Docker integration

### Observing Investigations

Watch investigations in real-time:
```bash
# Backend + Agent logs
docker compose logs -f backend agent

# All services
docker compose logs -f
```

### Exploring the System

- **API Documentation**:
  - Backend: http://localhost:8000/docs
  - Agent: http://localhost:8001/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Frappe Desk**: http://localhost:8080/desk
- **Customer Portal**: http://localhost:8080/helpdesk

See `docs/implementation.md` for detailed technical documentation and `docs/architecture.md` for system design.

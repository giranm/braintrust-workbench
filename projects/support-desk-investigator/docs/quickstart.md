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

1. Navigate to "Helpdesk" in the sidebar
2. Click "New Ticket"
3. Fill in:
   - Subject: "Checkout page returning 502 errors"
   - Description: "Customers are reporting intermittent 502 errors on the checkout page since 9:30 AM. Several failed transactions reported."
4. Save

## What's Running

- **Frappe Bench** (`http://localhost:8080`) - Development server with Helpdesk app
  - Web server: Port 8080
  - Socketio: Port 9000
  - Includes: Frappe v16, Telephony app, Helpdesk app
- **Backend API** (`http://localhost:8000`) - FastAPI service for webhooks and tools
  - Webhook receiver: POST /webhooks/frappe
  - Tool endpoints: /tools/* (incident search, logs, deploys, customer)
  - API docs: http://localhost:8000/docs
  - Automatic initialization: Waits for Qdrant, ingests sample data
- **Agent Service** (`http://localhost:8001`) - ADK-based investigation workflow
  - Investigation endpoint: POST /investigate
  - 4-phase workflow: Triage → Gather → Verify → Finalize
  - Uses Claude via Google ADK for reasoning
- **Qdrant v1.16.3** (`http://localhost:6333`) - Vector database for incident similarity search
  - Automatically initialized with 20 sample incidents
  - Uses local sentence-transformers embeddings (no API calls)
- **MariaDB 11.8** - Persistent database storage
- **Redis 6.2** - Cache and queue backend

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

Once Frappe is running, you're ready for:
- **Day 2**: Backend service + webhook integration
- **Day 3**: Agent service with Google ADK
- **Day 4**: Tool system + Qdrant

See `docs/implementation.md` for the full roadmap.

# Quick Start Guide

Get the Support Desk Investigator demo running in minutes.

## Prerequisites

- Docker and Docker Compose installed
- 4GB+ RAM available
- Ports 8080, 6333, 6334 free

## Step 1: Start Services

```bash
# From the project directory
./scripts/start.sh
```

This will:
- Start Frappe Helpdesk, MariaDB, Redis
- Initialize Frappe bench and install apps (first run takes 5-10 minutes)
- Create site and configure admin user

**First startup**: The initialization takes 5-10 minutes as it clones Frappe, installs dependencies, and sets up the Helpdesk app. You can monitor progress with:

```bash
docker compose logs -f frappe
```

Look for the message: `✅ Initialization complete!` followed by the web server starting.

**Subsequent startups**: Much faster (~30 seconds) as the bench already exists.

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
  - Tool endpoints: /tools/*
  - API docs: http://localhost:8000/docs
- **MariaDB 11.8** - Persistent database storage
- **Redis 6.2** - Cache and queue backend
- **Qdrant** - Vector DB (starts with `--profile tools`, not needed yet)

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

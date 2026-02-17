#!/bin/bash
set -e

echo "🚀 Starting Support Desk Investigator services..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update with your API keys."
    echo ""
fi

# Start services
echo "📦 Starting Docker Compose services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for Frappe to be healthy
echo "Waiting for Frappe Helpdesk..."
timeout=300
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose ps frappe | grep -q "Up"; then
        if docker compose logs frappe 2>&1 | grep -q "Listening on"; then
            echo "✅ Frappe is ready!"
            break
        fi
    fi

    if [ $elapsed -eq 0 ]; then
        echo "   (This may take 2-3 minutes on first run)"
    fi

    sleep 5
    elapsed=$((elapsed + 5))

    if [ $((elapsed % 30)) -eq 0 ]; then
        echo "   Still waiting... ($elapsed seconds elapsed)"
    fi
done

if [ $elapsed -ge $timeout ]; then
    echo "⚠️  Timeout waiting for Frappe. Check logs with: docker compose logs frappe"
    exit 1
fi

echo ""
echo "✅ All services are running!"
echo ""
echo "📋 Service URLs:"
echo "   - Frappe Helpdesk: http://localhost:8080"
echo "   - Default login: Administrator / admin123"
echo ""
echo "📊 Useful commands:"
echo "   - View logs:        docker compose logs -f"
echo "   - Stop services:    docker compose down"
echo "   - Restart Frappe:   docker compose restart frappe"
echo "   - Access shell:     docker compose exec frappe bash"
echo ""

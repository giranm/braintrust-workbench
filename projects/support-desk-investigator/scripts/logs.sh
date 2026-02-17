#!/bin/bash

SERVICE=${1:-frappe}

if [ "$SERVICE" = "all" ]; then
    docker compose logs -f
else
    echo "📜 Showing logs for: $SERVICE"
    echo "   (Use ./scripts/logs.sh all to see all services)"
    echo ""
    docker compose logs -f $SERVICE
fi

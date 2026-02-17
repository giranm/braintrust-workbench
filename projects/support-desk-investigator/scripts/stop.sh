#!/bin/bash
set -e

echo "🛑 Stopping Support Desk Investigator services..."
docker compose down

echo "✅ Services stopped."
echo ""
echo "💡 To remove all data (start fresh):"
echo "   docker compose down -v"

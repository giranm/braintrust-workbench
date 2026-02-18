#!/bin/bash
set -e

echo "🚀 Backend initialization starting..."

# Wait for Qdrant to be available
echo "⏳ Waiting for Qdrant to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f http://qdrant:6333/ > /dev/null 2>&1; then
        echo "✅ Qdrant is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ Qdrant failed to start after $MAX_RETRIES attempts"
        echo "⚠️  Proceeding anyway - ingestion will use fallback mock data"
        break
    fi
    echo "⏳ Waiting for Qdrant... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

# Run Qdrant ingestion (idempotent - will skip if data exists)
echo "📊 Running Qdrant ingestion (idempotent)..."
python /app/scripts/ingest-qdrant.py || {
    echo "⚠️  Qdrant ingestion failed, but continuing startup (will use mock data fallback)"
}

echo "✅ Initialization complete!"
echo "🚀 Starting backend service..."

# Start the backend service
exec uvicorn src.backend.app:app --host 0.0.0.0 --port 8000 --reload

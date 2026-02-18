"""Tool API endpoints for agent to call during investigation."""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Qdrant and local embedding model
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

qdrant_client: Optional[AsyncQdrantClient] = None
embedding_model: Optional[SentenceTransformer] = None

try:
    # Disable version check due to client/server version mismatch
    qdrant_client = AsyncQdrantClient(url=QDRANT_URL)
    # Load local embedding model (runs on CPU, ~80MB)
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info(f"✅ Qdrant and local embedding model ({EMBEDDING_MODEL_NAME}) initialized for incident search")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize Qdrant/embedding model: {e}. Using mock data fallback.")


# ============================================================================
# Request/Response Models
# ============================================================================


class LogQueryRequest(BaseModel):
    """Request for log query."""

    query: str
    time_range_minutes: int = 60
    limit: int = 100


class LogEntry(BaseModel):
    """Log entry response."""

    timestamp: datetime
    level: str
    service: str
    message: str
    metadata: dict = {}


class IncidentSearchRequest(BaseModel):
    """Request for incident search."""

    query: str
    limit: int = 10


class Incident(BaseModel):
    """Similar incident response."""

    incident_id: str
    title: str
    description: str
    resolution: str
    resolved_at: datetime
    similarity_score: float


class Deployment(BaseModel):
    """Deployment information."""

    deploy_id: str
    service: str
    version: str
    deployed_at: datetime
    deployed_by: str
    status: str
    changes: list[str]


class Customer(BaseModel):
    """Customer information."""

    customer_id: str
    name: str
    email: str
    tier: str
    account_created: datetime
    total_tickets: int
    recent_tickets: list[str]
    metadata: dict = {}


# ============================================================================
# Tool Endpoints
# ============================================================================


@router.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Fetch ticket details.

    TODO: Connect to Frappe API to fetch real ticket data.
    For now, returns mock data.
    """
    logger.info(f"🎫 Fetching ticket: {ticket_id}")

    # Mock ticket data
    return {
        "ticket_id": ticket_id,
        "subject": "Checkout page returning 502 errors",
        "description": (
            "Multiple customers reporting intermittent 502 errors on checkout "
            "page since 9:30 AM. Payment processing appears to be affected."
        ),
        "priority": "High",
        "status": "Open",
        "created_at": datetime.now().isoformat(),
        "customer_id": "CUST-001",
    }


@router.post("/logs/query")
async def query_logs(request: LogQueryRequest):
    """Query logs for error patterns.

    TODO: Connect to real log aggregation system (Day 4).
    For now, returns mock log data.
    """
    logger.info(f"📋 Querying logs: {request.query}")

    # Mock log data based on query
    mock_logs = []
    now = datetime.now()

    if "502" in request.query or "error" in request.query.lower():
        # Generate mock 502 errors
        for i in range(min(5, request.limit)):
            mock_logs.append(
                LogEntry(
                    timestamp=now - timedelta(minutes=i * 10),
                    level="ERROR",
                    service="checkout-api",
                    message=f"502 Bad Gateway: upstream connection timeout to payment-service",
                    metadata={
                        "endpoint": "/api/v1/checkout/complete",
                        "duration_ms": 30000,
                        "user_id": f"user-{100+i}",
                    },
                )
            )

    return {"logs": [log.dict() for log in mock_logs], "total": len(mock_logs)}


@router.post("/incidents/search")
async def search_incidents(request: IncidentSearchRequest):
    """Search for similar past incidents using Qdrant vector similarity search.

    Uses local sentence-transformers model for embeddings (no API calls).
    Falls back to mock data if Qdrant is unavailable or not configured.
    """
    logger.info(f"🔍 Searching incidents: {request.query}")

    # Try Qdrant vector search first
    if qdrant_client and embedding_model:
        try:
            # Generate embedding for search query using local model
            logger.debug("Generating embedding using local model")
            query_vector = embedding_model.encode(request.query).tolist()

            # Search Qdrant for similar incidents
            logger.debug(f"Searching Qdrant collection 'incidents' (limit={request.limit})")
            search_results = await qdrant_client.query_points(
                collection_name="incidents",
                query=query_vector,
                limit=request.limit,
            )

            if search_results and search_results.points:
                logger.info(f"✅ Found {len(search_results.points)} similar incidents from Qdrant")
                incidents = []
                for result in search_results.points:
                    payload = result.payload
                    incidents.append(
                        Incident(
                            incident_id=payload.get("incident_id", "unknown"),
                            title=payload.get("title", ""),
                            description=payload.get("description", ""),
                            resolution=payload.get("resolution", ""),
                            resolved_at=datetime.fromisoformat(payload.get("resolved_at"))
                            if payload.get("resolved_at")
                            else datetime.now(),
                            similarity_score=result.score,
                        )
                    )

                return {
                    "incidents": [inc.dict() for inc in incidents],
                    "total": len(incidents),
                }

        except Exception as e:
            logger.warning(f"⚠️ Qdrant search failed: {e}. Falling back to mock data.")

    # Fallback to mock data if Qdrant unavailable or search failed
    logger.info("Using mock incident data (Qdrant not available)")
    mock_incidents = []

    if "502" in request.query or "checkout" in request.query.lower():
        mock_incidents.append(
            Incident(
                incident_id="INC-2024-089",
                title="Checkout API 502 errors during payment processing",
                description=(
                    "Intermittent 502 errors on checkout completion. "
                    "Root cause: payment service database connection pool exhaustion."
                ),
                resolution=(
                    "Increased database connection pool size from 10 to 50. "
                    "Added connection timeout monitoring."
                ),
                resolved_at=datetime.now() - timedelta(days=45),
                similarity_score=0.87,
            )
        )

        mock_incidents.append(
            Incident(
                incident_id="INC-2024-112",
                title="Payment gateway timeout causing 502s",
                description=(
                    "Upstream payment gateway experiencing slowness, "
                    "causing reverse proxy to return 502 after 30s timeout."
                ),
                resolution=(
                    "Implemented circuit breaker pattern and fallback queue. "
                    "Increased timeout to 45s with retry logic."
                ),
                resolved_at=datetime.now() - timedelta(days=30),
                similarity_score=0.76,
            )
        )

    return {
        "incidents": [inc.dict() for inc in mock_incidents],
        "total": len(mock_incidents),
    }


@router.get("/deploys/recent")
async def get_recent_deploys(hours: int = 24, limit: int = 10):
    """Get recent deployments.

    TODO: Connect to deployment tracking system (Day 4).
    For now, returns mock deployment data.
    """
    logger.info(f"🚀 Fetching recent deployments (last {hours}h)")

    now = datetime.now()
    mock_deploys = [
        Deployment(
            deploy_id="DEPLOY-20260217-001",
            service="checkout-api",
            version="v2.34.1",
            deployed_at=now - timedelta(hours=3),
            deployed_by="deploy-bot",
            status="success",
            changes=[
                "Updated payment gateway client library",
                "Increased default request timeout",
                "Fixed null pointer in order validation",
            ],
        ),
        Deployment(
            deploy_id="DEPLOY-20260217-002",
            service="payment-service",
            version="v1.89.0",
            deployed_at=now - timedelta(hours=4),
            deployed_by="deploy-bot",
            status="success",
            changes=[
                "Database connection pool optimizations",
                "Added health check endpoint",
                "Performance improvements",
            ],
        ),
    ]

    return {"deployments": [d.dict() for d in mock_deploys], "total": len(mock_deploys)}


@router.get("/customer/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer information.

    TODO: Connect to customer database (Day 4).
    For now, returns mock customer data.
    """
    logger.info(f"👤 Fetching customer: {customer_id}")

    # Mock customer data
    mock_customer = Customer(
        customer_id=customer_id,
        name="Acme Corporation",
        email="support@acmecorp.example.com",
        tier="enterprise",
        account_created=datetime.now() - timedelta(days=365),
        total_tickets=47,
        recent_tickets=["TKT-00012", "TKT-00008", "TKT-00003"],
        metadata={
            "contract_value": "$50,000/year",
            "primary_contact": "Jane Smith",
            "timezone": "America/New_York",
        },
    )

    return mock_customer.dict()


@router.get("/health")
async def tools_health():
    """Tools API health check."""
    return {
        "status": "healthy",
        "endpoint": "tools",
        "available_tools": [
            "ticket",
            "logs/query",
            "incidents/search",
            "deploys/recent",
            "customer",
        ],
    }

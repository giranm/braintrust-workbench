"""ADK tool functions for backend API integration.

Wraps backend HTTP endpoints as ADK function tools that can be
used by agents during investigation workflows.
"""

import httpx
from typing import Optional

# Global HTTP client and backend URL
BACKEND_URL = "http://backend:8000"
client: Optional[httpx.AsyncClient] = None


async def get_ticket_details(ticket_id: str) -> dict:
    """Fetches full details for a support ticket.

    Use this when you need complete ticket information including
    subject, description, priority, status, and customer info.

    Args:
        ticket_id: The unique ticket identifier

    Returns:
        Ticket data with all fields
    """
    global client
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)

    response = await client.get(f"{BACKEND_URL}/tools/ticket/{ticket_id}")
    response.raise_for_status()
    return response.json()


async def query_logs(
    query: str,
    time_range_minutes: int = 60,
    limit: int = 10,
) -> dict:
    """Queries log aggregation system for error patterns.

    Use this when investigating errors, timeouts, or service issues.
    Search for error codes (502, 500), exception messages, or service names.

    Args:
        query: Search query string (e.g., "502 error checkout")
        time_range_minutes: How far back to search (default: 60)
        limit: Max log entries to return (default: 10)

    Returns:
        Dict with 'logs' list and 'total' count
    """
    global client
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)

    response = await client.post(
        f"{BACKEND_URL}/tools/logs/query",
        json={
            "query": query,
            "time_range_minutes": time_range_minutes,
            "limit": limit,
        },
    )
    response.raise_for_status()
    return response.json()


async def search_similar_incidents(query: str, limit: int = 5) -> dict:
    """Search for similar past incidents in the knowledge base.

    Use this to find historical tickets with similar symptoms or error patterns.
    Helps identify known issues and proven solutions.

    Args:
        query: Search query string (e.g., "checkout timeout")
        limit: Max incidents to return (default: 5)

    Returns:
        Dict with 'incidents' list and 'total' count
    """
    global client
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)

    response = await client.post(
        f"{BACKEND_URL}/tools/incidents/search",
        json={"query": query, "limit": limit},
    )
    response.raise_for_status()
    return response.json()


async def get_recent_deployments(hours: int = 24) -> dict:
    """Get recent deployment history.

    Use this when investigating issues that may be related to recent changes.
    Deployments are a common cause of new errors or behavioral changes.

    Args:
        hours: Look back window in hours (default: 24)

    Returns:
        Dict with 'deployments' list containing version, service, timestamp
    """
    global client
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)

    response = await client.get(
        f"{BACKEND_URL}/tools/deploys/recent",
        params={"hours": hours},
    )
    response.raise_for_status()
    return response.json()


async def get_customer_info(customer_id: str) -> dict:
    """Get customer profile and account information.

    Use this to understand customer context including tier, account health,
    and service configuration. Helps tailor response appropriately.

    Args:
        customer_id: Customer identifier

    Returns:
        Dict with customer name, tier, signup date, and metadata
    """
    global client
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)

    response = await client.get(f"{BACKEND_URL}/tools/customer/{customer_id}")
    response.raise_for_status()
    return response.json()


def create_investigation_tools(backend_url: str) -> list:
    """Initialize tools with backend URL and return list for ADK agent.

    Args:
        backend_url: Base URL for backend service

    Returns:
        List of async function tools for ADK agent
    """
    global BACKEND_URL, client
    BACKEND_URL = backend_url.rstrip("/")
    client = httpx.AsyncClient(timeout=30.0)

    return [
        get_ticket_details,
        query_logs,
        search_similar_incidents,
        get_recent_deployments,
        get_customer_info,
    ]

"""Tool client for calling backend API endpoints."""

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class ToolClient:
    """HTTP client for backend tool endpoints."""

    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"🔧 Initialized tool client (backend={backend_url})")

    async def get_ticket(self, ticket_id: str) -> dict:
        """Get full ticket details.

        Args:
            ticket_id: Ticket identifier

        Returns:
            Ticket data dict
        """
        url = f"{self.backend_url}/tools/ticket/{ticket_id}"
        logger.info(f"📋 GET {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to get ticket: {e}")
            return {}

    async def query_logs(
        self,
        query: str,
        service: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Query logs for error patterns.

        Args:
            query: Search query string
            service: Optional service name filter
            limit: Max results to return

        Returns:
            List of log entries
        """
        url = f"{self.backend_url}/tools/logs/query"
        payload = {"query": query, "limit": limit}
        if service:
            payload["service"] = service

        logger.info(f"📋 POST {url} (query='{query}')")

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("logs", [])
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to query logs: {e}")
            return []

    async def search_incidents(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        """Search for similar past incidents.

        Args:
            query: Search query string
            limit: Max results to return

        Returns:
            List of similar incidents
        """
        url = f"{self.backend_url}/tools/incidents/search"
        payload = {"query": query, "limit": limit}

        logger.info(f"🔍 POST {url} (query='{query}')")

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("incidents", [])
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to search incidents: {e}")
            return []

    async def get_recent_deploys(self, hours: int = 24) -> list[dict]:
        """Get recent deployments.

        Args:
            hours: Look back window in hours

        Returns:
            List of recent deployments
        """
        url = f"{self.backend_url}/tools/deploys/recent"
        params = {"hours": hours}

        logger.info(f"📦 GET {url}?hours={hours}")

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("deployments", [])
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to get deployments: {e}")
            return []

    async def get_customer(self, customer_id: str) -> dict:
        """Get customer information.

        Args:
            customer_id: Customer identifier

        Returns:
            Customer data dict
        """
        url = f"{self.backend_url}/tools/customer/{customer_id}"

        logger.info(f"👤 GET {url}")

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to get customer: {e}")
            return {}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

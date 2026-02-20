"""Frappe API client for posting investigation results back to tickets.

Handles authentication and communication with Frappe Helpdesk API to:
- Post internal notes/comments
- Add customer reply drafts
- Update ticket status and tags

References:
- https://docs.frappe.io/framework/user/en/api/rest
- https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication
- https://discuss.frappe.io/t/creating-a-comment-via-rest-api-in-doctype-of-customer/20997
"""

import logging
import os
from typing import Optional
from base64 import b64encode

import httpx

logger = logging.getLogger(__name__)


class FrappeClient:
    """Client for interacting with Frappe Helpdesk API."""

    def __init__(
        self,
        base_url: str = "http://frappe:8000",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ):
        """Initialize Frappe client.

        Args:
            base_url: Frappe instance URL
            api_key: API key for authentication
            api_secret: API secret for authentication

        Note: Generate API keys in Frappe: User → API Access → Generate Keys
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("FRAPPE_API_KEY", "Administrator")
        self.api_secret = api_secret or os.getenv("FRAPPE_API_SECRET", "admin123")

        # Create HTTP client with authentication
        auth_token = f"{self.api_key}:{self.api_secret}"
        auth_header = b64encode(auth_token.encode()).decode()

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
            # Disable Expect: 100-continue header (causes 417 errors with some servers)
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

        logger.info(f"🔗 Initialized Frappe client (base_url={base_url})")

    async def post_internal_note(
        self,
        ticket_id: str,
        notes: str,
        comment_type: str = "Comment",
    ) -> dict:
        """Post internal investigation notes to a ticket.

        Internal notes are visible only to agents, not customers.

        Args:
            ticket_id: Ticket ID (e.g., "HD-TICKET-00001" or just "1")
            notes: Investigation notes to post
            comment_type: Type of comment (default: "Comment" for internal)

        Returns:
            Response data from Frappe API

        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info(f"📝 Posting internal note to ticket {ticket_id}")

        # Normalize ticket ID format
        if not ticket_id.startswith("HD-TICKET-"):
            ticket_id = str(ticket_id)

        try:
            # Create Comment document for internal note
            comment_data = {
                "comment_type": comment_type,
                "reference_doctype": "HD Ticket",
                "reference_name": ticket_id,
                "content": notes,
            }

            response = await self.client.post(
                "/api/resource/Comment",
                json=comment_data,
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Internal note posted successfully to ticket {ticket_id}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to post internal note: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                logger.error(f"Response body: {e.response.text}")
            raise

    async def add_comment_draft(
        self,
        ticket_id: str,
        reply_text: str,
    ) -> dict:
        """Add a customer reply draft to a ticket (internal view).

        This creates a draft reply that agents can review and send.
        Shows in the internal desk view, not the customer portal.

        Args:
            ticket_id: Ticket ID
            reply_text: Draft reply text for the customer

        Returns:
            Response data from Frappe API
        """
        logger.info(f"💬 Adding reply draft to ticket {ticket_id} (internal)")

        try:
            comment_data = {
                "comment_type": "Info",  # Info type for drafts/suggestions
                "reference_doctype": "HD Ticket",
                "reference_name": ticket_id,
                "content": f"**Suggested Customer Reply:**\n\n{reply_text}",
            }

            response = await self.client.post(
                "/api/resource/Comment",
                json=comment_data,
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Reply draft added to ticket {ticket_id}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to add reply draft: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                logger.error(f"Response body: {e.response.text}")
            raise

    async def post_customer_communication(
        self,
        ticket_id: str,
        message: str,
        subject: Optional[str] = None,
    ) -> dict:
        """Post a customer-facing communication to a ticket.

        This creates a Communication record that appears in the customer portal.

        Args:
            ticket_id: Ticket ID
            message: Message content for the customer
            subject: Optional subject line

        Returns:
            Response data from Frappe API
        """
        logger.info(f"📧 Posting customer communication to ticket {ticket_id}")

        try:
            # Create Communication document for customer-facing message
            # Note: communication_medium must be "Email" (not "Portal") for Frappe Helpdesk
            # Set sender as "Helpdesk Assistant" service account for proper attribution
            comm_data = {
                "communication_type": "Communication",
                "communication_medium": "Email",
                "sent_or_received": "Sent",
                "reference_doctype": "HD Ticket",
                "reference_name": ticket_id,
                "subject": subject or "Re: Your Support Request",
                "content": message,
                "status": "Linked",
                "sender": "helpdesk-assistant@example.com",
                "sender_full_name": "Helpdesk Assistant",
            }

            response = await self.client.post(
                "/api/resource/Communication",
                json=comm_data,
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Customer communication posted to ticket {ticket_id}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to post customer communication: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                logger.error(f"Response body: {e.response.text}")
            raise

    async def update_ticket_status(
        self,
        ticket_id: str,
        status: str,
    ) -> dict:
        """Update ticket status.

        Args:
            ticket_id: Ticket ID
            status: New status (e.g., "Open", "Replied", "Resolved", "Closed")

        Returns:
            Response data from Frappe API
        """
        logger.info(f"🔄 Updating ticket {ticket_id} status to {status}")

        try:
            # Update HD Ticket document
            update_data = {"status": status}

            response = await self.client.put(
                f"/api/resource/HD Ticket/{ticket_id}",
                json=update_data,
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Ticket {ticket_id} status updated to {status}")
            return result

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to update ticket status: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    async def add_tags(
        self,
        ticket_id: str,
        tags: list[str],
    ) -> dict:
        """Add tags to a ticket.

        Args:
            ticket_id: Ticket ID
            tags: List of tags to add

        Returns:
            Response data from Frappe API
        """
        logger.info(f"🏷️  Adding tags to ticket {ticket_id}: {tags}")

        try:
            # Add tags using Tag Link doctype
            results = []
            for tag in tags:
                tag_data = {
                    "document_type": "HD Ticket",
                    "document_name": ticket_id,
                    "tag": tag,
                }

                response = await self.client.post(
                    "/api/resource/Tag Link",
                    json=tag_data,
                )
                # Ignore if tag already exists (409 conflict)
                if response.status_code not in [200, 201, 409]:
                    response.raise_for_status()

                results.append(response.json() if response.status_code in [200, 201] else {"tag": tag, "exists": True})

            logger.info(f"✅ Tags added to ticket {ticket_id}")
            return {"tags": results}

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to add tags: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    async def get_ticket(self, ticket_id: str) -> dict:
        """Fetch ticket details from Frappe.

        Args:
            ticket_id: Ticket ID

        Returns:
            Ticket data
        """
        logger.info(f"📋 Fetching ticket {ticket_id} from Frappe")

        try:
            response = await self.client.get(f"/api/resource/HD Ticket/{ticket_id}")
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Ticket {ticket_id} fetched successfully")
            return result.get("data", result)

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to fetch ticket: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

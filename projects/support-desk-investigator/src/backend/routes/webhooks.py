"""Webhook endpoints for receiving ticket events from Frappe."""

import logging
import os
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Request

from ...common.schemas import CaseFile, TicketPriority, TicketStatus

logger = logging.getLogger(__name__)
router = APIRouter()

# Agent service URL
AGENT_URL = os.getenv("AGENT_URL", "http://agent:8001")


@router.post("/frappe")
async def receive_frappe_webhook(request: Request):
    """Receive webhook from Frappe Helpdesk.

    Frappe sends webhooks when tickets are created or updated.
    This endpoint normalizes the Frappe ticket format into our CaseFile schema.

    Expected Frappe webhook payload:
    {
        "name": "TKT-00001",
        "subject": "...",
        "description": "...",
        "status": "Open",
        "priority": "Medium",
        "contact": {"email": "...", "name": "..."},
        "creation": "2026-02-17 10:30:00",
        ...
    }
    """
    try:
        payload = await request.json()
        logger.info(f"📥 Received Frappe webhook: {payload.get('name', 'unknown')}")
        logger.info(f"📦 Full webhook payload: {payload}")

        # Normalize Frappe payload to CaseFile
        case_file = _normalize_frappe_ticket(payload)

        logger.info(f"✅ Normalized ticket {case_file.ticket_id}")

        # Trigger agent investigation
        investigation_result = await _trigger_investigation(case_file)

        if investigation_result:
            logger.info(
                f"✅ Investigation complete for {case_file.ticket_id} "
                f"(confidence={investigation_result.confidence:.0%}, "
                f"escalate={investigation_result.should_escalate})"
            )
            # TODO Day 4: Post results back to Frappe
            # For now, just log the results
            logger.info(f"📝 Customer reply: {investigation_result.customer_reply[:100]}...")
            logger.info(f"📝 Internal notes: {investigation_result.internal_notes[:100]}...")

            return {
                "status": "investigated",
                "ticket_id": case_file.ticket_id,
                "confidence": investigation_result.confidence,
                "should_escalate": investigation_result.should_escalate,
                "investigation_time_ms": investigation_result.investigation_time_ms,
            }
        else:
            # Investigation failed, acknowledge receipt only
            return {
                "status": "received",
                "ticket_id": case_file.ticket_id,
                "message": "Ticket received, investigation pending",
            }

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _normalize_frappe_ticket(payload: dict) -> CaseFile:
    """Normalize Frappe ticket payload to CaseFile format.

    Args:
        payload: Raw webhook payload from Frappe

    Returns:
        Normalized CaseFile
    """
    # Extract contact info (may be nested object, string, or None)
    contact = payload.get("contact")
    if contact is None:
        customer_email = None
        customer_name = None
    elif isinstance(contact, str):
        customer_email = contact
        customer_name = None
    elif isinstance(contact, dict):
        customer_email = contact.get("email")
        customer_name = contact.get("name")
    else:
        customer_email = None
        customer_name = None

    # Parse timestamps
    created_at = payload.get("creation")
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace(" ", "T"))
        except ValueError:
            created_at = datetime.now()
    else:
        created_at = datetime.now()

    # Map priority (handle case variations)
    priority_str = payload.get("priority", "Medium")
    try:
        priority = TicketPriority(priority_str)
    except ValueError:
        priority = TicketPriority.MEDIUM

    # Map status
    status_str = payload.get("status", "Open")
    try:
        status = TicketStatus(status_str)
    except ValueError:
        status = TicketStatus.OPEN

    # Extract tags
    tags = payload.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    # Get ticket ID (may be int or string)
    ticket_id = payload.get("name", "unknown")
    if isinstance(ticket_id, int):
        ticket_id = str(ticket_id)

    # Get description and strip HTML tags (basic cleanup)
    description = payload.get("description", "")
    if description:
        # Simple HTML tag removal (for basic cases)
        import re
        description = re.sub(r'<[^>]+>', '', description).strip()

    return CaseFile(
        ticket_id=ticket_id,
        subject=payload.get("subject", ""),
        description=description,
        priority=priority,
        status=status,
        customer_id=payload.get("customer"),
        customer_email=customer_email,
        customer_name=customer_name,
        created_at=created_at,
        updated_at=datetime.now(),
        tags=tags,
        metadata=payload,  # Store full payload for reference
    )


async def _trigger_investigation(case_file: CaseFile):
    """Trigger investigation by calling agent service.

    Args:
        case_file: Normalized ticket data

    Returns:
        InvestigationResult or None if failed
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info(f"🤖 Triggering investigation for {case_file.ticket_id}")
            response = await client.post(
                f"{AGENT_URL}/investigate",
                json={"case_file": case_file.model_dump(mode='json')},
            )
            response.raise_for_status()
            result_data = response.json()

            # Import here to avoid circular dependency
            from ...common.schemas import InvestigationResult
            return InvestigationResult(**result_data)

    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to trigger investigation: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error during investigation: {e}", exc_info=True)
        return None


@router.get("/health")
async def webhook_health():
    """Webhook service health check."""
    return {"status": "healthy", "endpoint": "webhooks"}

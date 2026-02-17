"""Common data schemas for the Support Desk Investigator."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TicketPriority(str, Enum):
    """Ticket priority levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class TicketStatus(str, Enum):
    """Ticket status values."""

    OPEN = "Open"
    REPLIED = "Replied"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class CaseFile(BaseModel):
    """Normalized case file from Frappe ticket.

    This is the standardized format used throughout the investigation
    pipeline, regardless of the source ticketing system.
    """

    ticket_id: str = Field(..., description="Unique ticket identifier")
    subject: str = Field(..., description="Ticket subject/title")
    description: str = Field(..., description="Detailed problem description")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_name: Optional[str] = Field(None, description="Customer name")
    created_at: datetime = Field(..., description="Ticket creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    tags: list[str] = Field(default_factory=list, description="Ticket tags")
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata from source system",
    )


class Evidence(BaseModel):
    """Evidence item supporting an investigation conclusion."""

    source: str = Field(..., description="Evidence source (logs, incidents, etc.)")
    content: str = Field(..., description="Evidence content or description")
    timestamp: Optional[datetime] = Field(None, description="When evidence was found")
    relevance_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Relevance score (0-1)"
    )


class Action(BaseModel):
    """Recommended action from investigation."""

    description: str = Field(..., description="Action description")
    priority: str = Field(..., description="Action priority (low/medium/high)")
    assignee: Optional[str] = Field(None, description="Suggested assignee")


class InvestigationResult(BaseModel):
    """Results from agent investigation."""

    ticket_id: str = Field(..., description="Ticket being investigated")
    customer_reply: str = Field(..., description="Draft reply for the customer")
    internal_notes: str = Field(
        ..., description="Internal notes for engineering team"
    )
    evidence: list[Evidence] = Field(
        default_factory=list, description="Evidence supporting conclusions"
    )
    actions: list[Action] = Field(
        default_factory=list, description="Recommended actions"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Investigation confidence (0-1)"
    )
    should_escalate: bool = Field(
        default=False, description="Whether to escalate to human"
    )
    investigation_time_ms: Optional[int] = Field(
        None, description="Investigation duration in milliseconds"
    )

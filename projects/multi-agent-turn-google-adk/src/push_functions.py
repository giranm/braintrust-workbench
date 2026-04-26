"""Self-contained function definitions for `braintrust push`.

This file is designed to be pushed with:
    braintrust push src/push_functions.py

It registers tool code functions in Braintrust so the Python source
is visible alongside the tool schemas. Kept separate from setup_managed.py
to avoid heavy google-adk imports that braintrust push doesn't need.
"""

import os
import random

import braintrust
from pydantic import BaseModel, Field

PROJECT = os.environ.get("BRAINTRUST_PROJECT", "multi-agent-turn-google-adk")
project = braintrust.projects.create(PROJECT)


# ---------------------------------------------------------------------------
# Tool implementations (inlined to avoid google-adk import chain)
# ---------------------------------------------------------------------------

MOCK_ORDERS = {
    "12345": {
        "order_id": "12345",
        "status": "in_transit",
        "tracking_url": "https://tracking.example.com/12345",
        "eta": "2026-04-30",
        "items": ["Wireless Headphones", "USB-C Cable"],
        "total": 89.99,
    },
    "67890": {
        "order_id": "67890",
        "status": "delivered",
        "tracking_url": "https://tracking.example.com/67890",
        "eta": "2026-04-20",
        "items": ["Mechanical Keyboard"],
        "total": 149.99,
    },
    "11111": {
        "order_id": "11111",
        "status": "processing",
        "tracking_url": None,
        "eta": "2026-05-05",
        "items": ["Standing Desk", "Monitor Arm"],
        "total": 599.99,
    },
}

FAQ_ENTRIES = [
    {"question": "What is your return policy?",
     "answer": "You can return most items within 30 days of delivery for a full refund. Items must be in original condition with packaging."},
    {"question": "How long does shipping take?",
     "answer": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. Free shipping on orders over $50."},
    {"question": "How do I track my order?",
     "answer": "You can track your order using the tracking URL provided in your shipping confirmation email, or ask us with your order ID."},
    {"question": "Do you offer international shipping?",
     "answer": "Yes, we ship to over 50 countries. International shipping typically takes 10-15 business days. Additional customs fees may apply."},
    {"question": "How do I change my shipping address?",
     "answer": "You can change your shipping address before the order ships by contacting support with your order ID. Once shipped, the address cannot be changed."},
    {"question": "What payment methods do you accept?",
     "answer": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay."},
]


def _normalize_id(order_id: str) -> str:
    return order_id.strip().lstrip("#")


def lookup_order(order_id: str) -> dict:
    """Look up an order by its ID. Returns order status, tracking URL, ETA, items, and total."""
    order = MOCK_ORDERS.get(_normalize_id(order_id))
    if order is None:
        return {"error": f"Order {order_id} not found."}
    return order


def cancel_order(order_id: str, reason: str) -> dict:
    """Cancel an order. Only orders that are still processing can be cancelled."""
    order = MOCK_ORDERS.get(_normalize_id(order_id))
    if order is None:
        return {"error": f"Order {order_id} not found."}
    if order["status"] != "processing":
        return {"success": False, "message": f"Cannot cancel order {order_id} — status is '{order['status']}'."}
    return {"success": True, "message": f"Order {order_id} has been cancelled. Reason: {reason}", "refund_initiated": True}


def process_refund(order_id: str, amount: float) -> dict:
    """Process a refund for an order. Returns a confirmation with a reference number."""
    order = MOCK_ORDERS.get(_normalize_id(order_id))
    if order is None:
        return {"error": f"Order {order_id} not found."}
    if amount > order["total"]:
        return {"success": False, "message": f"Refund amount ${amount:.2f} exceeds order total ${order['total']:.2f}."}
    ref = f"REF-{random.randint(100000, 999999)}"
    return {"success": True, "reference_number": ref, "amount_refunded": amount, "message": f"Refund of ${amount:.2f} processed. Reference: {ref}"}


def get_invoice(order_id: str) -> dict:
    """Retrieve the invoice for an order, including line items and a PDF link."""
    order_id = _normalize_id(order_id)
    order = MOCK_ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id} not found."}
    return {"order_id": order_id, "invoice_url": f"https://invoices.example.com/{order_id}.pdf",
            "line_items": [{"item": item, "qty": 1} for item in order["items"]], "total": order["total"]}


def search_faq(query: str) -> dict:
    """Search the FAQ knowledge base. Returns the top 3 matching entries."""
    query_words = set(query.lower().split())
    scored = []
    for entry in FAQ_ENTRIES:
        entry_words = set(entry["question"].lower().split()) | set(entry["answer"].lower().split())
        overlap = len(query_words & entry_words)
        scored.append((overlap, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return {"results": [entry for _, entry in scored[:3]]}


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class LookupOrderInput(BaseModel):
    order_id: str = Field(description="The order ID to look up")


class CancelOrderInput(BaseModel):
    order_id: str = Field(description="The order ID to cancel")
    reason: str = Field(description="Reason for cancellation")


class ProcessRefundInput(BaseModel):
    order_id: str = Field(description="The order ID to refund")
    amount: float = Field(description="Refund amount in dollars")


class GetInvoiceInput(BaseModel):
    order_id: str = Field(description="The order ID to retrieve the invoice for")


class SearchFaqInput(BaseModel):
    query: str = Field(description="Search query for the FAQ knowledge base")


# ---------------------------------------------------------------------------
# Register tools (discovered by braintrust push)
# ---------------------------------------------------------------------------

project.tools.create(handler=lookup_order, name="lookup_order", slug="lookup-order",
                     description="Look up an order by its ID.", parameters=LookupOrderInput, if_exists="replace")
project.tools.create(handler=cancel_order, name="cancel_order", slug="cancel-order",
                     description="Cancel an order (processing only).", parameters=CancelOrderInput, if_exists="replace")
project.tools.create(handler=process_refund, name="process_refund", slug="process-refund",
                     description="Process a refund for an order.", parameters=ProcessRefundInput, if_exists="replace")
project.tools.create(handler=get_invoice, name="get_invoice", slug="get-invoice",
                     description="Retrieve the invoice for an order.", parameters=GetInvoiceInput, if_exists="replace")
project.tools.create(handler=search_faq, name="search_faq", slug="search-faq",
                     description="Search the FAQ knowledge base.", parameters=SearchFaqInput, if_exists="replace")


# ---------------------------------------------------------------------------
# Code-based scorers (discovered by braintrust push)
# ---------------------------------------------------------------------------


class ToolCallAccuracyInput(BaseModel):
    output: str = Field(description="The agent's response text")
    expected: str = Field(description="JSON string of expected tool names")
    metadata: str = Field(description="JSON string with tools_called list")


def tool_call_accuracy(output: str, expected: str, metadata: str = "{}") -> dict:
    """Span-level scorer: did the agent call the expected tool(s)?

    Compares the set of tools the agent actually called against the
    expected set. Returns 1.0 for exact match, partial credit for
    subset matches, 0.0 for complete mismatch.
    """
    import json as _json

    try:
        expected_tools = set(_json.loads(expected)) if expected else set()
    except (ValueError, TypeError):
        expected_tools = set()

    try:
        meta = _json.loads(metadata) if metadata else {}
        actual_tools = set(meta.get("tools_called", []))
    except (ValueError, TypeError):
        actual_tools = set()

    if not expected_tools and not actual_tools:
        return {"name": "tool_call_accuracy", "score": 1.0}
    if not expected_tools:
        return {"name": "tool_call_accuracy", "score": 0.0}

    overlap = expected_tools & actual_tools
    score = len(overlap) / len(expected_tools)
    return {"name": "tool_call_accuracy", "score": score,
            "metadata": {"expected": sorted(expected_tools), "actual": sorted(actual_tools)}}


class ResponseFormatInput(BaseModel):
    output: str = Field(description="The agent's response text")


def response_format(output: str) -> dict:
    """Span-level scorer: is the response well-structured?

    Checks that the response is non-empty, within a reasonable length,
    and doesn't contain error artifacts or broken formatting.
    """
    if not output or not output.strip():
        return {"name": "response_format", "score": 0.0, "metadata": {"reason": "empty response"}}

    length = len(output.strip())

    if length < 10:
        return {"name": "response_format", "score": 0.2, "metadata": {"reason": "too short", "length": length}}
    if length > 5000:
        return {"name": "response_format", "score": 0.5, "metadata": {"reason": "very long", "length": length}}

    error_markers = ["traceback", "exception", "error:", "stacktrace"]
    has_errors = any(marker in output.lower() for marker in error_markers)
    if has_errors:
        return {"name": "response_format", "score": 0.3, "metadata": {"reason": "contains error artifacts"}}

    return {"name": "response_format", "score": 1.0, "metadata": {"length": length}}


project.scorers.create(handler=tool_call_accuracy, name="tool_call_accuracy", slug="tool-call-accuracy",
                       description="Span-level: did the agent call the expected tool(s)?",
                       parameters=ToolCallAccuracyInput, if_exists="replace")
project.scorers.create(handler=response_format, name="response_format", slug="response-format",
                       description="Span-level: is the response well-structured?",
                       parameters=ResponseFormatInput, if_exists="replace")

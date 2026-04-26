"""Mocked customer-support tools.

Every function returns deterministic data so the demo is reproducible
without real backends. ADK auto-wraps plain functions into FunctionTool
using the docstring as the description and type hints for the schema.
"""

import random

# ---------------------------------------------------------------------------
# Order tools
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


def _normalize_id(order_id: str) -> str:
    """Strip leading '#' or whitespace from an order ID."""
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
        return {
            "success": False,
            "message": f"Cannot cancel order {order_id} — status is '{order['status']}'. "
            "Only orders with status 'processing' can be cancelled.",
        }
    return {
        "success": True,
        "message": f"Order {order_id} has been cancelled. Reason: {reason}",
        "refund_initiated": True,
    }


# ---------------------------------------------------------------------------
# Billing tools
# ---------------------------------------------------------------------------


def process_refund(order_id: str, amount: float) -> dict:
    """Process a refund for an order. Returns a confirmation with a reference number."""
    order = MOCK_ORDERS.get(_normalize_id(order_id))
    if order is None:
        return {"error": f"Order {order_id} not found."}
    if amount > order["total"]:
        return {
            "success": False,
            "message": f"Refund amount ${amount:.2f} exceeds order total ${order['total']:.2f}.",
        }
    ref = f"REF-{random.randint(100000, 999999)}"
    return {
        "success": True,
        "reference_number": ref,
        "amount_refunded": amount,
        "message": f"Refund of ${amount:.2f} for order {order_id} processed. Reference: {ref}",
    }


def get_invoice(order_id: str) -> dict:
    """Retrieve the invoice for an order, including line items and a PDF link."""
    order_id = _normalize_id(order_id)
    order = MOCK_ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id} not found."}
    return {
        "order_id": order_id,
        "invoice_url": f"https://invoices.example.com/{order_id}.pdf",
        "line_items": [{"item": item, "qty": 1} for item in order["items"]],
        "total": order["total"],
    }


# ---------------------------------------------------------------------------
# FAQ tool
# ---------------------------------------------------------------------------

FAQ_ENTRIES = [
    {
        "question": "What is your return policy?",
        "answer": "You can return most items within 30 days of delivery for a full refund. "
        "Items must be in original condition with packaging.",
    },
    {
        "question": "How long does shipping take?",
        "answer": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 "
        "business days. Free shipping on orders over $50.",
    },
    {
        "question": "How do I track my order?",
        "answer": "You can track your order using the tracking URL provided in your shipping "
        "confirmation email, or ask us with your order ID.",
    },
    {
        "question": "Do you offer international shipping?",
        "answer": "Yes, we ship to over 50 countries. International shipping typically takes "
        "10-15 business days. Additional customs fees may apply.",
    },
    {
        "question": "How do I change my shipping address?",
        "answer": "You can change your shipping address before the order ships by contacting "
        "support with your order ID. Once shipped, the address cannot be changed.",
    },
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay.",
    },
]


def search_faq(query: str) -> dict:
    """Search the FAQ knowledge base. Returns the top 3 matching entries."""
    # Simple keyword overlap scoring for the mock
    query_words = set(query.lower().split())
    scored = []
    for entry in FAQ_ENTRIES:
        entry_words = set(entry["question"].lower().split()) | set(entry["answer"].lower().split())
        overlap = len(query_words & entry_words)
        scored.append((overlap, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return {"results": [entry for _, entry in scored[:3]]}

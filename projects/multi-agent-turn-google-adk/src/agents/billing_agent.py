"""Billing specialist agent — handles refunds, invoices, and payment questions."""

from google.adk.agents import Agent

from src.agents.config import get_model
from src.tools.mock_tools import get_invoice, process_refund

billing_agent = Agent(
    name="billing_agent",
    model=get_model(),
    description="Handles billing queries: refunds, invoices, payment issues, and charges.",
    instruction=(
        "You are the Billing Specialist for our customer support team.\n\n"
        "Your responsibilities:\n"
        "- Process refund requests\n"
        "- Retrieve invoices for orders\n"
        "- Answer questions about charges and payments\n\n"
        "Guidelines:\n"
        "- Confirm the order ID before processing any refund\n"
        "- Always provide the refund reference number to the customer\n"
        "- If the query shifts to order status, tracking, or general questions, "
        "let the router handle the transfer\n"
        "- Be concise and helpful\n"
    ),
    tools=[process_refund, get_invoice],
)

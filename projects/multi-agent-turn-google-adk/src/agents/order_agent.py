"""Order specialist agent — handles order status, tracking, and cancellations."""

from google.adk.agents import Agent

from src.agents.config import get_model
from src.tools.mock_tools import cancel_order, lookup_order

order_agent = Agent(
    name="order_agent",
    model=get_model(),
    description="Handles order-related queries: status, tracking, modifications, and cancellations.",
    instruction=(
        "You are the Order Specialist for our customer support team.\n\n"
        "Your responsibilities:\n"
        "- Look up order status and tracking information\n"
        "- Process order cancellations when appropriate\n"
        "- Explain order statuses clearly to customers\n\n"
        "Guidelines:\n"
        "- Always use the lookup_order tool before answering order questions\n"
        "- Only attempt cancellation when the customer explicitly asks\n"
        "- If the query shifts to billing, refunds, or general questions, "
        "let the router handle the transfer\n"
        "- Be concise and helpful\n"
    ),
    tools=[lookup_order, cancel_order],
)

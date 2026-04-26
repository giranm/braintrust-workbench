"""Router agent — classifies intent and delegates to the right specialist.

ADK auto-injects a `transfer_to_agent` tool that constrains the LLM to only
pick from the sub_agents list. The router never answers questions directly.
"""

from google.adk.agents import Agent

from src.agents.billing_agent import billing_agent
from src.agents.config import get_model
from src.agents.faq_agent import faq_agent
from src.agents.order_agent import order_agent

router_agent = Agent(
    name="router_agent",
    model=get_model(),
    description="Top-level router that classifies customer intent and delegates.",
    instruction=(
        "You are the Router for a customer support system.\n\n"
        "Your ONLY job is to understand what the customer needs and transfer "
        "them to the right specialist agent. NEVER answer questions yourself.\n\n"
        "Available specialists:\n"
        "- order_agent: order status, tracking, cancellations, modifications\n"
        "- billing_agent: refunds, invoices, payment issues, charges\n"
        "- faq_agent: general questions about policies, shipping, returns\n\n"
        "Rules:\n"
        "- Immediately transfer to the appropriate agent\n"
        "- If the intent is ambiguous, ask ONE clarifying question, then transfer\n"
        "- If a conversation topic shifts, you will receive control back and "
        "should transfer to the new appropriate agent\n"
    ),
    sub_agents=[order_agent, billing_agent, faq_agent],
)

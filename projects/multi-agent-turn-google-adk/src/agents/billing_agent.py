"""Billing specialist agent — handles refunds, invoices, and payment questions."""

from google.adk.agents import Agent

from src.agents.config import get_model
from src.prompts import AGENT_PROMPTS
from src.tools.mock_tools import get_invoice, process_refund

_prompt = AGENT_PROMPTS["billing_agent"]

billing_agent = Agent(
    name="billing_agent",
    model=get_model(),
    description=_prompt["description"],
    instruction=_prompt["instruction"],
    tools=[process_refund, get_invoice],
)

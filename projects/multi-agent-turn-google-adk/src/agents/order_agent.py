"""Order specialist agent — handles order status, tracking, and cancellations."""

from google.adk.agents import Agent

from src.agents.config import get_model
from src.prompts import AGENT_PROMPTS
from src.tools.mock_tools import cancel_order, lookup_order

_prompt = AGENT_PROMPTS["order_agent"]

order_agent = Agent(
    name="order_agent",
    model=get_model(),
    description=_prompt["description"],
    instruction=_prompt["instruction"],
    tools=[lookup_order, cancel_order],
)

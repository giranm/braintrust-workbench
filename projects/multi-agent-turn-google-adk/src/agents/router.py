"""Router agent — classifies intent and delegates to the right specialist.

ADK auto-injects a `transfer_to_agent` tool that constrains the LLM to only
pick from the sub_agents list. The router never answers questions directly.
"""

from google.adk.agents import Agent

from src.agents.billing_agent import billing_agent
from src.agents.config import get_model
from src.agents.faq_agent import faq_agent
from src.agents.order_agent import order_agent
from src.prompts import AGENT_PROMPTS

_prompt = AGENT_PROMPTS["router_agent"]

router_agent = Agent(
    name="router_agent",
    model=get_model(),
    description=_prompt["description"],
    instruction=_prompt["instruction"],
    sub_agents=[order_agent, billing_agent, faq_agent],
)

"""FAQ specialist agent — answers general product and policy questions."""

from google.adk.agents import Agent

from src.agents.config import get_model
from src.prompts import AGENT_PROMPTS
from src.tools.mock_tools import search_faq

_prompt = AGENT_PROMPTS["faq_agent"]

faq_agent = Agent(
    name="faq_agent",
    model=get_model(),
    description=_prompt["description"],
    instruction=_prompt["instruction"],
    tools=[search_faq],
)

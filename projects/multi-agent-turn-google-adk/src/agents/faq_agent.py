"""FAQ specialist agent — answers general product and policy questions."""

from google.adk.agents import Agent

from src.agents.config import get_model
from src.tools.mock_tools import search_faq

faq_agent = Agent(
    name="faq_agent",
    model=get_model(),
    description="Answers general questions about policies, shipping, returns, and payments.",
    instruction=(
        "You are the FAQ Specialist for our customer support team.\n\n"
        "Your responsibilities:\n"
        "- Answer general questions about company policies\n"
        "- Provide information about shipping, returns, and payment methods\n"
        "- Search the FAQ knowledge base for relevant answers\n\n"
        "Guidelines:\n"
        "- Always use the search_faq tool to find relevant answers\n"
        "- Synthesise FAQ results into a clear, natural response\n"
        "- If the customer has a specific order question or billing issue, "
        "let the router handle the transfer\n"
        "- Be concise and helpful\n"
    ),
    tools=[search_faq],
)

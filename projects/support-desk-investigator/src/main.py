"""
Support Desk Investigator - Main Application

This module implements an LLM-powered support desk agent with Braintrust logging
for full observability. It demonstrates how to track LLM interactions, monitor
performance, and enable debugging through comprehensive tracing.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Braintrust and OpenAI
# NOTE: Install dependencies first with: uv sync
try:
    import braintrust
    from openai import OpenAI
except ImportError:
    print("Error: Required packages not installed. Run: uv sync")
    exit(1)


class SupportAgent:
    """
    LLM-powered support desk agent with Braintrust observability.

    This agent processes customer support tickets and generates responses
    while logging all interactions to Braintrust for monitoring and analysis.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the support agent.

        Args:
            model: OpenAI model to use for generation
        """
        self.model = model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Initialize Braintrust logger
        self.logger = braintrust.init_logger(
            project="support-desk-investigator",
            api_key=os.environ.get("BRAINTRUST_API_KEY")
        )

    def generate_response(self, ticket: str, category: str = "general") -> Dict[str, Any]:
        """
        Generate a support response for the given ticket.

        Args:
            ticket: Customer support ticket text
            category: Category of the ticket (billing, technical, general)

        Returns:
            Dictionary with response and metadata
        """
        # Build prompt with support context
        system_prompt = self._build_system_prompt(category)

        # Start Braintrust span for logging
        with self.logger.span(
            name="support_response",
            input={"ticket": ticket, "category": category},
            metadata={"model": self.model}
        ) as span:
            try:
                # Call LLM
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": ticket}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                # Extract response text
                response_text = response.choices[0].message.content

                # Log output to Braintrust
                span.log(
                    output={"response": response_text},
                    metrics={
                        "tokens_used": response.usage.total_tokens,
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens
                    }
                )

                return {
                    "response": response_text,
                    "category": category,
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens
                }

            except Exception as e:
                # Log error to Braintrust
                span.log(error=str(e))
                raise

    def _build_system_prompt(self, category: str) -> str:
        """Build system prompt based on ticket category."""
        base_prompt = (
            "You are a helpful, professional, and empathetic customer support agent. "
            "Your goal is to resolve customer issues or escalate when necessary. "
        )

        category_guidance = {
            "billing": "Focus on payment issues, refunds, and account billing questions.",
            "technical": "Focus on troubleshooting technical problems and product usage.",
            "general": "Handle general inquiries with clear, friendly responses."
        }

        return base_prompt + category_guidance.get(category, category_guidance["general"])


def main():
    """Main entry point for the support agent demo."""
    print("🎯 Support Desk Investigator - Braintrust Demo\n")

    # Initialize agent
    agent = SupportAgent()

    # Example support tickets
    tickets = [
        {
            "text": "My payment failed but I was charged twice. Can you help?",
            "category": "billing"
        },
        {
            "text": "I can't log in to my account. I keep getting an error message.",
            "category": "technical"
        },
        {
            "text": "What are your business hours?",
            "category": "general"
        }
    ]

    # Process each ticket
    for i, ticket_data in enumerate(tickets, 1):
        print(f"\n📋 Ticket {i}: {ticket_data['text']}")
        print(f"Category: {ticket_data['category']}")

        # Generate response
        result = agent.generate_response(
            ticket=ticket_data['text'],
            category=ticket_data['category']
        )

        print(f"\n🤖 Agent Response:\n{result['response']}")
        print(f"\n📊 Tokens used: {result['tokens_used']}")
        print("-" * 80)

    print("\n✅ All tickets processed!")
    print("📈 View traces and metrics at: https://www.braintrust.dev/app")


if __name__ == "__main__":
    main()

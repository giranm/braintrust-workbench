#!/usr/bin/env python3
"""
Example: Using scorers for online evaluation during live agent interactions.

This shows how to integrate evaluation scorers into your production agent
to get real-time quality metrics for each interaction.

This pattern allows you to:
1. Monitor quality in production
2. Detect issues early
3. Compare different agent versions
4. Track quality over time
"""

import os
import uuid
from dotenv import load_dotenv
from braintrust import current_span

# Import agent and scorers
from multi_agent_chat_demo.agents.weather_agent import WeatherAgent
from evals.scorers import (
    helpfulness_check,
    weather_accuracy_check,
    tool_call_check,
    faithfulness_check,
)

load_dotenv()


async def evaluate_agent_response(
    user_message: str,
    agent_response: str,
    expected_data: dict,
    trace: any,
) -> dict:
    """
    Evaluate agent response using multiple scorers.

    Args:
        user_message: User's input
        agent_response: Agent's response
        expected_data: Expected response data (for validation)
        trace: Braintrust trace object

    Returns:
        Dict of scores by scorer name
    """
    scores = {}

    # Run helpfulness scorer
    helpfulness_result = await helpfulness_check(agent_response, user_message)
    scores["helpfulness"] = helpfulness_result["score"]

    # Run weather accuracy scorer (if city is known)
    if expected_data.get("city"):
        accuracy_result = await weather_accuracy_check(
            agent_response, expected_data, user_message
        )
        scores["accuracy"] = accuracy_result["score"]

    # Run tool call checker (if we expect tools)
    if expected_data.get("expected_tools"):
        tool_result = await tool_call_check(
            agent_response,
            expected_data,
            {"expected_tools": expected_data["expected_tools"]},
            trace,
        )
        if tool_result:
            scores["tool_accuracy"] = tool_result["score"]

    # Run faithfulness checker
    faithfulness_result = await faithfulness_check(
        agent_response, user_message, trace
    )
    if faithfulness_result:
        scores["faithfulness"] = faithfulness_result["score"]

    return scores


async def monitored_agent_interaction():
    """
    Example: Agent interaction with online evaluation.

    This pattern can be integrated into your production app
    to monitor quality in real-time.
    """
    # Create agent
    agent = WeatherAgent()
    conversation_id = str(uuid.uuid4())

    # User query
    user_message = "What's the weather in London?"

    # Expected data for validation (could come from test suite)
    expected = {
        "city": "London",
        "expected_tools": ["get_weather"],
    }

    # Get agent response
    response = await agent.respond(
        message=user_message,
        conversation_history=[],
        conversation_id=conversation_id,
    )

    print(f"User: {user_message}")
    print(f"Agent: {response}\n")

    # Get current span for trace access
    span = current_span()

    # Evaluate response
    if span:
        scores = await evaluate_agent_response(
            user_message=user_message,
            agent_response=response,
            expected_data=expected,
            trace=span,
        )

        # Log scores to Braintrust
        span.log(
            scores=scores,
            metadata={
                "online_eval": True,
                "conversation_id": conversation_id,
            },
        )

        print("📊 Quality Scores:")
        for scorer_name, score in scores.items():
            emoji = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
            print(f"  {emoji} {scorer_name}: {score:.2f}")

    # End conversation
    agent.end_conversation(conversation_id)


async def main():
    """Run the example."""
    print("=" * 60)
    print("Online Evaluation Example")
    print("=" * 60)
    print()

    await monitored_agent_interaction()

    print("\n" + "=" * 60)
    print("✅ Example complete!")
    print("\nScores are logged to Braintrust and can be viewed in:")
    print("https://www.braintrust.dev/app/multi-agent-chat-demo")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

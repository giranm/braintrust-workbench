#!/usr/bin/env python3
"""
Weather conversation evaluation using Braintrust.

This evaluation script tests the weather agent's ability to:
1. Provide accurate and helpful responses
2. Use proper formatting and structure
3. Respond appropriately to different query types

Note: The Python Braintrust SDK does not support querying span data in scorers
like the TypeScript SDK. Therefore, custom scorers that inspect tool calls or
span hierarchy cannot be used. We use LLM-as-a-judge scorers instead.

Run with: uv run python evals/weather_conversation.py
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

from braintrust import Eval, init_dataset

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import agent and scorers
from multi_agent_chat_demo.agents.weather_agent import WeatherAgent
from evals.scorers import (
    weather_accuracy_check,
    helpfulness_check,
    response_structure_check,
)

# Load environment
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "multi-agent-chat-demo")
DATASET_NAME = "WeatherConversationDataset"


async def task(input_data: dict, hooks: Any) -> str:
    """
    Task function: Get weather agent response for input.

    Args:
        input_data: Dict with "input" (user message) and optional "expected" data
        hooks: Braintrust hooks object

    Returns:
        Agent response string
    """
    # Create agent instance
    agent = WeatherAgent()

    # Get user message
    user_message = input_data if isinstance(input_data, str) else input_data.get("input", "")

    # Call agent
    response = await agent.respond(
        message=user_message,
        conversation_history=[],
        conversation_id=None,  # Single-turn eval
    )

    return response


# Scorer wrappers for Braintrust Eval
# Note: Python SDK scorers receive EvalScorerArgs with: input, output, expected, metadata
# They do NOT receive trace objects like TypeScript SDK

def weather_accuracy_scorer(output, expected, input, **kwargs):
    """Scorer wrapper for weather_accuracy_check."""
    input_text = input if isinstance(input, str) else input.get("input", "")
    # Run async scorer
    import asyncio
    return asyncio.run(weather_accuracy_check(output, expected, input_text))


def helpfulness_scorer(output, input, **kwargs):
    """Scorer wrapper for helpfulness_check."""
    input_text = input if isinstance(input, str) else input.get("input", "")
    import asyncio
    return asyncio.run(helpfulness_check(output, input_text))


def response_structure_scorer(output, **kwargs):
    """Scorer wrapper for response_structure_check."""
    import asyncio
    return asyncio.run(response_structure_check(output))


def main():
    """Run the weather conversation evaluation."""
    print("=" * 60)
    print("Weather Conversation Evaluation")
    print("=" * 60)
    print(f"Project: {PROJECT_NAME}")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    # Run evaluation
    Eval(
        PROJECT_NAME,
        experiment_name=f"weather-eval-{datetime.now().strftime('%Y-%m-%d')}",
        task=task,
        data=init_dataset(
            project=PROJECT_NAME,
            name=DATASET_NAME,
        ),
        scores=[
            weather_accuracy_scorer,
            helpfulness_scorer,
            response_structure_scorer,
            # Note: tool_call_scorer and faithfulness_scorer removed
            # Python SDK doesn't support span querying in scorers like TypeScript SDK
        ],
        metadata={
            "eval_type": "single_turn",
            "agent_version": "v1",
            "description": "Basic weather conversation evaluation with tool calling and LLM-as-a-judge scorers",
        },
    )

    print("\n✅ Evaluation complete!")
    print(f"View results at: https://www.braintrust.dev/app/{PROJECT_NAME}")


if __name__ == "__main__":
    main()

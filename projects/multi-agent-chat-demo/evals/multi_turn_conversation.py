#!/usr/bin/env python3
"""
Multi-turn conversation evaluation for weather chat.

Simulates realistic multi-turn conversations to evaluate:
1. Conversation coherence across turns
2. Context maintenance
3. Tool usage across multiple requests
4. User satisfaction

Similar to l8r's sim.eval.ts pattern.

Run with: uv run python evals/multi_turn_conversation.py
"""

import os
import asyncio
import uuid
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

from braintrust import Eval, init_dataset, traced

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import agent and scorers
from multi_agent_chat_demo.agents.weather_agent import WeatherAgent
from evals.scorers import (
    conversation_coherence_check,
)

# Load environment
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "multi-agent-chat-demo")
DATASET_NAME = "MultiTurnWeatherDataset"
MAX_TURNS = 5


async def run_multi_turn_conversation(
    seed_messages: list[dict],
    conversation_id: str = None,
) -> dict:
    """
    Run a multi-turn conversation with the weather agent.

    Args:
        seed_messages: Initial conversation messages to simulate
        conversation_id: Optional conversation ID for tracing

    Returns:
        Dict with messages, turn_count, and metadata
    """
    # Create agent instance
    agent = WeatherAgent()

    # Generate conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    conversation_history = []
    turn_count = 0

    # Process each seed message
    for i in range(0, len(seed_messages), 2):
        if i >= len(seed_messages):
            break

        turn_count += 1
        user_message_obj = seed_messages[i]
        user_message = user_message_obj["content"] if isinstance(user_message_obj, dict) else user_message_obj

        # Wrap turn in traced span
        @traced(name=f"turn_{turn_count}")
        async def process_turn():
            # Get agent response
            response = await agent.respond(
                message=user_message,
                conversation_history=conversation_history.copy(),
                conversation_id=conversation_id,
            )

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": response})

            return response

        await process_turn()

    # End conversation
    agent.end_conversation(conversation_id)

    return {
        "messages": conversation_history,
        "turn_count": turn_count,
        "conversation_id": conversation_id,
    }


async def task(input_data: dict, hooks: Any) -> str:
    """
    Task function: Run multi-turn conversation and return formatted output.

    Args:
        input_data: Dict with "messages" (seed conversation)
        hooks: Braintrust hooks object

    Returns:
        Formatted conversation string
    """
    seed_messages = input_data.get("messages", [])

    # Run conversation
    result = await run_multi_turn_conversation(seed_messages)

    # Format output
    conversation_text = "\n\n".join(
        [f"{msg['role'].upper()}: {msg['content']}" for msg in result["messages"]]
    )

    # Include metadata header
    header = f"[Turns: {result['turn_count']}, ID: {result['conversation_id']}]"

    return f"{header}\n\n{conversation_text}"


# Scorer wrappers for Braintrust Eval
# Note: Python SDK scorers receive EvalScorerArgs with: input, output, expected, metadata

def coherence_scorer(output, **kwargs):
    """Check conversation coherence across turns."""
    # Parse messages from output
    lines = output.split("\n\n")
    messages = []

    for line in lines:
        if line.startswith("[Turns:"):
            continue
        if ":" in line:
            role, content = line.split(":", 1)
            role = role.strip().lower()
            content = content.strip()
            if role in ["user", "assistant"]:
                messages.append({"role": role, "content": content})

    import asyncio
    return asyncio.run(conversation_coherence_check(messages))


def multi_turn_helpfulness_scorer(output, **kwargs):
    """
    Check if the agent was helpful across the conversation.

    Evaluates the overall helpfulness of the agent's responses
    in the multi-turn context.
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Evaluate if the weather assistant was helpful across this multi-turn conversation.

Conversation:
{output}

A helpful multi-turn conversation should:
- Address each user question appropriately
- Maintain context from previous turns
- Provide accurate weather information
- Not repeat information unnecessarily
- Be friendly and professional throughout

Answer with ONLY 'Y' for helpful or 'N' for unhelpful.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "MultiTurnHelpfulness",
        "score": score,
        "metadata": {
            "llm_answer": answer,
        },
    }


def context_maintenance_scorer(output, **kwargs):
    """
    Check if the agent maintains context across turns.

    Verifies that the agent doesn't lose track of the conversation
    and doesn't ask for information already provided.
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Evaluate if the weather assistant maintains context across turns in this conversation.

Conversation:
{output}

Good context maintenance means:
- The agent doesn't ask for information the user already provided
- Follow-up questions are answered with awareness of previous exchanges
- The agent doesn't repeat the same information unnecessarily
- References to earlier parts of the conversation are handled correctly

Answer with ONLY 'Y' for good context maintenance or 'N' for poor context maintenance.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "ContextMaintenance",
        "score": score,
        "metadata": {
            "llm_answer": answer,
        },
    }


def main():
    """Run the multi-turn conversation evaluation."""
    print("=" * 60)
    print("Multi-Turn Weather Conversation Evaluation")
    print("=" * 60)
    print(f"Project: {PROJECT_NAME}")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    # Run evaluation
    Eval(
        PROJECT_NAME,
        experiment_name=f"multi-turn-eval-{datetime.now().strftime('%Y-%m-%d')}",
        task=task,
        data=init_dataset(
            project=PROJECT_NAME,
            name=DATASET_NAME,
        ),
        scores=[
            coherence_scorer,
            multi_turn_helpfulness_scorer,
            context_maintenance_scorer,
        ],
        metadata={
            "eval_type": "multi_turn",
            "max_turns": MAX_TURNS,
            "agent_version": "v1",
            "description": "Multi-turn conversation evaluation with coherence and context tracking",
        },
    )

    print("\n✅ Evaluation complete!")
    print(f"View results at: https://www.braintrust.dev/app/{PROJECT_NAME}")


if __name__ == "__main__":
    main()

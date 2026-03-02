#!/usr/bin/env python3
"""Test script to mimic browser behavior and test multi-turn conversation tracing."""

import asyncio
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent
from multi_agent_chat_demo.agents.weather_agent import WeatherAgent


async def test_multi_turn_conversation():
    """Simulate a multi-turn conversation like the browser would."""
    print("=" * 60)
    print("Testing Multi-Turn Conversation Tracing")
    print("=" * 60)

    # Create agent instance
    agent = WeatherAgent()

    # Generate a conversation ID (like the UI does)
    conversation_id = str(uuid.uuid4())
    print(f"\n📝 Conversation ID: {conversation_id}")

    # Simulate conversation turns
    turns = [
        "What's the weather in London?",
        "How about Paris?",
        "And what about Tokyo?",
    ]

    conversation_history = []

    for i, user_message in enumerate(turns):
        print(f"\n{'=' * 60}")
        print(f"Turn {i}: {user_message}")
        print(f"{'=' * 60}")

        try:
            # Call agent (mimicking what the Reflex app does)
            response = await agent.respond(
                message=user_message,
                conversation_history=conversation_history.copy(),
                conversation_id=conversation_id,
            )

            print(f"\n🤖 Agent Response:\n{response}")

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": response})

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            break

    # End the conversation
    print(f"\n{'=' * 60}")
    print("Ending conversation...")
    agent.end_conversation(conversation_id)
    print("✅ Conversation ended and span flushed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(test_multi_turn_conversation())

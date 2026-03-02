#!/usr/bin/env python3
"""Quick test script to verify the weather agent works."""

import asyncio
import sys
import os

# Add the project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from multi_agent_chat_demo.agents.weather_agent import WeatherAgent


async def test_agent():
    """Test the weather agent with a simple query."""
    print("🧪 Testing WeatherAgent...")
    print("=" * 60)

    # Create agent
    agent = WeatherAgent()
    print(f"✅ Agent created: {agent.name}")

    # Test query
    query = "What is the weather in Cape Town?"
    print(f"\n📝 Query: {query}")
    print("-" * 60)

    try:
        # Get response
        response = await agent.respond(query)
        print(f"\n✅ Response received:")
        print(response)
        print("\n" + "=" * 60)
        print("✅ Test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error occurred:")
        print(f"   {type(e).__name__}: {e}")
        print("\n" + "=" * 60)
        print("❌ Test failed!")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)

"""Tests for main module."""

import pytest
from src.main import Agent, Orchestrator


def test_agent_creation():
    """Test agent initialization."""
    agent = Agent(
        name="TestAgent",
        role="Tester",
        system_prompt="You are a test agent."
    )

    assert agent.name == "TestAgent"
    assert agent.role == "Tester"
    assert "test" in agent.system_prompt.lower()


def test_orchestrator_agent_registration():
    """Test agent registration with orchestrator."""
    orchestrator = Orchestrator()
    agent = Agent(
        name="TestAgent",
        role="Tester",
        system_prompt="You are a test agent."
    )

    orchestrator.register_agent(agent)

    assert "TestAgent" in orchestrator.agents
    assert orchestrator.agents["TestAgent"] == agent


def test_orchestrator_invalid_agent():
    """Test routing to non-existent agent raises error."""
    orchestrator = Orchestrator()

    with pytest.raises(ValueError, match="Agent .* not found"):
        orchestrator.route_message("test message", "NonExistentAgent")


def test_conversation_history_tracking():
    """Test that orchestrator tracks conversation history."""
    orchestrator = Orchestrator()

    # Initially empty
    assert len(orchestrator.conversation_history) == 0

    # Note: Full integration test would require API keys
    # This is a structure test only

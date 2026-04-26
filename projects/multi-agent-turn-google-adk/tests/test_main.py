"""Smoke test that imports resolve without errors."""

from src.agents import router_agent
from src.tools import lookup_order


def test_router_agent_exists():
    assert router_agent.name == "router_agent"
    assert len(router_agent.sub_agents) == 3


def test_tools_importable():
    result = lookup_order("12345")
    assert result["order_id"] == "12345"

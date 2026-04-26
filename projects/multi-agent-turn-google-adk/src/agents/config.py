"""Shared model configuration for all agents."""

from google.adk.models.lite_llm import LiteLlm

from src.prompts import DEFAULT_MODEL


def get_model() -> LiteLlm:
    """Return a LiteLlm instance configured from environment variables."""
    return LiteLlm(model=DEFAULT_MODEL)

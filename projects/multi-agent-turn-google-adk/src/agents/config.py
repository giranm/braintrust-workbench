"""Shared model configuration for all agents."""

import os

from google.adk.models.lite_llm import LiteLlm

DEFAULT_MODEL = "anthropic/claude-haiku-4-5-20251001"


def get_model() -> LiteLlm:
    """Return a LiteLlm instance configured from environment variables."""
    model_string = os.environ.get("ADK_MODEL", DEFAULT_MODEL)
    return LiteLlm(model=model_string)

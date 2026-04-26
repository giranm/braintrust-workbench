"""Braintrust tracing integration for LiteLLM calls.

Registers a LiteLLM callback that creates Braintrust `llm` type spans
for every model call ADK makes, capturing tokens, cost, and latency.
"""

import braintrust
import litellm
from litellm.integrations.custom_logger import CustomLogger


class BraintrustLLMCallback(CustomLogger):
    """LiteLLM callback that logs each LLM call as a Braintrust span."""

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        span = braintrust.current_span()
        if span is None:
            return

        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])

        # Extract response content
        output = None
        try:
            if hasattr(response_obj, "choices") and response_obj.choices:
                choice = response_obj.choices[0]
                if hasattr(choice, "message"):
                    output = choice.message.model_dump()
        except Exception:
            pass

        # Extract token usage
        metrics = {}
        usage = getattr(response_obj, "usage", None)
        if usage:
            prompt_tokens = getattr(usage, "prompt_tokens", None)
            completion_tokens = getattr(usage, "completion_tokens", None)
            total_tokens = getattr(usage, "total_tokens", None)
            if prompt_tokens is not None:
                metrics["prompt_tokens"] = prompt_tokens
            if completion_tokens is not None:
                metrics["completion_tokens"] = completion_tokens
            if total_tokens is not None:
                metrics["tokens"] = total_tokens

        # Duration
        if start_time and end_time:
            duration_s = (end_time - start_time).total_seconds()
            metrics["duration"] = duration_s

        # Cost (LiteLLM calculates this for us)
        response_cost = kwargs.get("response_cost", None)
        if response_cost is not None:
            metrics["cost"] = response_cost

        # Create the LLM span
        with span.start_span(name=model, type="llm") as llm_span:
            llm_span.log(
                input=messages,
                output=output,
                metrics=metrics,
                metadata={"model": model},
            )


_initialized = False


def init_tracing():
    """Register the Braintrust LLM callback with LiteLLM. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return
    _initialized = True
    litellm.callbacks = litellm.callbacks or []
    litellm.callbacks.append(BraintrustLLMCallback())

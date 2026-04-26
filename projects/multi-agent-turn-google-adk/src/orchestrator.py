"""Turn-based multi-agent orchestrator with Braintrust tracing.

Wraps ADK's Runner/Session API and logs each conversation turn,
agent delegation, and tool call as nested Braintrust spans.

LLM calls are traced automatically via the LiteLLM callback in
src/tracing.py — that callback creates `llm` type spans with
token counts, cost, and latency under the currently-active span.
"""

import os

import braintrust
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.agents.router import router_agent
from src.tracing import init_tracing

# Register LiteLLM callback before any ADK calls
init_tracing()

BRAINTRUST_PROJECT = os.environ.get("BRAINTRUST_PROJECT", "multi-agent-turn-google-adk")

_session_service = InMemorySessionService()
_runner = Runner(
    app_name=BRAINTRUST_PROJECT,
    agent=router_agent,
    session_service=_session_service,
)


async def create_session(user_id: str = "cli-user") -> str:
    """Create a new ADK session and return its ID."""
    session = await _session_service.create_session(
        app_name=BRAINTRUST_PROJECT,
        user_id=user_id,
    )
    return session.id


async def send_message(
    session_id: str,
    message: str,
    *,
    user_id: str = "cli-user",
    conversation_span: braintrust.Span | None = None,
    verbose: bool = False,
) -> str:
    """Send a user message and return the final agent response text.

    If *conversation_span* is provided, each agent turn, tool call, and
    LLM invocation is logged as a nested child span. LLM spans are created
    automatically by the LiteLLM callback under the active turn span.
    """
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=message)],
    )

    final_response = ""
    current_agent: str | None = None
    turn_span: braintrust.Span | None = None
    # Track pending tool call so we can pair it with its response
    pending_tool_name: str | None = None
    pending_tool_span: braintrust.Span | None = None

    async for event in _runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content,
    ):
        # Track agent transfers
        author = getattr(event, "author", None)
        if author and author != current_agent:
            # Close pending tool span if any
            if pending_tool_span is not None:
                pending_tool_span.__exit__(None, None, None)
                pending_tool_span = None
                pending_tool_name = None
            # Close previous turn span with its output
            if turn_span is not None:
                turn_span.__exit__(None, None, None)
            current_agent = author
            if verbose:
                print(f"  [{current_agent}]")
            # Open a new turn span — LLM callback will nest llm spans here
            if conversation_span is not None:
                turn_span = conversation_span.start_span(
                    name=f"turn:{current_agent}",
                    type="task",
                )
                turn_span.__enter__()
                turn_span.log(input=message)

        # Process event parts
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Tool call — open a tool span
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    if verbose:
                        print(f"    -> tool: {fc.name}({fc.args})")
                    # Close any previous unclosed tool span
                    if pending_tool_span is not None:
                        pending_tool_span.__exit__(None, None, None)
                    if turn_span is not None:
                        pending_tool_span = turn_span.start_span(
                            name=f"tool:{fc.name}",
                            type="tool",
                        )
                        pending_tool_span.__enter__()
                        pending_tool_span.log(
                            input=dict(fc.args) if fc.args else {},
                        )
                        pending_tool_name = fc.name

                # Tool response — close the tool span with output
                if hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    if verbose:
                        print(f"    <- {fr.name}: {fr.response}")
                    if pending_tool_span is not None:
                        response_data = fr.response
                        if hasattr(response_data, "model_dump"):
                            response_data = response_data.model_dump()
                        pending_tool_span.log(output=response_data)
                        pending_tool_span.__exit__(None, None, None)
                        pending_tool_span = None
                        pending_tool_name = None

                # Text response
                if hasattr(part, "text") and part.text:
                    final_response = part.text

    # Close any remaining open spans
    if pending_tool_span is not None:
        pending_tool_span.__exit__(None, None, None)
    if turn_span is not None:
        if final_response:
            turn_span.log(output=final_response)
        turn_span.__exit__(None, None, None)

    return final_response

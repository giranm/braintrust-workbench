"""Custom Braintrust scorers for the multi-agent customer support demo.

Each scorer follows the Braintrust convention:
    (output, expected, **kwargs) -> Score

Scorers are organized by level:
- Span-level: score a single agent turn (tool accuracy, response format)
- Trace-level: score the full conversation (resolution quality)

And by type:
- Code-based: deterministic logic, uploaded via `braintrust push`
- LLM-as-Judge: prompt-based, registered via `project.scorers.create()`
"""

from pydantic import BaseModel, Field

from braintrust import Score


# ---------------------------------------------------------------------------
# Eval scorers (used by src/eval.py, not managed objects)
# ---------------------------------------------------------------------------


def routing_accuracy(output: str, expected: dict, **kwargs) -> Score:
    """Check whether the correct specialist agent handled the query."""
    expected_agent = expected.get("agent", "")
    actual_agent = kwargs.get("metadata", {}).get("agent", "")
    match = 1.0 if actual_agent == expected_agent else 0.0
    return Score(
        name="routing_accuracy",
        score=match,
        metadata={"expected": expected_agent, "actual": actual_agent},
    )


def tool_selection(output: str, expected: dict, **kwargs) -> Score:
    """Check whether the agent called the correct tool(s)."""
    expected_tools = set(expected.get("tools", []))
    actual_tools = set(kwargs.get("metadata", {}).get("tools_called", []))

    if not expected_tools:
        return Score(name="tool_selection", score=1.0 if not actual_tools else 0.0)

    overlap = expected_tools & actual_tools
    score = len(overlap) / len(expected_tools) if expected_tools else 0.0
    return Score(
        name="tool_selection",
        score=score,
        metadata={"expected": sorted(expected_tools), "actual": sorted(actual_tools)},
    )


def task_completion(output: str, expected: dict, **kwargs) -> Score:
    """Check whether key information from the expected answer appears in the output."""
    must_contain = expected.get("must_contain", [])
    if not must_contain:
        return Score(name="task_completion", score=1.0)

    output_lower = output.lower()
    hits = sum(1 for term in must_contain if term.lower() in output_lower)
    score = hits / len(must_contain)
    return Score(
        name="task_completion",
        score=score,
        metadata={"must_contain": must_contain, "hits": hits, "total": len(must_contain)},
    )


# ---------------------------------------------------------------------------
# Span-level code scorers (managed objects via braintrust push)
# ---------------------------------------------------------------------------


class ToolCallAccuracyInput(BaseModel):
    output: str = Field(description="The agent's response text")
    expected: str = Field(description="JSON string of expected tool names")
    metadata: str = Field(description="JSON string with tools_called list")


def tool_call_accuracy(output: str, expected: str, metadata: str = "{}") -> Score:
    """Span-level scorer: did the agent call the expected tool(s)?

    Compares the set of tools the agent actually called against the
    expected set. Returns 1.0 for exact match, partial credit for
    subset matches, 0.0 for complete mismatch.
    """
    import json

    try:
        expected_tools = set(json.loads(expected)) if expected else set()
    except (json.JSONDecodeError, TypeError):
        expected_tools = set()

    try:
        meta = json.loads(metadata) if metadata else {}
        actual_tools = set(meta.get("tools_called", []))
    except (json.JSONDecodeError, TypeError):
        actual_tools = set()

    if not expected_tools and not actual_tools:
        return Score(name="tool_call_accuracy", score=1.0)
    if not expected_tools:
        return Score(name="tool_call_accuracy", score=0.0)

    overlap = expected_tools & actual_tools
    score = len(overlap) / len(expected_tools)
    return Score(
        name="tool_call_accuracy",
        score=score,
        metadata={"expected": sorted(expected_tools), "actual": sorted(actual_tools)},
    )


class ResponseFormatInput(BaseModel):
    output: str = Field(description="The agent's response text")


def response_format(output: str) -> Score:
    """Span-level scorer: is the response well-structured?

    Checks that the response is non-empty, within a reasonable length,
    and doesn't contain error artifacts or broken formatting.
    """
    if not output or not output.strip():
        return Score(name="response_format", score=0.0, metadata={"reason": "empty response"})

    length = len(output.strip())

    # Too short to be useful
    if length < 10:
        return Score(name="response_format", score=0.2, metadata={"reason": "too short", "length": length})

    # Unreasonably long (likely a loop or dump)
    if length > 5000:
        return Score(name="response_format", score=0.5, metadata={"reason": "very long", "length": length})

    # Check for common error artifacts
    error_markers = ["traceback", "exception", "error:", "stacktrace"]
    has_errors = any(marker in output.lower() for marker in error_markers)
    if has_errors:
        return Score(name="response_format", score=0.3, metadata={"reason": "contains error artifacts"})

    return Score(name="response_format", score=1.0, metadata={"length": length})


# ---------------------------------------------------------------------------
# LLM-as-Judge scorer configs (managed objects via project.scorers.create)
# ---------------------------------------------------------------------------

RESPONSE_HELPFULNESS_PROMPT = """\
You are evaluating a single turn of a customer support conversation.

Customer message: {{input}}
Agent response: {{output}}

Is the agent's response helpful? Consider:
- Does it directly address the customer's question or request?
- Does it provide actionable information (order status, next steps, etc.)?
- Is the tone professional and empathetic?
- Does it avoid unnecessary filler or off-topic content?

Answer "Yes" if the response is helpful, "No" if it is not.
"""

CONVERSATION_RESOLUTION_PROMPT = """\
You are evaluating a full multi-turn customer support conversation.

Full conversation:
{{input}}

Final agent response:
{{output}}

Was the customer's issue fully resolved by the end of this conversation? Consider:
- Did the customer get a clear answer to their original question?
- Were all follow-up questions addressed?
- If a topic shift occurred, was each topic handled before moving on?
- Would the customer reasonably feel their issue is resolved?

Answer "Yes" if the issue was resolved, "No" if it was not.
"""

LLM_SCORER_CONFIGS = [
    {
        "name": "response_helpfulness",
        "slug": "response-helpfulness",
        "description": "Span-level LLM scorer: is the agent's response helpful and actionable?",
        "prompt": RESPONSE_HELPFULNESS_PROMPT,
        "model": "gpt-4o-mini",
        "use_cot": True,
        "choice_scores": {"Yes": 1.0, "No": 0.0},
    },
    {
        "name": "conversation_resolution",
        "slug": "conversation-resolution",
        "description": "Trace-level LLM scorer: was the customer's issue fully resolved?",
        "prompt": CONVERSATION_RESOLUTION_PROMPT,
        "model": "gpt-4o-mini",
        "use_cot": True,
        "choice_scores": {"Yes": 1.0, "No": 0.0},
    },
]

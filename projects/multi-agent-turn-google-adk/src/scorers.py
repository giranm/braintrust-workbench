"""Custom Braintrust scorers for the multi-agent customer support demo.

Each scorer follows the Braintrust convention:
    (output, expected, **kwargs) -> Score

Heuristic scorers return deterministic scores. LLM-graded scorers are
defined as prompt-based scorers and registered via `braintrust push`.
"""

from braintrust import Score


# ---------------------------------------------------------------------------
# Heuristic scorers
# ---------------------------------------------------------------------------


def routing_accuracy(output: str, expected: dict, **kwargs) -> Score:
    """Check whether the correct specialist agent handled the query.

    Expects `expected` to contain:
        {"agent": "order_agent" | "billing_agent" | "faq_agent"}
    and `kwargs["metadata"]` to contain:
        {"agent": "<agent that actually handled>"}
    """
    expected_agent = expected.get("agent", "")
    actual_agent = kwargs.get("metadata", {}).get("agent", "")
    match = 1.0 if actual_agent == expected_agent else 0.0
    return Score(
        name="routing_accuracy",
        score=match,
        metadata={"expected": expected_agent, "actual": actual_agent},
    )


def tool_selection(output: str, expected: dict, **kwargs) -> Score:
    """Check whether the agent called the correct tool(s).

    Expects `expected` to contain:
        {"tools": ["lookup_order", ...]}
    and `kwargs["metadata"]` to contain:
        {"tools_called": ["lookup_order", ...]}
    """
    expected_tools = set(expected.get("tools", []))
    actual_tools = set(kwargs.get("metadata", {}).get("tools_called", []))

    if not expected_tools:
        # No tool expected — score 1 if none were called
        return Score(
            name="tool_selection",
            score=1.0 if not actual_tools else 0.0,
        )

    overlap = expected_tools & actual_tools
    score = len(overlap) / len(expected_tools) if expected_tools else 0.0
    return Score(
        name="tool_selection",
        score=score,
        metadata={"expected": sorted(expected_tools), "actual": sorted(actual_tools)},
    )


def task_completion(output: str, expected: dict, **kwargs) -> Score:
    """Check whether key information from the expected answer appears in the output.

    Expects `expected` to contain:
        {"must_contain": ["tracking", "12345", ...]}
    """
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
# LLM-graded scorer definitions (for braintrust push / automations)
# ---------------------------------------------------------------------------

RESPONSE_RELEVANCE_PROMPT = """\
You are evaluating a customer support agent's response.

Customer question: {{input}}
Agent response: {{output}}

Is the agent's response relevant and helpful for the customer's question?
Consider:
- Does it address what the customer asked?
- Is the information accurate and useful?
- Is the tone appropriate for customer support?

Answer "Yes" if the response is relevant and helpful, "No" if it is not.
"""

CONVERSATION_COHERENCE_PROMPT = """\
You are evaluating a multi-turn customer support conversation.

Conversation:
{{input}}

Agent's latest response:
{{output}}

Is the agent's response coherent within the context of the full conversation?
Consider:
- Does it maintain context from previous turns?
- Does it avoid contradicting earlier statements?
- Does it handle topic shifts gracefully?

Answer "Yes" if the response is coherent, "No" if it is not.
"""

# These are used by src/automations.py to register LLM scorers
LLM_SCORER_CONFIGS = [
    {
        "name": "response_relevance",
        "prompt": RESPONSE_RELEVANCE_PROMPT,
        "model": "gpt-4o-mini",
        "use_cot": True,
        "choice_scores": {"Yes": 1.0, "No": 0.0},
    },
    {
        "name": "conversation_coherence",
        "prompt": CONVERSATION_COHERENCE_PROMPT,
        "model": "gpt-4o-mini",
        "use_cot": True,
        "choice_scores": {"Yes": 1.0, "No": 0.0},
    },
]

"""Reusable scorer functions for weather chat evaluations.

IMPORTANT: Python SDK Limitation
================================
The Braintrust Python SDK does not currently support querying span data within
scorers like the TypeScript SDK does. Scorers that require trace/span access
(tool_call_check, faithfulness_check) are defined here for reference but cannot
be used in Eval() calls.

Working Scorers (used in evaluations):
- weather_accuracy_check
- helpfulness_check
- response_structure_check
- conversation_coherence_check

Reference Only (require span access - not usable in Python Eval):
- tool_call_check
- faithfulness_check
"""

import os
from typing import Any, Optional
from anthropic import Anthropic


# Initialize Anthropic client for LLM-as-a-judge scorers
_anthropic_client = None


def _get_anthropic_client():
    """Get or create Anthropic client for scorers."""
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _anthropic_client


async def tool_call_check(output: str, expected: dict, metadata: dict, trace: Any) -> Optional[dict]:
    """
    Check if expected tools were called during execution.

    Queries span hierarchy to verify tool usage.
    Similar to l8r's toolCallCheck scorer.

    Args:
        output: Agent response text
        expected: Expected data including expected tools list
        metadata: Test case metadata
        trace: Braintrust trace object with getSpans() method

    Returns:
        Score dict with score (0-1), name, and metadata
    """
    expected_tools = metadata.get("expected_tools", []) or expected.get("tools", [])
    if not expected_tools:
        return None

    # Query trace for tool-type spans
    tool_spans = await trace.getSpans(span_type=["tool"])

    # Extract actual tool names from spans
    actual_tool_set = set()
    for span in tool_spans:
        # Check both span_attributes.name and metadata.tool_name
        tool_name = (
            span.get("span_attributes", {}).get("name")
            or span.get("metadata", {}).get("tool_name")
        )
        if tool_name:
            actual_tool_set.add(tool_name)

    expected_tool_set = set(expected_tools)
    expected_array = list(expected_tool_set)
    actual_array = list(actual_tool_set)

    # Calculate overlap
    overlap = len([tool for tool in expected_array if tool in actual_tool_set])
    score = overlap / len(expected_tool_set) if expected_tool_set else 1.0

    return {
        "name": "ToolCallCheck",
        "score": score,
        "metadata": {
            "expected_tools": expected_array,
            "actual_tools": actual_array,
            "overlap": overlap,
            "total_expected": len(expected_tool_set),
            "total_actual": len(actual_tool_set),
            "missing_tools": [t for t in expected_array if t not in actual_tool_set],
            "unexpected_tools": [t for t in actual_array if t not in expected_tool_set],
        },
    }


async def weather_accuracy_check(output: str, expected: dict, input_text: str) -> dict:
    """
    LLM-as-a-judge scorer: Check if weather response is accurate and complete.

    Args:
        output: Agent response text
        expected: Expected data including city and required content
        input_text: User's query

    Returns:
        Score dict with score (0-1), name, and metadata
    """
    client = _get_anthropic_client()

    expected_city = expected.get("city", "")
    expected_contains = expected.get("contains", [])

    prompt = f"""Evaluate if this weather response is accurate and complete.

User query: {input_text}
Agent response: {output}

Criteria:
1. Does the response mention the correct city ({expected_city if expected_city else 'the requested city'})?
2. Does it include relevant weather information (temperature, conditions, etc.)?
3. Is the response formatted clearly and professionally?
4. Does it address the user's specific question?

Answer with ONLY 'Y' for yes (accurate and complete) or 'N' for no (inaccurate or incomplete).
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "WeatherAccuracyCheck",
        "score": score,
        "metadata": {
            "llm_answer": answer,
            "expected_city": expected_city,
            "expected_contains": expected_contains,
        },
    }


async def helpfulness_check(output: str, input_text: str) -> dict:
    """
    LLM-as-a-judge scorer: Check if response is helpful and user-friendly.

    Args:
        output: Agent response text
        input_text: User's query

    Returns:
        Score dict with score (0-1), name, and metadata
    """
    client = _get_anthropic_client()

    prompt = f"""Rate whether this weather assistant response is helpful and user-friendly.

User query: {input_text}
Assistant response: {output}

A helpful response should:
- Directly address the user's question
- Provide actionable weather information
- Be friendly and conversational in tone
- Include context about what the weather means (e.g., "It's quite cold" or "Perfect for outdoor activities")
- Not leave the user with unanswered questions

Answer with ONLY 'Y' for yes (helpful) or 'N' for no (unhelpful).
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "HelpfulnessCheck",
        "score": score,
        "metadata": {
            "llm_answer": answer,
        },
    }


async def response_structure_check(output: str) -> dict:
    """
    LLM-as-a-judge scorer: Check if response has good structure and formatting.

    Args:
        output: Agent response text

    Returns:
        Score dict with score (0-1), name, and metadata
    """
    client = _get_anthropic_client()

    prompt = f"""Does this weather response have good structure and formatting?

Response to evaluate:
{output}

A well-structured weather response should:
- Be clear and easy to read
- Use emojis appropriately (e.g., 🌤️ for weather)
- Organize information logically (city, condition, temperature, etc.)
- Include relevant weather details
- Be professional yet friendly in tone

Answer with ONLY 'Y' for yes (well-structured) or 'N' for no (poorly structured).
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "ResponseStructureCheck",
        "score": score,
        "metadata": {
            "llm_answer": answer,
            "has_emoji": "🌤️" in output or "☀️" in output or "🌧️" in output,
        },
    }


async def faithfulness_check(output: str, input_text: str, trace: Any) -> Optional[dict]:
    """
    Check if response is grounded in tool results (faithfulness).

    Queries tool spans to extract results, then verifies agent response
    doesn't hallucinate facts not present in tool outputs.

    Args:
        output: Agent response text
        input_text: User's query
        trace: Braintrust trace object with getSpans() method

    Returns:
        Score dict with score (0-1), name, and metadata
    """
    # Get tool spans from trace
    tool_spans = await trace.getSpans(span_type=["tool"])

    if not tool_spans:
        # No tools called, can't check faithfulness
        return None

    # Extract tool results as context
    context_parts = []
    for span in tool_spans:
        tool_name = (
            span.get("span_attributes", {}).get("name")
            or span.get("metadata", {}).get("tool_name", "Tool")
        )
        tool_output = span.get("output", {})

        if tool_output:
            context_parts.append(
                f"Tool: {tool_name}\nResult: {tool_output}"
            )

    if not context_parts:
        return None

    context = "\n\n".join(context_parts)

    # Use LLM to check faithfulness
    client = _get_anthropic_client()

    prompt = f"""Check if the assistant's response is faithful to the tool results (no hallucination).

User query: {input_text}

Tool results (ground truth):
{context}

Assistant response to verify:
{output}

Is the assistant's response grounded in the tool results? Check:
1. Are weather values (temperature, wind, humidity) consistent with tool data?
2. Is the city/location correct?
3. Are weather conditions accurately described based on the tool output?
4. Does the response avoid making up facts not in the tool results?

Answer with ONLY 'Y' if the response is faithful to the tool results, or 'N' if it contains hallucinated information.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "FaithfulnessCheck",
        "score": score,
        "metadata": {
            "llm_answer": answer,
            "tool_count": len(tool_spans),
            "has_context": len(context_parts) > 0,
        },
    }


async def conversation_coherence_check(messages: list[dict]) -> dict:
    """
    LLM-as-a-judge scorer: Check multi-turn conversation coherence.

    For multi-turn conversations, verifies the agent maintains context
    and responds coherently across turns.

    Args:
        messages: List of conversation messages with role and content

    Returns:
        Score dict with score (0-1), name, and metadata
    """
    if len(messages) <= 2:
        # Single turn, coherence is automatic
        return {
            "name": "ConversationCoherenceCheck",
            "score": 1,
            "metadata": {"turn_count": len(messages) // 2, "reason": "single_turn"},
        }

    client = _get_anthropic_client()

    # Format conversation
    conversation_text = "\n\n".join(
        [f"{msg['role'].upper()}: {msg['content']}" for msg in messages]
    )

    prompt = f"""Evaluate if this multi-turn conversation is coherent and well-handled.

Conversation:
{conversation_text}

A coherent conversation should:
- Maintain context across turns
- Refer back to previous exchanges when relevant
- Not repeat the same information unnecessarily
- Flow naturally from turn to turn
- Address follow-up questions appropriately

Answer with ONLY 'Y' for coherent or 'N' for incoherent.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = response.content[0].text.strip().upper()
    score = 1 if answer == "Y" else 0

    return {
        "name": "ConversationCoherenceCheck",
        "score": score,
        "metadata": {
            "llm_answer": answer,
            "turn_count": len(messages) // 2,
        },
    }

# Python SDK Notes for Braintrust Evaluations

## Overview

This evaluation system was designed following patterns from the [l8r TypeScript app](https://github.com/braintrustdata/l8r), but adapted for the Python Braintrust SDK. However, there are important differences between the TypeScript and Python SDKs that affect what's possible in evaluations.

## Key Difference: Span Querying in Scorers

### TypeScript SDK
In TypeScript, scorers can query span data during evaluation:

```typescript
async function toolCallCheck({ expected, metadata, trace }: any) {
  const toolSpans = await trace.getSpans({ spanType: ["tool"] });
  // Inspect tool spans and validate...
}
```

This allows custom scorers to:
- Verify which tools were called
- Check tool inputs and outputs
- Validate span metadata
- Ensure response faithfulness to tool results

### Python SDK
In Python, scorers **only** receive `EvalScorerArgs` which contains:
- `input`: The test input
- `output`: The agent's output
- `expected`: Expected output (if provided)
- `metadata`: Test case metadata

**There is no `trace` parameter** in Python scorers. The scorer signature is:

```python
def my_scorer(input, output, expected, metadata, **kwargs):
    # Can only work with input/output, no span access
    pass
```

## Impact on Evaluation Strategy

### What We Can't Do (from l8r)
- ❌ `toolCallCheck` scorer - requires `trace.getSpans(span_type=["tool"])`
- ❌ `faithfulnessCheck` scorer - requires extracting tool outputs from spans
- ❌ Any custom scorer that inspects span hierarchy

### What We Can Do
- ✅ LLM-as-a-judge scorers that work with input/output
- ✅ `weather_accuracy_check` - validates response has correct weather info
- ✅ `helpfulness_check` - evaluates user-friendliness
- ✅ `response_structure_check` - checks formatting
- ✅ `conversation_coherence_check` - multi-turn flow quality

## Implemented Scorers

### Active Scorers (Used in Evaluations)

1. **weather_accuracy_check** (LLM-as-a-judge)
   - Validates correct city and weather information
   - Uses Claude Haiku for binary Y/N judgment
   - Works with input/output only

2. **helpfulness_check** (LLM-as-a-judge)
   - Evaluates user-friendliness and completeness
   - Checks if response addresses user's question
   - Works with input/output only

3. **response_structure_check** (LLM-as-a-judge)
   - Checks formatting and presentation
   - Validates use of emojis and organization
   - Works with output only

4. **conversation_coherence_check** (LLM-as-a-judge)
   - Multi-turn conversation flow evaluation
   - Parses conversation from formatted output
   - Works with output only

### Reference Scorers (Not Usable in Python Eval)

These scorers are defined in `scorers.py` but **cannot be used** in `Eval()` calls because they require span access:

1. **tool_call_check** - Requires `trace.getSpans(span_type=["tool"])`
2. **faithfulness_check** - Requires extracting tool outputs from spans

These remain in the code as documentation of the TypeScript patterns and for potential future use if the Python SDK adds span querying support.

## Workarounds

### Option 1: LLM-as-a-Judge (Current Approach)
Use Claude to evaluate outputs based on expected behavior:

```python
def tool_usage_check_via_llm(output, expected, **kwargs):
    """Ask LLM if the response appears to use weather data."""
    prompt = f"""Does this response appear to use actual weather tool data?

    Response: {output}
    Expected city: {expected.get('city')}

    Answer Y or N."""

    # Call Claude for judgment
    response = client.messages.create(...)
    return {"name": "ToolUsage", "score": 1 if "Y" else 0}
```

### Option 2: Metadata Passing
Pass span information through task metadata:

```python
async def task(input_data, hooks):
    # Run agent
    response = await agent.respond(...)

    # Add span info to metadata
    hooks.metadata["tools_called"] = ["get_weather"]

    return response

def scorer(output, metadata, **kwargs):
    # Access span info from metadata
    tools_called = metadata.get("tools_called", [])
    # Validate...
```

### Option 3: Online Evaluation
Use scorers during agent execution where spans are directly accessible:

```python
from evals.scorers import helpfulness_check

async def monitored_interaction():
    response = await agent.respond(message)

    # Run scorers with access to current span
    span = current_span()

    # Can access span data here
    scores = await evaluate_response(response, span)
    span.log(scores=scores)
```

## Evaluation Workflow

### Setup (One-time)
```bash
uv run python evals/setup_evals.py
```

Creates two datasets:
- `WeatherConversationDataset`: 10 single-turn test cases
- `MultiTurnWeatherDataset`: 6 multi-turn scenarios

### Run Evaluations
```bash
# All evaluations
uv run python evals/run_all_evals.py

# Single-turn only
uv run python evals/weather_conversation.py

# Multi-turn only
uv run python evals/multi_turn_conversation.py
```

## Results Interpretation

### Current Metrics (Without Span-Based Scorers)

**Strengths:**
- Subjective quality metrics (helpfulness, structure)
- Response accuracy for expected content
- Conversation flow quality

**Limitations:**
- Cannot verify exact tool usage programmatically
- Cannot check faithfulness to tool outputs directly
- Must rely on LLM judgment for technical validation

### Comparison to TypeScript l8r App

| Capability | TypeScript (l8r) | Python (This Project) |
|-----------|-----------------|----------------------|
| LLM-as-a-judge scorers | ✅ | ✅ |
| Custom span query scorers | ✅ | ❌ |
| Tool call verification | ✅ (programmatic) | ⚠️ (via LLM) |
| Faithfulness checking | ✅ (programmatic) | ⚠️ (via LLM) |
| Response quality | ✅ | ✅ |

## Future Improvements

### If Python SDK Adds Span Querying
When/if the Python SDK adds `trace.getSpans()` support:

1. Uncomment `tool_call_check` scorer in evaluations
2. Uncomment `faithfulness_check` scorer in evaluations
3. Update scorer wrappers to accept `trace` parameter
4. Update documentation to reflect new capabilities

### Alternative Approaches
- Contribute to Braintrust Python SDK to add span querying
- Use Braintrust REST API directly in scorers for span data
- Build hybrid evaluation (Python agent + TypeScript evals)

## References

- [Braintrust Python SDK Docs](https://www.braintrust.dev/docs/reference/python)
- [l8r TypeScript Evaluation Example](https://github.com/braintrustdata/l8r/tree/main/evals)
- [Braintrust Eval Guide](https://www.braintrust.dev/docs/guides/evals)

---

**Last Updated**: 2026-03-02
**SDK Version**: braintrust>=0.0.1 (Python)

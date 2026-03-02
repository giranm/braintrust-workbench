# Weather Chat Evaluations

Comprehensive evaluation suite for the weather chat agent using Braintrust.

## Overview

This evaluation system tests the weather agent across multiple dimensions:

### Single-Turn Evaluations (`weather_conversation.py`)
- **Tool Call Accuracy**: Verifies correct tool usage
- **Weather Accuracy**: Checks response accuracy using LLM-as-a-judge
- **Helpfulness**: Evaluates user-friendliness of responses
- **Response Structure**: Validates formatting and presentation
- **Faithfulness**: Ensures responses are grounded in tool results (no hallucination)

### Multi-Turn Evaluations (`multi_turn_conversation.py`)
- **Conversation Coherence**: Evaluates flow across turns
- **Context Maintenance**: Checks if agent remembers previous exchanges
- **Multi-Turn Helpfulness**: Overall helpfulness across conversation
- **Tool Usage Patterns**: Verifies appropriate tool calling in context

## Quick Start

### 1. Setup Datasets

First, create and populate the evaluation datasets in Braintrust:

```bash
# Navigate to project directory
cd projects/multi-agent-chat-demo

# Activate virtual environment
source .venv/bin/activate

# Run setup script
uv run python evals/setup_evals.py
```

This will:
- Create `WeatherConversationDataset` (10 single-turn test cases)
- Create `MultiTurnWeatherDataset` (6 multi-turn conversations)
- Upload all test cases to Braintrust

### 2. Run Evaluations

Run single-turn evaluation:
```bash
uv run python evals/weather_conversation.py
```

Run multi-turn evaluation:
```bash
uv run python evals/multi_turn_conversation.py
```

### 3. View Results

Results are available in the Braintrust dashboard:
- https://www.braintrust.dev/app/multi-agent-chat-demo

## Evaluation Architecture

### Scorers (`scorers.py`)

Reusable scorer functions following Braintrust patterns:

#### LLM-as-a-Judge Scorers (Claude Haiku)
- **`weather_accuracy_check`**: Validates weather information accuracy
- **`helpfulness_check`**: Evaluates response helpfulness
- **`response_structure_check`**: Checks formatting and presentation
- **`conversation_coherence_check`**: Multi-turn coherence evaluation

#### Python SDK Limitation

**Note**: The Python Braintrust SDK does not currently support querying span data within scorers like the TypeScript SDK does. In TypeScript, you can use `trace.getSpans()` to inspect tool calls and other span data. In Python, scorers only receive `EvalScorerArgs` with `input`, `output`, `expected`, and `metadata`.

This means custom scorers that query span hierarchy (like `tool_call_check` and `faithfulness_check` from the l8r TypeScript app) cannot be directly ported to Python evaluations. These scorers are defined in `scorers.py` for reference but are not used in the evaluation scripts.

**Workarounds**:
1. Use LLM-as-a-judge scorers that work with input/output directly (current approach)
2. Pass span data through task metadata if needed
3. Use online evaluation during agent execution where spans are directly accessible

### Datasets

#### Single-Turn Dataset (`sample_conversations.json`)
10 test cases covering:
- Simple city queries ("What's the weather in London?")
- Specific conditions ("Is it raining in Tokyo?")
- Conversational queries with context
- Capability inquiries (non-weather questions)
- Metric-specific requests (humidity, wind speed)

Categories:
- `single_city`: Basic weather queries
- `specific_metrics`: Requests for specific data
- `conversational`: Natural language queries
- `recommendation`: Requests for advice
- `greeting`: Non-weather interactions

#### Multi-Turn Dataset (`multi_turn_conversations.json`)
6 conversation scenarios covering:
- Sequential city queries
- Follow-up questions about conditions
- Clarifying questions
- Comparison requests
- Recommendation flows

Categories:
- `sequential_cities`: Multiple city queries
- `follow_up_question`: Context-dependent questions
- `clarifying_question`: Requests for specific details
- `comparison`: Comparing weather across cities
- `recommendation_request`: Asking for advice

## Scorer Patterns

### Custom Scorer (Querying Spans)

Example: Tool Call Check
```python
async def tool_call_check(output: str, expected: dict, metadata: dict, trace: Any):
    # Get expected tools from metadata
    expected_tools = metadata.get("expected_tools", [])

    # Query trace for tool spans
    tool_spans = await trace.getSpans(span_type=["tool"])

    # Extract actual tool names
    actual_tools = [
        span.get("span_attributes", {}).get("name")
        for span in tool_spans
    ]

    # Calculate overlap score
    overlap = len(set(expected_tools) & set(actual_tools))
    score = overlap / len(expected_tools) if expected_tools else 1.0

    return {
        "name": "ToolCallCheck",
        "score": score,
        "metadata": {...}
    }
```

### LLM-as-a-Judge Scorer

Example: Helpfulness Check
```python
async def helpfulness_check(output: str, input_text: str):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Rate whether this response is helpful.

    User query: {input_text}
    Response: {output}

    Answer with ONLY 'Y' or 'N'.
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
        "metadata": {"llm_answer": answer}
    }
```

## Using Scorers in the App

Scorers can also be used for **online evaluation** during live agent interactions:

```python
from evals.scorers import helpfulness_check, tool_call_check

# After agent responds
async def evaluate_response(user_message, agent_response, trace):
    # Run scorers
    helpfulness_score = await helpfulness_check(agent_response, user_message)
    tool_score = await tool_call_check(agent_response, {}, {}, trace)

    # Log scores to Braintrust
    current_span().log(
        scores={
            "helpfulness": helpfulness_score["score"],
            "tool_accuracy": tool_score["score"],
        }
    )
```

This enables real-time quality monitoring in production.

## Evaluation Metrics

### Target Scores (Baseline)

Single-turn evaluation targets:
- **ToolCallCheck**: 1.0 (100% - should always call correct tool)
- **WeatherAccuracyCheck**: ≥ 0.9 (90%+)
- **HelpfulnessCheck**: ≥ 0.9 (90%+)
- **ResponseStructureCheck**: ≥ 0.8 (80%+)
- **FaithfulnessCheck**: 1.0 (100% - no hallucination)

Multi-turn evaluation targets:
- **ConversationCoherenceCheck**: ≥ 0.9 (90%+)
- **MultiTurnHelpfulness**: ≥ 0.9 (90%+)
- **ContextMaintenance**: ≥ 0.8 (80%+)

## Adding New Test Cases

### Single-Turn Test Case

Edit `datasets/sample_conversations.json`:

```json
{
  "input": "What's the weather in Seattle?",
  "expected": {
    "tools": ["get_weather"],
    "contains": ["temperature", "Seattle"],
    "city": "Seattle"
  },
  "metadata": {
    "category": "single_city",
    "difficulty": "easy",
    "expected_tools": ["get_weather"]
  }
}
```

### Multi-Turn Test Case

Edit `datasets/multi_turn_conversations.json`:

```json
{
  "messages": [
    {"role": "user", "content": "What's the weather in Seattle?"},
    {"role": "assistant", "content": "placeholder"},
    {"role": "user", "content": "Is it good for hiking?"},
    {"role": "assistant", "content": "placeholder"}
  ],
  "metadata": {
    "category": "outdoor_activity_recommendation",
    "expected_tools": ["get_weather"],
    "turn_count": 2
  }
}
```

Then re-run setup:
```bash
uv run python evals/setup_evals.py
```

## Adding New Scorers

1. Define scorer function in `scorers.py`:
```python
async def my_custom_scorer(output: str, input: str) -> dict:
    # Scoring logic here
    return {
        "name": "MyCustomScorer",
        "score": 0.95,
        "metadata": {...}
    }
```

2. Add to evaluation scripts:
```python
from .scorers import my_custom_scorer

Eval(
    ...,
    scores=[
        ...,
        my_custom_scorer,
    ]
)
```

## Continuous Evaluation

Set up automated evaluations:

```bash
# Run evaluations daily
cron: 0 9 * * * cd /path/to/project && uv run python evals/weather_conversation.py
```

Or use Braintrust's scheduled experiments feature.

## Troubleshooting

### Dataset Not Found
```bash
# Re-run setup
uv run python evals/setup_evals.py
```

### Scorer Errors
Check that:
- `ANTHROPIC_API_KEY` is set in `.env`
- `BRAINTRUST_API_KEY` is set in `.env`
- Agent is properly instrumented with Braintrust

### Import Errors
```bash
# Ensure dependencies are installed
uv sync
```

## References

- [Braintrust Evaluations Guide](https://www.braintrust.dev/docs/guides/evals)
- [Braintrust Cookbook - Evals](https://github.com/braintrustdata/braintrust-cookbook)
- [l8r App Evaluation Example](https://github.com/braintrustdata/l8r)

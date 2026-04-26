# Planning - Multi Agent Turn Google ADK

## Overview

**Project**: multi-agent-turn-google-adk
**Type**: Python
**Focus**: Observability & Tracing, LLM Evaluation, Custom Scorers
**Status**: Planning

## Purpose

Demonstrate that Braintrust integrates effectively with Google Agent Development
Kit (ADK) and can support complex multi-agent workflows — including multi-turn
orchestration, tool use, and both offline and online scoring via Braintrust
automations.

## Goals

### Primary Goal
Build a multi-agent customer support AI application that handles user queries
across multiple conversational turns (not one-shot), with tool access and full
Braintrust instrumentation for tracing, evaluation, and automated scoring.

### Secondary Goals
- [ ] Prove Braintrust + Google ADK integration works end-to-end
- [ ] Demonstrate multi-turn conversation tracing with parent-child span linking
- [ ] Show tool-call tracing within agent turns
- [ ] Implement offline evals with custom scorers
- [ ] Implement online scoring via Braintrust automations (SDK/API)
- [ ] Provide a thin Python CLI for interactive testing

## Scope

### In Scope
- Multi-agent ADK setup with turn-based customer support orchestration
- Mocked tools that agents can invoke (order lookup, refund processing, FAQ search, escalation)
- Braintrust tracing of every agent turn, tool call, and handoff
- Offline evaluation suite with custom scorers
- Online scoring automations configured via Braintrust SDK/API
- Makefile target to provision Braintrust automations as part of project setup
- Thin Python CLI client for multi-turn interaction

### Out of Scope
- Real external service integrations (all tools are mocked)
- React/web frontend
- Production deployment or infrastructure
- Non-Google-ADK agent frameworks

## Configuration

### Model Provider

ADK supports multiple model providers via the `LiteLlm` adapter. The project
defaults to **Anthropic (Claude)** and falls back to Gemini if configured.

The active provider is controlled by `LLM_PROVIDER` in `.env`:

| `LLM_PROVIDER` | Model string | Required env var |
|-----------------|-------------|------------------|
| `anthropic` (default) | `anthropic/claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` |
| `google` | `gemini/gemini-2.0-flash` | `GOOGLE_API_KEY` |

Agent creation uses the LiteLLM wrapper:

```python
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(model=os.environ.get("ADK_MODEL", "anthropic/claude-haiku-4-5-20251001"))
```

### Braintrust Project Name

Derived from the `BRAINTRUST_PROJECT` environment variable — never hardcoded.
Defaults to `multi-agent-turn-google-adk` if unset.

```python
project = os.environ.get("BRAINTRUST_PROJECT", "multi-agent-turn-google-adk")
logger = init_logger(project=project)
```

This allows the same code to log to different Braintrust projects (e.g. dev vs
staging) without code changes.

## Application Design

### Customer Support Scenario

A user contacts support with a question. The system uses multiple specialized
agents that coordinate in a turn-based pattern to resolve the query. A
conversation may span several back-and-forth turns before resolution.

### Agents

| Agent | Role | Tools |
|-------|------|-------|
| **Router** | Classifies intent and delegates to the right specialist | — |
| **Order Agent** | Handles order status, tracking, modifications | `lookup_order`, `cancel_order` |
| **Billing Agent** | Handles refunds, payment issues, invoice queries | `process_refund`, `get_invoice` |
| **FAQ Agent** | Answers general product and policy questions | `search_faq` |

The Router agent receives every user message and decides which specialist should
handle it. Specialists can request clarification from the user (multi-turn) or
hand back to the Router if the query shifts topic.

### Mocked Tools

All tools return deterministic or semi-random mock data. No real backends.

| Tool | Agent | Input | Mock Output |
|------|-------|-------|-------------|
| `lookup_order` | Order | order_id | Order status, tracking URL, ETA |
| `cancel_order` | Order | order_id, reason | Confirmation or denial with reason |
| `process_refund` | Billing | order_id, amount | Refund confirmation, reference number |
| `get_invoice` | Billing | order_id | Invoice PDF URL, line items |
| `search_faq` | FAQ | query | Top-3 matching FAQ entries |

### Multi-Turn Flow

```
User: "Where is my order #12345?"
  → Router classifies → Order Agent
  → Order Agent calls lookup_order(12345)
  → Order Agent responds with status

User: "Can I cancel it?"
  → Router classifies → Order Agent (same context)
  → Order Agent calls cancel_order(12345, "customer request")
  → Order Agent responds with confirmation

User: "Will I get a refund?"
  → Router classifies → Billing Agent (topic shift)
  → Billing Agent calls process_refund(12345, ...)
  → Billing Agent responds with refund details
```

## Braintrust Integration

### Tracing Architecture

Every conversation gets a root span. Each agent turn is a child span. Tool calls
are nested within the agent turn that invoked them.

```
conversation (type: task)                    ← Root span
├── turn-1: router (type: task)              ← Router classification
│   └── gemini call (type: llm)              ← Auto-traced ADK model call
├── turn-1: order-agent (type: task)         ← Specialist handling
│   ├── lookup_order (type: tool)            ← Tool invocation
│   └── gemini call (type: llm)             
├── turn-2: router (type: task)             
│   └── gemini call (type: llm)             
├── turn-2: order-agent (type: task)        
│   ├── cancel_order (type: tool)           
│   └── gemini call (type: llm)             
├── turn-3: router (type: task)              ← Topic shift detected
│   └── gemini call (type: llm)             
└── turn-3: billing-agent (type: task)      
    ├── process_refund (type: tool)         
    └── gemini call (type: llm)             
```

### Offline Evaluation (Evals)

Run via `uv run python src/eval.py`. Uses Braintrust `Eval()` with test datasets
and custom scorers.

**Dataset**: Predefined multi-turn conversation scenarios with expected outcomes.

**Custom Scorers**:

| Scorer | What it measures |
|--------|-----------------|
| `routing_accuracy` | Did the Router pick the correct specialist agent? |
| `tool_selection` | Did the specialist call the right tool with correct args? |
| `response_relevance` | Is the agent response relevant to the user query? (LLM-graded) |
| `conversation_coherence` | Does the multi-turn conversation stay coherent across turns? (LLM-graded) |
| `task_completion` | Was the user's request fully resolved? |

### Online Scoring (Automations)

Braintrust automations run scorers against production logs automatically.
Configured via the Braintrust SDK/API and provisioned as part of project setup.

**Automation setup**:
- `make setup-automations` calls a Python script that uses the Braintrust SDK to
  create/update scoring automations for the project
- Automations attach online scorers to logged spans so every production
  conversation is scored without manual eval runs
- Scorers reuse the same implementations from offline evals where possible

**Online scorers**:

| Scorer | Trigger |
|--------|---------|
| `response_relevance` | Every agent response span |
| `task_completion` | Every completed conversation span |

### Key Metrics

| Metric | Target |
|--------|--------|
| Routing accuracy | >= 90% on test dataset |
| Tool selection accuracy | >= 95% on test dataset |
| Response relevance (LLM-graded) | >= 0.8 average |
| Task completion rate | >= 85% on test dataset |

## CLI Client

Thin Python CLI using `input()` loop. No framework dependencies.

```
$ uv run python src/cli.py

Customer Support AI (type 'quit' to exit)
─────────────────────────────────────────
You: Where is my order #12345?
Agent: Your order #12345 is currently in transit...

You: Can I cancel it?
Agent: I've submitted a cancellation request...

You: quit
Session logged to Braintrust. View at: https://www.braintrust.dev/app/...
```

Features:
- Maintains conversation state across turns
- Prints which agent handled each turn (for transparency)
- Logs the full conversation to Braintrust on exit
- Supports `--verbose` flag to show tool calls and routing decisions

## Technical Approach

### Dependencies
```
braintrust          # Tracing, eval, scoring, automations
google-adk          # Multi-agent orchestration
litellm             # Multi-provider model adapter (Anthropic, Gemini, etc.)
```

### Key Components
1. **Agent definitions** (`src/agents/`): ADK agent configs with system prompts and tool bindings
2. **Tools** (`src/tools/`): Mocked tool implementations
3. **Orchestrator** (`src/orchestrator.py`): Turn-based coordination with Braintrust tracing
4. **Scorers** (`src/scorers.py`): Custom Braintrust scorer implementations
5. **Eval suite** (`src/eval.py`): Offline evaluation with test datasets
6. **Automations** (`src/automations.py`): Script to provision online scoring via Braintrust API
7. **CLI** (`src/cli.py`): Interactive multi-turn client

### Project Structure
```
multi-agent-turn-google-adk/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── router.py           # Router agent definition
│   │   ├── order_agent.py      # Order specialist
│   │   ├── billing_agent.py    # Billing specialist
│   │   └── faq_agent.py        # FAQ specialist
│   ├── tools/
│   │   ├── __init__.py
│   │   └── mock_tools.py       # All mocked tool implementations
│   ├── scorers.py              # Custom Braintrust scorers
│   ├── orchestrator.py         # Turn-based multi-agent coordination
│   ├── eval.py                 # Offline evaluation suite
│   ├── automations.py          # Provision Braintrust online scoring
│   ├── cli.py                  # Interactive CLI client
│   └── main.py                 # Entry point (runs a demo scenario)
├── tests/
│   ├── test_agents.py
│   ├── test_tools.py
│   ├── test_scorers.py
│   └── test_orchestrator.py
├── data/
│   └── eval_scenarios.json     # Multi-turn test conversations
├── docs/
├── Makefile
├── pyproject.toml
├── .mise.toml
└── .env.example
```

## Makefile Targets

```makefile
install          # mise install && uv sync
setup            # cp .env.example .env (if not exists)
setup-automations # Provision Braintrust online scoring automations
run              # Run demo scenario (src/main.py)
cli              # Start interactive CLI (src/cli.py)
eval             # Run offline evaluation suite
test             # Run pytest
lint             # Run ruff
```

## Implementation Plan

### Phase 1: Foundation
- [ ] Finalize project structure
- [ ] Configure mise + uv environment
- [ ] Install dependencies
- [ ] Set up .env with API keys
- [ ] Create Makefile with targets

### Phase 2: Agents & Tools
- [ ] Define mocked tools with deterministic outputs
- [ ] Create Router agent with intent classification prompt
- [ ] Create Order, Billing, and FAQ specialist agents
- [ ] Wire tools to respective agents via ADK

### Phase 3: Orchestrator & CLI
- [ ] Implement turn-based orchestration with agent handoffs
- [ ] Build thin CLI client with conversation state
- [ ] Verify multi-turn flows work end-to-end

### Phase 4: Braintrust Tracing
- [ ] Instrument orchestrator with root conversation span
- [ ] Add child spans for each agent turn
- [ ] Trace tool calls as nested spans
- [ ] Verify span hierarchy in Braintrust dashboard

### Phase 5: Scoring & Evaluation
- [ ] Implement custom scorers (routing, tool selection, relevance, coherence, completion)
- [ ] Create eval dataset with multi-turn scenarios
- [ ] Build offline eval suite using Braintrust Eval()
- [ ] Implement automation provisioning script
- [ ] Add `make setup-automations` target
- [ ] Verify online scoring works on logged spans

### Phase 6: Polish & Documentation
- [ ] Write unit tests
- [ ] Update README with examples and sample output
- [ ] Update implementation.md with decisions
- [ ] Add example Braintrust dashboard screenshots or descriptions

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Google ADK tracing doesn't expose hooks for Braintrust | High | Medium | Wrap ADK runner with manual span creation |
| LLM rate limits during eval runs | Medium | Medium | Use small eval dataset, add backoff |
| Braintrust automation API changes | Low | Low | Pin SDK version, check docs before provisioning |
| LiteLLM adapter quirks with ADK | Medium | Low | Test both providers in CI; pin litellm version |

## References

- Braintrust Docs: https://www.braintrust.dev/docs
- Braintrust Cookbook: https://github.com/braintrustdata/braintrust-cookbook
- Braintrust Automations: https://www.braintrust.dev/docs/guides/automations
- Google ADK Docs: https://google.github.io/adk-docs/
- Google ADK Python: https://github.com/google/adk-python

---

**Last Updated**: 2026-04-26
**Status**: Planning

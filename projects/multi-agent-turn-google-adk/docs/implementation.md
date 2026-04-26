# Implementation Notes - Multi Agent Turn Google ADK

## Overview

This document tracks implementation decisions, technical notes, and progress during development.

**Last Updated**: 2026-04-26

## Implementation Log

### 2026-04-26 - Initial Setup
- Created project structure from template
- Configured mise for Python 3.12 + UV
- Added `google-adk`, `braintrust`, and `litellm` as core dependencies
- Set up environment variables for Braintrust, Anthropic, and Google API keys

### 2026-04-26 - Core Implementation
- Implemented 4 ADK agents: Router, Order, Billing, FAQ
- Built 5 mocked tools with deterministic data and `#`-prefix normalization
- ADK's built-in `sub_agents` + `transfer_to_agent` handles routing natively
- Created orchestrator wrapping ADK Runner with Braintrust span hierarchy
- Built thin CLI client and scripted demo scenario

### 2026-04-26 - Tracing Improvements
- Added LiteLLM callback (`src/tracing.py`) for LLM span capture
- Reworked orchestrator to log input/output on all span levels
- Tool spans now capture both arguments and response data
- Root span logs full conversation as input/output

---

## Architecture Decisions

### Google ADK for Agent Framework

**Date**: 2026-04-26
**Status**: Accepted

**Context**:
Need a multi-agent framework that supports turn-based orchestration with tool use.

**Decision**:
Use Google Agent Development Kit (ADK) as the primary agent framework.

**Consequences**:
- **Positive**: Native Python, built-in sub-agent routing via `transfer_to_agent`,
  session management, tool auto-wrapping from plain functions
- **Negative**: ADK controls LLM calls internally, which requires custom
  instrumentation for observability (see tracing decision below)

### Anthropic via LiteLLM Adapter

**Date**: 2026-04-26
**Status**: Accepted

**Context**:
No Gemini access available. ADK natively targets Gemini but supports other
providers via `LiteLlm` adapter.

**Decision**:
Use `google.adk.models.lite_llm.LiteLlm` with `anthropic/claude-haiku-4-5-20251001`
as the default model. Configurable via `ADK_MODEL` env var.

**Consequences**:
- **Positive**: Works with Anthropic out of the box, easy to switch providers
- **Negative**: Adds `litellm` as a dependency; LiteLLM callback (not
  `wrap_openai`) required for Braintrust tracing

### Custom Tracing Strategy for ADK + Braintrust

**Date**: 2026-04-26
**Status**: Accepted

**Context**:
Braintrust provides two built-in auto-instrumentation mechanisms:

1. **`braintrust.wrap_openai(client)`** — wraps the OpenAI Python SDK client to
   auto-trace all LLM calls with token counts, cost, and latency.
2. **`@braintrust.traced`** — decorator that auto-creates spans for any function,
   logging input arguments and return values.

Neither works cleanly with ADK because ADK is a black box for both LLM calls
and tool invocations:

- ADK calls `litellm.acompletion()` internally, not the OpenAI client, so
  `wrap_openai` cannot intercept those calls.
- ADK invokes tool functions internally through its own runner loop, so
  `@braintrust.traced` on our tool functions would create spans outside the
  orchestration context (no parent turn span).

**Decision**:
Use a **two-layer tracing strategy**:

1. **LiteLLM callback** (`src/tracing.py`): A `CustomLogger` registered via
   `litellm.callbacks` that hooks into every `acompletion` call ADK makes. It
   uses `braintrust.current_span()` to create `llm`-type child spans under
   whatever turn span is active, capturing messages, response, token counts,
   cost, and latency.

2. **Manual span hierarchy** (`src/orchestrator.py`): The orchestrator processes
   ADK runner events and creates `task`-type spans for agent turns and
   `tool`-type spans for tool calls, with proper input/output logging at each
   level.

**Why this gives more insight than auto-wrapping alone**:

`wrap_openai` or `@braintrust.traced` alone would produce a flat list of LLM
calls with no orchestration context. You'd see 10+ Anthropic calls but couldn't
tell which agent made them, what tools were invoked, or how control transferred
between agents.

The two-layer approach produces a trace tree that shows:

```
conversation (task) — full conversation input/output
├── turn:router_agent (task)
│   ├── claude-haiku (llm) — tokens: 1332, cost, latency
│   └── tool:transfer_to_agent — {agent_name: order_agent}
├── turn:order_agent (task) — input: user message, output: response
│   ├── tool:lookup_order — input: {order_id}, output: {order data}
│   └── claude-haiku (llm) — tokens: 1511, cost, latency
└── ...
```

This makes it possible to:
- See total token spend per agent, not just per call
- Identify routing inefficiencies (unnecessary transfers)
- Trace tool call chains within an agent turn
- Correlate LLM cost with the specific user intent being handled
- Debug multi-turn context issues by inspecting per-turn input/output

**Consequences**:
- **Positive**: Rich trace hierarchy, full LLM metrics, tool I/O visibility,
  agent-level attribution
- **Negative**: Custom callback code to maintain; if ADK changes its internal
  LiteLLM usage, the callback may need updating

**Generalizable pattern**: Any orchestration framework (LangGraph, CrewAI, etc.)
that manages LLM calls internally will need a similar two-layer approach. The
LLM-level hook (callback/monkey-patch) captures model metrics, while the
orchestration-level instrumentation captures the domain-specific context.

---

## Braintrust Integration Notes

### Logging & Tracing
- **Implementation**: `src/tracing.py` (LLM callback) + `src/orchestrator.py` (span hierarchy)
- **Logger**: `braintrust.init_logger(project=BRAINTRUST_PROJECT)` — project name from env
- **Span types used**: `task` (conversation root, agent turns), `tool` (tool calls), `llm` (model calls)
- **Key function**: `braintrust.current_span()` — used by LiteLLM callback to nest LLM spans under the active turn

### Evaluations
- **Framework**: `braintrust.Eval()` in `src/eval.py`
- **Runner**: `uv run braintrust eval src/eval.py`
- **Dataset**: `data/eval_scenarios.json` — 8 scenarios (single and multi-turn)
- **Metrics**: routing accuracy, tool selection, task completion

### Custom Scorers
- **Heuristic** (`src/scorers.py`): `routing_accuracy`, `tool_selection`, `task_completion`
- **LLM-graded** (`src/scorers.py`): `response_relevance`, `conversation_coherence` — prompt-based, registered via `src/automations.py`
- **Online scoring**: LLM scorers registered as managed objects via `project.scorers.create()`, then enabled in Braintrust dashboard

---

## Code Organization

### Directory Structure
```
multi-agent-turn-google-adk/
├── src/
│   ├── agents/
│   │   ├── config.py          - LiteLlm model config (env-driven)
│   │   ├── router.py          - Router with sub_agents delegation
│   │   ├── order_agent.py     - Order specialist + tools
│   │   ├── billing_agent.py   - Billing specialist + tools
│   │   └── faq_agent.py       - FAQ specialist + tools
│   ├── tools/
│   │   └── mock_tools.py      - 5 mocked tools with ID normalization
│   ├── tracing.py             - LiteLLM callback for Braintrust LLM spans
│   ├── orchestrator.py        - ADK Runner wrapper with span hierarchy
│   ├── scorers.py             - Heuristic + LLM scorer definitions
│   ├── eval.py                - Offline evaluation suite
│   ├── automations.py         - Braintrust scorer provisioning
│   ├── cli.py                 - Interactive CLI client
│   └── main.py                - Scripted demo scenario
├── tests/
│   ├── test_main.py           - Smoke tests (imports, agent structure)
│   ├── test_tools.py          - Mock tool behavior tests
│   └── test_scorers.py        - Scorer logic tests
├── data/
│   └── eval_scenarios.json    - 8 eval scenarios
└── Makefile                   - install, setup, run, cli, eval, test, etc.
```

---

## Dependencies

### Core Dependencies
- **braintrust** (v0.16.0): Observability, evaluation, scoring, automations
- **google-adk** (v1.31.1): Multi-agent orchestration framework
- **litellm** (v1.83.0): Multi-provider model adapter (Anthropic, Gemini, etc.)
- **python-dotenv**: .env loading for CLI/main entry points

### Development Dependencies
- **pytest**: Testing framework
- **ruff**: Linting and formatting

---

## Lessons Learned

### ADK's Built-in Routing Is Sufficient
No need for a manual orchestrator/router. ADK's `sub_agents` + auto-injected
`transfer_to_agent` tool handles agent delegation natively. The LLM decides
which agent to route to based on the sub-agent descriptions.

### Order ID Normalization Matters
LLMs pass order IDs as the user says them (e.g. `#12345`). Mock tools need to
strip the `#` prefix to match stored data. This is a common pattern in
tool-calling systems.

### `logger.flush()` Is Synchronous
Braintrust's `logger.flush()` returns `None`, not a coroutine. Do not `await` it.

---

**Maintained By**: Giran Moodley
**Last Updated**: 2026-04-26

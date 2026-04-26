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

### 2026-04-26 - Managed Objects
- Extracted prompts to `src/prompts.py` (single source of truth)
- Created `src/setup_managed.py` for idempotent Braintrust setup
- Created `src/push_functions.py` for `braintrust push` (tool code upload)
- Tools created via REST API, schemas added via PATCH, code uploaded via push
- Prompts published via SDK, tool references added via REST API PATCH
- Dataset `eval-scenarios` uploaded as managed golden dataset
- `src/eval.py` uses managed dataset with local JSON fallback

### 2026-04-27 - Scorers and Online Scoring
- Added 4 managed scorers: 2 code-based (span) + 2 LLM-as-Judge (span/trace)
- Code scorers uploaded via `braintrust push` with Pydantic input schemas
- LLM scorers registered via `project.scorers.create(messages=[...])` — fixed `prompt=` bug
- Configured 2 online scoring rules at 100% sampling via `PUT /v1/project_score`
- Added 8 new scorer tests (31 total)

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
- **Runner**: `make eval` (sources `.env` before running `braintrust eval`)
- **Dataset**: Managed dataset `eval-scenarios` in Braintrust (falls back to `data/eval_scenarios.json`)
- **Eval scorers**: `routing_accuracy`, `tool_selection`, `task_completion`

### Managed Objects (`make setup-managed`)
All project assets are registered as Braintrust managed objects:
- **Dataset**: `eval-scenarios` — 8 golden scenarios via `braintrust.init_dataset()`
- **Prompts**: 4 agent prompts via `project.prompts.create()` + REST API PATCH for tool linking
- **Tools**: 5 tool code functions via `braintrust push` (Python 3.12) + schema via REST API PATCH
- **Scorers**: 2 code-based via `braintrust push`, 2 LLM-as-Judge via `project.scorers.create(messages=[...])`
- **Online rules**: 2 rules via `PUT /v1/project_score` (span-level + trace-level, 100% sampling)

**Registration order matters**: tools first (REST API), then prompts (SDK + REST PATCH for tool links), then scorers, then online rules (which reference scorer IDs).

### Custom Scorers
- **Eval-only** (`src/scorers.py`): `routing_accuracy`, `tool_selection`, `task_completion` — used by `Eval()`, not managed objects
- **Managed code scorers** (`src/push_functions.py`): `tool-call-accuracy` (span), `response-format` (span) — uploaded with Python source via `braintrust push`
- **Managed LLM scorers** (`src/setup_managed.py`): `response-helpfulness` (span), `conversation-resolution` (trace) — GPT-4o-mini with CoT, registered with `messages=` format

### Online Scoring Rules
Two automation rules at 100% sampling:
- **Agent Response Quality** (span-level): targets `turn:*` spans with `span_attributes.type = 'task'`, runs `response-format` + `response-helpfulness`
- **Conversation Resolution** (trace-level): targets all traces, runs `conversation-resolution`

Configured via `PUT /v1/project_score` with versioned scorer references (`{type: "function", id, version}`).

---

## Code Organization

### Directory Structure
```
multi-agent-turn-google-adk/
├── src/
│   ├── agents/
│   │   ├── config.py          - LiteLlm model config (imports from prompts.py)
│   │   ├── router.py          - Router with sub_agents delegation
│   │   ├── order_agent.py     - Order specialist + tools
│   │   ├── billing_agent.py   - Billing specialist + tools
│   │   └── faq_agent.py       - FAQ specialist + tools
│   ├── tools/
│   │   └── mock_tools.py      - 5 mocked tools with ID normalization
│   ├── prompts.py             - Central prompt registry (AGENT_PROMPTS dict)
│   ├── tracing.py             - LiteLLM callback for Braintrust LLM spans
│   ├── orchestrator.py        - ADK Runner wrapper with span hierarchy
│   ├── scorers.py             - Eval + managed scorer definitions
│   ├── eval.py                - Offline evaluation suite (managed dataset)
│   ├── setup_managed.py       - Push all managed objects + online rules
│   ├── push_functions.py      - Self-contained for braintrust push (tools + code scorers)
│   ├── automations.py         - Legacy scorer provisioning
│   ├── cli.py                 - Interactive CLI client
│   └── main.py                - Scripted demo scenario
├── tests/
│   ├── test_main.py           - Smoke tests (imports, agent structure)
│   ├── test_tools.py          - Mock tool behavior tests (22 tests)
│   └── test_scorers.py        - Scorer logic tests (19 tests)
├── data/
│   └── eval_scenarios.json    - 8 eval scenarios (seed for managed dataset)
└── Makefile                   - install, setup, setup-managed, run, cli, eval, test
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

### LLM Scorers Need `messages=`, Not `prompt=`
`project.scorers.create(prompt="...")` registers fine but fails at runtime —
the OpenAI API requires a `messages` array. Always use
`messages=[{"role": "user", "content": prompt_text}]`.

### Python SDK Double-Serializes Prompt Tools
`project.prompts.create(tools=[...])` stores tools as a JSON string, not an
array. Braintrust UI won't render the tool references. Workaround: publish
prompts without tools, then PATCH via REST API with `json.dumps(tools)`.

### Tool-Prompt Linking Uses OpenAI Function Format
Braintrust links tools to prompts by matching `function.name` in the prompt's
`tools` array to the tool's `slug`. Use standard OpenAI function-calling format:
`{"type": "function", "function": {"name": "<tool-slug>", ...}}`.

### `braintrust push` and `braintrust eval` Don't Load `.env`
Both CLI commands require env vars in the shell. Makefile targets use
`set -a && . ./.env &&` prefix to source credentials.

---

**Maintained By**: Giran Moodley
**Last Updated**: 2026-04-27

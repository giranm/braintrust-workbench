# Multi Agent Turn Google ADK

Multi-agent turn-based orchestration using Google ADK with Braintrust observability, evaluation, and online scoring.

## Overview

This project showcases **multi-agent orchestration** using [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) with turn-based coordination, instrumented with Braintrust for observability, evaluation, and custom scoring.

It demonstrates that Braintrust integrates effectively with Google ADK and can support complex workflows including multi-turn conversations, tool use, managed objects, and automated online scoring.

**Type**: Python
**Focus**: Observability & Tracing, LLM Evaluation, Custom Scorers, Online Scoring

## What This Demonstrates

- Multi-agent customer support with Router + 3 specialist agents (Order, Billing, FAQ)
- 5 mocked tools with Braintrust-managed schemas and code
- Two-layer tracing: LiteLLM callback (LLM metrics) + manual span hierarchy (orchestration context)
- Managed prompts, tools, datasets, and scorers as Braintrust objects
- Offline evaluation with golden dataset + custom scorers
- Online scoring rules at 100% sampling (span-level and trace-level)

## Prerequisites

- [mise](https://mise.jdx.dev/) installed
- Braintrust account ([sign up](https://www.braintrust.dev/))
- Anthropic API key (default provider) or Google API key (alternative)

## Quick Start

```bash
cd projects/multi-agent-turn-google-adk

# Install tools and dependencies
make install

# Create .env and add API keys
make setup

# Run the scripted demo
make run

# Or start the interactive CLI
make cli-verbose
```

## Makefile Targets

```
make help              # Show all targets
make install           # mise install + uv sync
make setup             # Create .env from template
make setup-managed     # Push datasets, prompts, tools, scorers, and online rules to Braintrust
make setup-automations # Provision online scoring automations (legacy)
make run               # Run scripted demo scenario
make cli               # Interactive CLI
make cli-verbose       # Interactive CLI with routing/tool visibility
make eval              # Run offline Braintrust evaluation
make test              # Run pytest (31 tests)
make lint              # Run ruff
```

## Project Structure

```
multi-agent-turn-google-adk/
├── src/
│   ├── agents/
│   │   ├── config.py          # LiteLlm model config (env-driven)
│   │   ├── router.py          # Routes to specialists via ADK sub_agents
│   │   ├── order_agent.py     # Order status, tracking, cancellations
│   │   ├── billing_agent.py   # Refunds, invoices, payments
│   │   └── faq_agent.py       # General questions, policies
│   ├── tools/
│   │   └── mock_tools.py      # 5 mocked tools with deterministic data
│   ├── prompts.py             # Central prompt registry (single source of truth)
│   ├── tracing.py             # LiteLLM callback for Braintrust LLM spans
│   ├── orchestrator.py        # ADK Runner + Braintrust span hierarchy
│   ├── scorers.py             # Code-based + LLM-as-Judge scorer definitions
│   ├── eval.py                # Offline evaluation suite
│   ├── setup_managed.py       # Push all managed objects to Braintrust
│   ├── push_functions.py      # Self-contained file for braintrust push (tools + code scorers)
│   ├── cli.py                 # Interactive CLI with --verbose
│   └── main.py                # Scripted demo scenario
├── tests/                     # 31 tests
├── data/
│   └── eval_scenarios.json    # 8 golden eval scenarios (also managed dataset)
├── Makefile
├── pyproject.toml
└── .env.example
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
BRAINTRUST_API_KEY=your-key-here
BRAINTRUST_PROJECT=multi-agent-turn-google-adk
LLM_PROVIDER=anthropic
ADK_MODEL=anthropic/claude-haiku-4-5
ANTHROPIC_API_KEY=your-key-here
```

## Braintrust Managed Objects

All project assets are registered as managed objects in Braintrust via `make setup-managed`:

| Object Type | Count | Description |
|------------|-------|-------------|
| **Dataset** | 1 | `eval-scenarios` — 8 golden multi-turn test scenarios |
| **Prompts** | 4 | One per agent (router, order, billing, faq) with tool references |
| **Tools** | 5 | `lookup_order`, `cancel_order`, `process_refund`, `get_invoice`, `search_faq` |
| **Scorers** | 4 | 2 code-based (span-level) + 2 LLM-as-Judge (span/trace-level) |
| **Online Rules** | 2 | Agent Response Quality (span) + Conversation Resolution (trace) |

## Scorers

| Scorer | Level | Type | What it measures |
|--------|-------|------|------------------|
| `response-format` | Span | Code | Is the response well-structured? |
| `tool-call-accuracy` | Span | Code | Did the agent call the expected tools? |
| `response-helpfulness` | Span | LLM-as-Judge | Is the response helpful and actionable? |
| `conversation-resolution` | Trace | LLM-as-Judge | Was the customer's issue fully resolved? |

## Online Scoring

Two automation rules run at 100% sampling on all incoming logs:

- **Agent Response Quality** (span-level): Runs `response-format` + `response-helpfulness` on every agent turn span
- **Conversation Resolution** (trace-level): Runs `conversation-resolution` on every conversation trace

## Tracing Architecture

Uses a two-layer strategy because ADK controls LLM calls internally:

1. **LiteLLM callback** (`src/tracing.py`): Creates `llm` spans with token counts, cost, latency
2. **Manual span hierarchy** (`src/orchestrator.py`): Creates `task` and `tool` spans with orchestration context

```
demo-conversation (task) — full conversation input/output
├── turn:router_agent (task)
│   ├── claude-haiku (llm) — 1,332 tok, $0.002
│   └── tool:transfer_to_agent
├── turn:order_agent (task) — input: user msg, output: response
│   ├── tool:lookup_order — input: {order_id}, output: {order data}
│   └── claude-haiku (llm) — 1,511 tok, $0.002
└── ...
```

## Documentation

- **[docs/planning.md](./docs/planning.md)**: Project goals, scope, and implementation plan
- **[docs/implementation.md](./docs/implementation.md)**: Technical decisions, architecture notes
- **[docs/issues.md](./docs/issues.md)**: Known issues and limitations
- **[docs/changelog.md](./docs/changelog.md)**: Version history

## References

- **[Braintrust Docs](https://www.braintrust.dev/docs)**: Official documentation
- **[Braintrust Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples
- **[Google ADK Docs](https://google.github.io/adk-docs/)**: Agent Development Kit
- **[Google ADK Python](https://github.com/google/adk-python)**: Python SDK

## License

MIT - See [LICENSE](../../LICENSE)

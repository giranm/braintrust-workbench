# Changelog - Multi Agent Turn Google ADK

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-04-27

### Added
- 4 managed scorers: `tool-call-accuracy`, `response-format` (code), `response-helpfulness`, `conversation-resolution` (LLM-as-Judge)
- Online scoring rules: "Agent Response Quality" (span-level, 100%) and "Conversation Resolution" (trace-level, 100%)
- 8 new scorer tests (31 total)
- Pydantic input schemas for code-based scorers
- `setup_online_rules()` in setup_managed.py using `PUT /v1/project_score` API

### Fixed
- LLM scorer registration: use `messages=[...]` format instead of `prompt=` string to avoid OpenAI `missing messages` error

## [0.2.0] - 2026-04-26

### Added
- Braintrust managed objects: dataset, prompts, tools, scorers
- `src/prompts.py` — central prompt registry (single source of truth)
- `src/setup_managed.py` — idempotent setup script for all managed objects
- `src/push_functions.py` — self-contained file for `braintrust push` (tool code + code scorers)
- Prompts reference tools via OpenAI function-calling format (slug matching)
- Tools uploaded with Python source code via `braintrust push` (Python 3.12)
- Tool schemas added via REST API PATCH (preserves pushed code)
- Eval dataset uploaded as managed golden dataset (`eval-scenarios`)
- `make setup-managed` target

### Changed
- Agent prompts extracted from inline strings to `AGENT_PROMPTS` dict in `src/prompts.py`
- `src/eval.py` uses managed dataset when `BRAINTRUST_API_KEY` is set, falls back to local JSON
- Model string `DEFAULT_MODEL` lives in `src/prompts.py` (avoids circular imports)
- `pyproject.toml` updated to `braintrust[cli]` for push support

### Fixed
- Model prefix stripped for Braintrust prompts (`anthropic/claude-haiku-4-5` -> `claude-haiku-4-5`)
- Python SDK double-serializes `tools` param — work around via REST API PATCH
- `braintrust push` requires Python <= 3.13 — use `uvx --python 3.12` in Makefile

## [0.1.0] - 2026-04-26

### Added
- Initial project scaffolding from template
- 4 ADK agents: Router, Order, Billing, FAQ with LiteLLM adapter (Anthropic default)
- 5 mocked tools: lookup_order, cancel_order, process_refund, get_invoice, search_faq
- Orchestrator wrapping ADK Runner with Braintrust span hierarchy
- Two-layer tracing: LiteLLM callback (LLM spans) + manual hierarchy (task/tool spans)
- Thin CLI client with `--verbose` flag
- Scripted demo scenario (`src/main.py`)
- Offline eval suite with 8 multi-turn scenarios and 3 heuristic scorers
- 23 unit tests
- Makefile with install, setup, run, cli, eval, test targets
- Project documentation (README, AGENTS.md, docs/)

# Multi Agent Turn Google ADK

Multi-agent turn-based orchestration using Google ADK with Braintrust observability

## Overview

This project showcases **multi-agent orchestration** using [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) with turn-based coordination, instrumented with Braintrust for observability, evaluation, and custom scoring.

**Type**: Python
**Focus**: Observability & Tracing, LLM Evaluation, Custom Scorers

## What This Demonstrates

- Custom scorers for multi-turn agent interactions
- LLM evaluation of agent responses and orchestration quality
- Observability and tracing of multi-agent turns and tool calls

## Prerequisites

- [mise](https://mise.jdx.dev/) installed
- Braintrust account ([sign up](https://www.braintrust.dev/))
- Google Cloud credentials (for ADK / Gemini access)

## Quick Start

```bash
# Navigate to project
cd projects/multi-agent-turn-google-adk

# Install tools
mise install
mise trust

# Install Python dependencies
uv sync
cp .env.example .env
# Edit .env with your API keys

# Run the demo
uv run python src/main.py
```

## Project Structure

```
multi-agent-turn-google-adk/
├── src/
│   ├── main.py         # Main application
│   └── eval.py         # Braintrust evaluations
├── tests/              # Tests
├── docs/               # Development documentation
│   ├── planning.md         # Project goals and strategy
│   ├── implementation.md   # Technical decisions
│   ├── issues.md           # Known issues and bugs
│   └── changelog.md        # Version history
├── .mise.toml          # Tool configuration
└── pyproject.toml      # Dependencies
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
BRAINTRUST_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

## Running

### Main Application

```bash
uv run python src/main.py
```

### Evaluations

```bash
# Run Braintrust evaluations
uv run python src/eval.py

# View results at: https://www.braintrust.dev/app
```

### Tests

```bash
uv run pytest
```

## Braintrust Integration

This project uses Braintrust for:

- **Observability & Tracing**: Trace multi-agent turns and tool calls across the ADK orchestration
- **LLM Evaluation**: Evaluate agent responses and orchestration quality
- **Custom Scorers**: Score multi-turn agent interactions for coherence, task completion, and handoff quality

## Documentation

See the `docs/` directory for:
- **[planning.md](./docs/planning.md)**: Project goals, scope, and implementation plan
- **[implementation.md](./docs/implementation.md)**: Technical decisions and progress
- **[issues.md](./docs/issues.md)**: Known issues and resolutions
- **[changelog.md](./docs/changelog.md)**: Version history

## References

### Braintrust Resources
- **[Official Docs](https://www.braintrust.dev/docs)**: API reference, guides, concepts
  - [Evaluations](https://www.braintrust.dev/docs/guides/evals)
  - [Logging](https://www.braintrust.dev/docs/guides/logging)
  - [Python SDK](https://www.braintrust.dev/docs/reference/python)
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples and tutorials

### Google ADK Resources
- **[ADK Docs](https://google.github.io/adk-docs/)**: Agent Development Kit documentation
- **[ADK GitHub](https://github.com/google/adk-python)**: Python SDK

## License

MIT - See [LICENSE](../../LICENSE)

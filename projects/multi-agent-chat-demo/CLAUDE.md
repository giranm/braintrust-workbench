# Multi Agent Chat Demo - Claude Code Guide

## Project Overview

Demonstrates Braintrust Observability for multi-agent chat systems with orchestration, conversation logging, and tool use tracing.

**Type**: Python
**Focus**: Observability

## Project Structure

```
multi-agent-chat-demo/
├── .mise.toml          # Tool versions (Python 3.12, UV)
├── CLAUDE.md           # This file
├── README.md           # Public documentation
├── .env.example        # Environment template
├── pyproject.toml      # Python dependencies (UV)
├── src/
│   ├── __init__.py
│   ├── main.py         # Main application
│   └── eval.py         # Braintrust evaluations
├── tests/
│   └── test_main.py    # Tests
└── docs/               # Development documentation
    ├── planning.md         # Project goals and strategy
    ├── implementation.md   # Technical decisions and notes
    ├── issues.md           # Bugs and known issues
    └── changelog.md        # Version history
```

## Technology Stack

- **Python**: 3.12 (managed by mise)
- **UV**: Package management
- **Braintrust**: Observability and logging
- **OpenAI**: LLM provider for agents

## Braintrust Integration

This project demonstrates Braintrust patterns from:
- **[Official Docs](https://www.braintrust.dev/docs)**: Logging, tracing, and observability
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Agent tracing examples

### Patterns Used

1. **Agent Conversation Logging**: Track all multi-agent interactions in Braintrust
   - Docs reference: [Logging Guide](https://www.braintrust.dev/docs/guides/logging)
2. **Tool Use Tracing**: Monitor agent tool calls with full context
   - Docs reference: [Tracing](https://www.braintrust.dev/docs/guides/tracing)
3. **Multi-Agent Orchestration**: Coordinate multiple agents with full observability
   - Cookbook example: [Agent Examples](https://github.com/braintrustdata/braintrust-cookbook)

## Setup and Running

### Prerequisites

```bash
# Ensure you're in the project directory
cd projects/multi-agent-chat-demo

# Install tools
mise install

# Sync dependencies
uv sync
```

### Environment Variables

Required variables in `.env`:
```bash
BRAINTRUST_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

### Running the Project

```bash
# Run main application
uv run python src/main.py

# Run evaluations
uv run python src/eval.py

# Run tests
uv run pytest
```

## Key Files

### `src/main.py`
Main multi-agent chat orchestration with Braintrust logging. Creates multiple agents with different roles and coordinates their interactions while logging everything to Braintrust.

### `src/eval.py`
Evaluations for agent performance, conversation quality, and tool usage effectiveness.

Evaluation metrics:
- Conversation coherence across agents
- Tool usage success rate
- Response quality per agent

### `tests/test_main.py`
Unit tests for agent initialization, orchestration logic, and Braintrust integration.

## Development Workflow

When working on this project:

1. **Read documentation first**:
   - This file (CLAUDE.md) for project overview
   - `docs/planning.md` for goals and strategy
   - `docs/issues.md` for known problems
   - `docs/implementation.md` for technical context

2. **Reference Braintrust resources**:
   - Official docs: https://www.braintrust.dev/docs (for logging and tracing APIs)
   - Cookbook: https://github.com/braintrustdata/braintrust-cookbook (for agent examples)

3. **During development**:
   - Maintain isolation: Use `mise` tools, don't install globally
   - Run demo frequently: Test agent interactions after changes
   - Document decisions: Update `docs/implementation.md` with technical choices
   - Track issues: Log bugs in `docs/issues.md`

4. **After changes**:
   - Update `docs/changelog.md` with notable changes
   - Update README if user-facing features changed
   - Move resolved issues in `docs/issues.md`

## Expected Outputs

Success looks like:
- Console output: Clear agent conversation flow with role labels
- Braintrust dashboard: Full trace of multi-agent interactions with tool calls
- Eval results: High conversation quality scores and successful tool usage

## Common Tasks

### Adding Dependencies

```bash
uv add [package-name]
uv lock
```

### Running Specific Tests

```bash
uv run pytest tests/test_main.py::test_function_name
```

### Debugging

```bash
# Verbose output
uv run python src/main.py --verbose

# Interactive mode
uv run python -i src/main.py
```

## Braintrust-Specific Notes

### Experiment Naming

Use consistent naming: `multi-agent-chat-demo-[variant]-[date]`

Example: `multi-agent-chat-demo-baseline-20260302`

### Dataset Management

Create datasets with multi-turn conversation examples to evaluate agent performance across different scenarios.

### Metrics and Scorers

Custom metrics for this project:
- **Agent Coherence**: Measure conversation flow quality
- **Tool Success Rate**: Track successful tool invocations
- **Response Latency**: Monitor per-agent and total response times

## Troubleshooting

### Common Issues

1. **Import errors**: Run `uv sync` to ensure dependencies are installed
2. **API key errors**: Check `.env` file exists and has valid keys
3. **Mise tool errors**: Run `mise install` and `mise trust`

### Debugging Braintrust

```bash
# Check Braintrust connection
uv run python -c "from braintrust import init_logger; print('Connected!')"

# View recent experiments
# Visit: https://www.braintrust.dev/app
```

## Notes for Claude Code

- This project focuses on multi-agent observability using Braintrust
- Prioritize clear logging and tracing of agent interactions
- Always verify traces appear in Braintrust dashboard after running
- Reference Braintrust docs (https://www.braintrust.dev/docs) for logging APIs
- Reference cookbook (https://github.com/braintrustdata/braintrust-cookbook) for agent patterns
- Keep code simple and well-documented for showcase purposes

### Using Project Documentation

The `docs/` folder contains critical context:
- **Before coding**: Read `planning.md` and `issues.md`
- **During coding**: Update `implementation.md` with decisions
- **After coding**: Update `changelog.md` and resolve issues in `issues.md`

This documentation is in version control and helps maintain context across sessions.

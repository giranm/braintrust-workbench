# Support Desk Investigator - Claude Code Guide

## Project Overview

This project demonstrates how to use **Braintrust** for observability and evaluations of LLM-powered support desk agents. It showcases logging LLM interactions, creating custom evaluation metrics, managing test datasets, and tracking experiments to improve support quality.

**Type**: Python
**Focus**: Observability & Evaluations

## Project Structure

```
support-desk-investigator/
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
- **Braintrust**: Evals and observability
- **OpenAI**: LLM provider (configurable)

## Braintrust Integration

This project demonstrates Braintrust patterns from:
- **[Official Docs](https://www.braintrust.dev/docs)**: Core concepts and API usage
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Implementation examples

### Patterns Used

1. **Custom Scorers**: Building domain-specific evaluation metrics for support quality
   - Docs reference: [Custom Scorers](https://www.braintrust.dev/docs/guides/evals#custom-scorers)
2. **Dataset Management**: Creating and versioning test datasets for consistent evaluation
   - Docs reference: [Datasets](https://www.braintrust.dev/docs/guides/datasets)
3. **Experiment Tracking**: Running and comparing experiments to improve support responses
   - Docs reference: [Experiments](https://www.braintrust.dev/docs/guides/experiments)

## Setup and Running

### Prerequisites

```bash
# Ensure you're in the project directory
cd projects/support-desk-investigator

# Install tools
mise install

# Sync dependencies
uv sync
```

### Environment Variables

Required variables in `.env`:
```bash
BRAINTRUST_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here  # or other LLM provider
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
Main support desk agent implementation with Braintrust logging for observability

### `src/eval.py`
Evaluation framework with custom scorers for support quality metrics

Evaluation metrics:
- Response Quality: Accuracy, helpfulness, and completeness
- Tone & Empathy: Professional and empathetic communication
- Resolution Rate: Ability to resolve or escalate issues appropriately

### `tests/test_main.py`
Unit tests for core functionality

## Development Workflow

When working on this project:

1. **Read documentation first**:
   - This file (CLAUDE.md) for project overview
   - `docs/planning.md` for goals and strategy
   - `docs/issues.md` for known problems
   - `docs/implementation.md` for technical context

2. **Reference Braintrust resources**:
   - Official docs: https://www.braintrust.dev/docs (for API reference and concepts)
   - Cookbook: https://github.com/braintrustdata/braintrust-cookbook (for examples)

3. **During development**:
   - Maintain isolation: Use `mise` tools, don't install globally
   - Run evals frequently: After code changes, run `src/eval.py`
   - Document decisions: Update `docs/implementation.md` with technical choices
   - Track issues: Log bugs in `docs/issues.md`

4. **After changes**:
   - Update `docs/changelog.md` with notable changes
   - Update README if user-facing features changed
   - Move resolved issues in `docs/issues.md`

## Expected Outputs

The project demonstrates:

- Console output: Support agent responses with performance metrics
- Braintrust dashboard: Experiment comparisons, metric trends, trace logs
- Eval results: Quality scores, tone analysis, resolution rates

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

Use consistent naming: `support-desk-investigator-[variant]-[date]`

Example: `support-desk-investigator-baseline-20260217`

### Dataset Management

Test datasets include sample support tickets with expected responses and quality criteria

### Metrics and Scorers

Custom scorers evaluate:
- **Accuracy Score**: Factual correctness of responses
- **Empathy Score**: Tone and customer care quality
- **Resolution Score**: Ability to solve or properly escalate issues

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

- This project focuses on observability and evaluations for support desk scenarios
- Prioritize clarity and educational value
- Always run evals after changes to verify improvements
- Reference Braintrust docs (https://www.braintrust.dev/docs) for API usage
- Reference cookbook (https://github.com/braintrustdata/braintrust-cookbook) for examples
- Keep code simple and well-documented for showcase purposes

### Using Project Documentation

The `docs/` folder contains critical context:
- **Before coding**: Read `planning.md` and `issues.md`
- **During coding**: Update `implementation.md` with decisions
- **After coding**: Update `changelog.md` and resolve issues in `issues.md`

This documentation is in version control and helps maintain context across sessions.

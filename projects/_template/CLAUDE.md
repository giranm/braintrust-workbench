# [Project Name] - Claude Code Guide

## Project Overview

[Describe what this project demonstrates about Braintrust]

**Type**: Python | TypeScript | Fullstack
**Focus**: [e.g., LLM Evaluation, Prompt Engineering, A/B Testing, etc.]

## Project Structure

```
[project-name]/
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

- **Python**: [version] (managed by mise)
- **UV**: Package management
- **Braintrust**: Evals and observability
- **[Other libraries]**: [purpose]

## Braintrust Integration

This project demonstrates Braintrust patterns from:
- **[Official Docs](https://www.braintrust.dev/docs)**: Core concepts and API usage
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Implementation examples

### Patterns Used

1. **[Pattern 1]**: [Description and file location]
   - Docs reference: [Link to relevant docs page]
2. **[Pattern 2]**: [Description and file location]
   - Docs reference: [Link to relevant docs page]
3. **[Pattern 3]**: [Description and file location]
   - Cookbook example: [Link to relevant cookbook example]

## Setup and Running

### Prerequisites

```bash
# Ensure you're in the project directory
cd projects/[project-name]

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
[Description of main functionality]

### `src/eval.py`
[Description of evaluation approach]

Evaluation metrics:
- [Metric 1]: [Description]
- [Metric 2]: [Description]

### `tests/test_main.py`
[Description of test coverage]

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

[Describe what success looks like]

- Console output: [what to expect]
- Braintrust dashboard: [what metrics/experiments to see]
- Eval results: [expected scores/metrics]

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

Use consistent naming: `[project-name]-[variant]-[date]`

Example: `sentiment-eval-baseline-20260216`

### Dataset Management

[How datasets are created/loaded for this project]

### Metrics and Scorers

[Custom metrics or scorers used in evaluations]

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

- This project focuses on [specific Braintrust capability]
- Prioritize [clarity/performance/educational value]
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

# Support Desk Investigator

A Braintrust demo showcasing observability and evaluations for LLM-powered support desk agents.

## Overview

This project showcases **Observability & Evaluations** by demonstrating how to log, monitor, and evaluate LLM-based support agents. Learn how to build custom evaluation metrics, manage test datasets, and track experiments to continuously improve support quality.

**Type**: Python
**Focus**: Observability & Evaluations

## What This Demonstrates

- ✅ Custom scorers for domain-specific evaluation (support quality metrics)
- ✅ Dataset management for consistent evaluation and regression testing
- ✅ Experiment tracking to compare and improve support agent performance

## Prerequisites

- [mise](https://mise.jdx.dev/) installed
- Braintrust account ([sign up](https://www.braintrust.dev/))
- OpenAI API key (or other LLM provider)

## Quick Start

```bash
# Clone and navigate to project
cd projects/support-desk-investigator

# Install tools
mise install

# For Python projects
uv sync
cp .env.example .env
# Edit .env with your API keys

# Run the demo
uv run python src/main.py
```

## Project Structure

```
support-desk-investigator/
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
```

## Running

### Main Application

```bash
# Python
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
# Python
uv run pytest
```

## How It Works

1. **Support Agent**: Processes customer inquiries using an LLM with Braintrust logging for full observability
2. **Custom Scorers**: Evaluates response quality, tone, empathy, and resolution effectiveness
3. **Experiment Tracking**: Compares different prompts, models, and parameters to improve performance

## Braintrust Integration

This project uses Braintrust for:

- **Observability**: Logs all LLM interactions with full trace data for debugging and monitoring
- **Custom Metrics**: Evaluates support quality with domain-specific scorers (accuracy, empathy, resolution)
- **Experiment Management**: Compares variants to optimize support agent performance

### Key Metrics

- **Response Quality**: Accuracy, helpfulness, and completeness (target: >0.8)
- **Tone & Empathy**: Professional and empathetic communication (target: >0.85)
- **Resolution Rate**: Ability to solve or escalate appropriately (target: >0.75)

## Example Output

```
Processing support ticket: "My payment failed but I was charged"
Agent Response: "I understand how frustrating this must be..."
Metrics:
  - Quality Score: 0.87
  - Empathy Score: 0.91
  - Resolution Score: 0.82

View full trace at: https://www.braintrust.dev/app/...
```

### Braintrust Dashboard

View detailed experiment results, metric trends, and trace logs in the Braintrust web interface.

## Customization

### Changing Evaluation Metrics

Edit `src/eval.py` to add or modify custom scorers based on your support quality criteria.

### Adding New Support Scenarios

Extend the test dataset with new ticket types and expected response patterns.

## References

### Braintrust Resources
- **[Official Docs](https://www.braintrust.dev/docs)**: API reference, guides, concepts
  - [Getting Started](https://www.braintrust.dev/docs/getting-started)
  - [Evaluations](https://www.braintrust.dev/docs/guides/evals)
  - [Logging](https://www.braintrust.dev/docs/guides/logging)
  - [Python SDK](https://www.braintrust.dev/docs/reference/python)
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples and tutorials

### Related Resources
- [LLM Evaluation Best Practices](https://www.braintrust.dev/docs/guides/evals#best-practices)
- [Custom Scorers Guide](https://www.braintrust.dev/docs/guides/evals#custom-scorers)

## Documentation

See the `docs/` directory for:
- **[planning.md](./docs/planning.md)**: Project goals, scope, and implementation plan
- **[implementation.md](./docs/implementation.md)**: Technical decisions and progress
- **[issues.md](./docs/issues.md)**: Known issues and resolutions
- **[changelog.md](./docs/changelog.md)**: Version history

## Learn More

- **Braintrust Docs**: https://www.braintrust.dev/docs
- **Braintrust Cookbook**: https://github.com/braintrustdata/braintrust-cookbook
- **Braintrust Community**: https://www.braintrust.dev/community

## Troubleshooting

### Issue: API Key Not Found

**Solution**: Ensure `.env` file exists and contains valid `BRAINTRUST_API_KEY` and `OPENAI_API_KEY`

### Issue: Module Import Errors

**Solution**: Run `uv sync` to install all dependencies

## License

MIT - See [LICENSE](../../LICENSE)

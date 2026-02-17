# [Project Name]

[Brief description of what this project demonstrates]

## Overview

This project showcases **[Braintrust capability]** by [description of the demo].

**Type**: Python | TypeScript | Fullstack
**Focus**: [e.g., LLM Evaluation, Observability, A/B Testing]

## What This Demonstrates

- ✅ [Feature/pattern 1]
- ✅ [Feature/pattern 2]
- ✅ [Feature/pattern 3]

## Prerequisites

- [mise](https://mise.jdx.dev/) installed
- Braintrust account ([sign up](https://www.braintrust.dev/))
- [Other requirements]

## Quick Start

```bash
# Clone and navigate to project
cd projects/[project-name]

# Install tools
mise install

# For Python projects
uv sync
cp .env.example .env
# Edit .env with your API keys

# Run the demo
uv run python src/main.py

# For TypeScript projects
npm install
cp .env.example .env
# Edit .env with your API keys

# Run the demo
npm run dev
```

## Project Structure

```
[project-name]/
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

# TypeScript
npm run dev
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

# TypeScript
npm test
```

## How It Works

[Explain the key components and flow]

1. **[Step 1]**: [Description]
2. **[Step 2]**: [Description]
3. **[Step 3]**: [Description]

## Braintrust Integration

This project uses Braintrust for:

- **[Feature 1]**: [How it's used]
- **[Feature 2]**: [How it's used]
- **[Feature 3]**: [How it's used]

### Key Metrics

- **[Metric 1]**: [Description and threshold]
- **[Metric 2]**: [Description and threshold]

## Example Output

```
[Paste example console output]
```

### Braintrust Dashboard

[Screenshot or description of what to expect in the Braintrust dashboard]

## Customization

### Changing [Parameter]

[How to customize the demo]

### Adding New [Feature]

[How to extend the demo]

## References

### Braintrust Resources
- **[Official Docs](https://www.braintrust.dev/docs)**: API reference, guides, concepts
  - [Getting Started](https://www.braintrust.dev/docs/getting-started)
  - [Evaluations](https://www.braintrust.dev/docs/guides/evals)
  - [Logging](https://www.braintrust.dev/docs/guides/logging)
  - [Python SDK](https://www.braintrust.dev/docs/reference/python)
  - [TypeScript SDK](https://www.braintrust.dev/docs/reference/typescript)
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples and tutorials

### Related Resources
- [Other relevant resources]

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

### Issue: [Common Problem]

**Solution**: [How to fix]

### Issue: [Another Problem]

**Solution**: [How to fix]

## License

MIT - See [LICENSE](../../LICENSE)

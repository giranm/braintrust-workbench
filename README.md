# 🧠 Braintrust Workbench

A collection of independent projects showcasing **Braintrust** (Evals & Observability) capabilities for AI applications.

## Overview

This repository contains isolated demo projects that demonstrate various Braintrust features and patterns. Each project is self-contained with its own environment, dependencies, and documentation.

## Project Structure

```
braintrust-workbench/
├── projects/          # Individual demo projects
│   ├── template/      # Template for new projects
│   │   ├── docs/      # Documentation templates
│   │   └── ...
│   └── [demos]/       # Your showcase projects
│       ├── docs/      # Planning, implementation, issues
│       └── ...
└── scripts/           # Utility scripts
```

## Prerequisites

Before getting started, ensure you have:

- **[mise](https://mise.jdx.dev/)**: Tool version manager
  ```bash
  # Install mise (if not already installed)
  curl https://mise.run | sh
  ```

- **[UV](https://docs.astral.sh/uv/)**: Python package manager (installed via mise)

- **Braintrust Account**: Sign up at [braintrust.dev](https://www.braintrust.dev/)

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd braintrust-workbench
```

### 2. Create a New Project

**Recommended** - Using Claude Code's interactive skill:
```bash
/new-project
```

**Alternative** - Using the bootstrap script:
```bash
./scripts/new-project.sh my-eval-demo python

# Or manually copy the template
cp -r projects/template projects/my-eval-demo
cd projects/my-eval-demo
```

### 3. Enter the Project Environment

```bash
cd projects/my-eval-demo

# Install project-specific tools (Python, Node, etc.)
mise install

# For Python projects
uv sync
source .venv/bin/activate  # Activate virtual environment

# For TypeScript projects
npm install
```

### 4. Configure Braintrust

```bash
# Copy environment template
cp .env.example .env

# Add your Braintrust API key
echo "BRAINTRUST_API_KEY=your-key-here" >> .env
```

### 5. Run the Demo

```bash
# Python
uv run python src/main.py

# TypeScript
npm run dev
```

## Projects

See [projects/README.md](projects/README.md) for a complete index of available demos.

## Creating New Projects

Each project is isolated with its own:
- **Tool versions** (via `.mise.toml`)
- **Dependencies** (via `uv` or `npm`)
- **Documentation** (README.md and CLAUDE.md)
- **Configuration** (environment variables, settings)

### Project Types

- **Python**: LLM evals, data processing, backend services
- **TypeScript**: Frontends, fullstack apps, interactive demos
- **Fullstack**: Combined Python + TypeScript projects

## Braintrust Patterns

This workbench follows patterns from:
- **[Official Documentation](https://www.braintrust.dev/docs)**: API reference, guides, best practices
- **[Braintrust Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples and tutorials

Capabilities demonstrated:
- ✅ Evaluating LLM outputs
- ✅ Prompt engineering and comparison
- ✅ Dataset management
- ✅ Experiment tracking
- ✅ Production observability
- ✅ A/B testing
- ✅ Custom scorers and metrics

## Development Workflow

### Working on a Project

```bash
cd projects/<project-name>

# Check tool versions
mise current

# Run code
uv run python src/main.py  # Python
npm run dev                # TypeScript

# Run tests
uv run pytest              # Python
npm test                   # TypeScript
```

### Adding Dependencies

```bash
# Python
uv add braintrust openai anthropic

# TypeScript
npm install --save braintrust
```

### Running Evaluations

```bash
# Python projects typically include eval scripts
uv run python src/eval.py

# View results on Braintrust dashboard
```

## Contributing

This is a personal workbench, but contributions are welcome:

1. Create a new project in `projects/`
2. Follow the template structure
3. Document your demo thoroughly
4. Include example outputs and eval results

## Resources

- **Braintrust Docs**: https://www.braintrust.dev/docs
- **Braintrust Cookbook**: https://github.com/braintrustdata/braintrust-cookbook
- **mise Documentation**: https://mise.jdx.dev/
- **UV Documentation**: https://docs.astral.sh/uv/

## License

MIT License - see [LICENSE](LICENSE) for details.

## Questions or Issues?

- Check project-specific README.md files
- Reference the Braintrust Cookbook
- Review mise and UV documentation

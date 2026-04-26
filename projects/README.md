# Projects Index

This directory contains individual Braintrust demo projects. Each project is isolated with its own environment, dependencies, and documentation.

## Available Projects

### [Multi Agent Chat Demo](./multi-agent-chat-demo/)

**Type**: Python
**Focus**: Observability - Demonstrates Braintrust logging and tracing for multi-agent chat systems

Multi-agent chat with orchestration showcasing:
- Agent conversation logging with full context
- Tool use tracing across multiple agents
- Multi-agent orchestration and coordination

See [project README](./multi-agent-chat-demo/README.md) for details.

---

### Template

The `template/` directory contains boilerplate files for creating new projects. Use `scripts/new-project.sh` to bootstrap new projects from this template.

## Project Structure

Each project follows this structure:

```
project-name/
├── .mise.toml          # Tool version configuration (Python, Node, etc.)
├── AGENTS.md           # Project-specific guidance for coding agents
├── CLAUDE.md           # Compatibility shim when present
├── README.md           # Project documentation
├── .env.example        # Environment variable template
├── pyproject.toml      # Python project (UV)
│   OR
├── package.json        # TypeScript project (pnpm)
├── src/                # Source code
└── tests/              # Tests and evaluations
```

## Creating a New Project

```bash
# From the repository root
./scripts/new-project.sh <project-name> <type>

# Types: python | typescript | fullstack
```

Example:
```bash
./scripts/new-project.sh sentiment-eval python
cd projects/sentiment-eval
mise install
uv sync
```

## Project Isolation

Each project uses **mise** to manage tool versions independently:

- Python version (e.g., 3.12)
- Node version (e.g., 20)
- UV for Python package management

This ensures projects don't interfere with each other and can use different dependency versions.

## Braintrust Patterns

All projects follow patterns from:
- **[Official Braintrust Docs](https://www.braintrust.dev/docs)**: Core concepts, API reference, SDK guides
- **[Braintrust Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples and tutorials

Key areas covered:
- Evaluations and metrics
- Prompt engineering
- Dataset management
- Experiment tracking
- Production observability
- Custom scorers
- Logging and tracing

## Adding Your Project to This Index

After creating a new project, document it here:

```markdown
### [Project Name](./project-name/)

**Type**: Python | TypeScript | Fullstack
**Focus**: Brief description of what this project demonstrates

Key features:
- Feature 1
- Feature 2

See [project README](./project-name/README.md) for details.
```

---

**Next Steps**: Create your first project with `./scripts/new-project.sh`!

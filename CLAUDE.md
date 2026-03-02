# Braintrust Workbench - Claude Code Guide

## Project Overview

This repository is a collection of independent projects that showcase **Braintrust** (Evals & Observability) capabilities. Each project in the `projects/` directory is isolated with its own environment and dependencies.

## Project Structure

```
braintrust-workbench/
├── .claude/                 # Claude Code configuration
├── CLAUDE.md               # This file
├── README.md               # Public documentation
├── .mise.toml              # Root mise config (reference only)
├── scripts/
│   └── new-project.sh      # Bootstrap new projects
└── projects/
    ├── README.md           # Index of all projects
    ├── _template/          # Template for new projects
    └── [project-name]/     # Individual isolated projects
        ├── .mise.toml      # Project-specific tool versions
        ├── CLAUDE.md       # Project-specific guidance
        ├── README.md       # Project documentation
        ├── docs/           # Development documentation
        │   ├── planning.md
        │   ├── implementation.md
        │   ├── issues.md
        │   └── changelog.md
        └── ...
```

## Key Principles

### 1. **Isolation**
- Each project has its own `.mise.toml` defining Python/Node versions
- Each project has its own virtual environment (`.venv/`)
- Dependencies are managed per-project (UV for Python, npm/pnpm for TypeScript)

### 2. **Braintrust Patterns**
- Reference the **Braintrust Documentation** for official guides: https://www.braintrust.dev/docs
- Reference the **Braintrust Cookbook** for practical examples: https://github.com/braintrustdata/braintrust-cookbook
- Common use cases: LLM evals, prompt engineering, observability, A/B testing
- Always use Braintrust SDK best practices from the docs and cookbook

### 3. **Technology Stack**
- **Python**: Primary language for most demos, managed via UV
- **TypeScript**: For frontend/fullstack demos, managed via npm/pnpm
- **mise**: Tool version management for isolation
- **UV**: Python package and project management

## Working with Projects

### Creating a New Project

**Recommended**: Use the interactive Claude skill:
```bash
/new-project
```

The skill will guide you through:
- Project name and type selection
- Description and focus area
- Key features to demonstrate
- Automatic setup and initialization

**Alternative**: Use the bootstrap script (static):
```bash
./scripts/new-project.sh <project-name> <type>
# type: python | typescript | fullstack
# Note: Requires manual editing of placeholders
```

**Manual setup**:
1. Copy `projects/_template/` to `projects/<project-name>/`
2. Update `.mise.toml` with required tool versions
3. Replace placeholders in `CLAUDE.md` and `README.md`
4. Initialize the project (uv init or npm init)

### Entering a Project

```bash
cd projects/<project-name>
mise install          # Install project-specific tools
mise trust            # Trust the local .mise.toml

# For Python projects
uv sync               # Install dependencies
source .venv/bin/activate  # or: mise exec -- python

# For TypeScript projects
npm install           # or pnpm install
```

### Project-Specific Guidance

When working in a specific project:
1. **Read documentation first**:
   - `projects/<project-name>/CLAUDE.md` - Project overview
   - `projects/<project-name>/docs/planning.md` - Goals and strategy
   - `projects/<project-name>/docs/issues.md` - Known problems
   - `projects/<project-name>/docs/implementation.md` - Technical context
2. Follow the project's specific patterns and requirements
3. Reference the Braintrust cookbook for eval/observability patterns
4. Maintain isolation - don't cross-pollinate dependencies
5. **Document as you go**:
   - Update `docs/implementation.md` with decisions
   - Log issues in `docs/issues.md`
   - Update `docs/changelog.md` after changes

## Braintrust Integration

### Documentation Resources

**Official Documentation**: https://www.braintrust.dev/docs
- Getting Started guides
- API Reference
- SDK documentation (Python, TypeScript, REST)
- Evaluations and Scoring
- Datasets and Experiments
- Prompt Playground
- Observability and Logging
- Best practices

**Cookbook Examples**: https://github.com/braintrustdata/braintrust-cookbook
- Practical code examples
- End-to-end tutorials
- Integration patterns
- Real-world use cases

### Common Patterns

Refer to the docs and cookbook for:
- Setting up evaluations
- Logging LLM calls
- Creating datasets
- Running experiments
- Comparing prompts
- Monitoring in production
- Using custom scorers
- Building eval pipelines

### Environment Variables

Projects typically need:
```bash
BRAINTRUST_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-key  # or other LLM providers
```

Store these in `.env` (never commit!) and use `.env.example` as a template.

## Commands and Workflows

### Common Tasks

When asked to create or modify projects:
1. Check if working in root or a specific project directory
2. If in a project, respect its `.mise.toml` and use local tools
3. For Python: use `uv` commands (uv add, uv run, etc.)
4. For TypeScript: use npm/pnpm commands
5. Always run tests and evals after changes

### Running Code

```bash
# Python projects
cd projects/<project-name>
uv run python src/main.py
uv run pytest

# TypeScript projects
cd projects/<project-name>
npm run dev
npm test
```

## File Management

### What to Commit
- Source code and tests
- Configuration files (`.mise.toml`, `pyproject.toml`, `package.json`)
- Lock files (`uv.lock`, `package-lock.json`)
- Documentation (README.md, CLAUDE.md)
- **Development docs** (`docs/planning.md`, `docs/implementation.md`, `docs/issues.md`, `docs/changelog.md`)
- Environment templates (`.env.example`)

### What NOT to Commit
- Virtual environments (`.venv/`, `node_modules/`)
- Environment files with secrets (`.env`)
- Build artifacts (`dist/`, `build/`, `__pycache__/`)
- IDE-specific files (unless agreed upon)
- Braintrust local cache/state

## Documentation Workflow

Each project has a `docs/` directory for development documentation:

### Planning (`docs/planning.md`)
- Project goals and scope
- Implementation strategy
- Success criteria
- **Read before starting work**

### Implementation (`docs/implementation.md`)
- Technical decisions and rationale
- Architecture notes
- Braintrust integration details
- **Update as you make decisions**

### Issues (`docs/issues.md`)
- Known bugs and workarounds
- Technical debt
- **Check before starting, update when finding issues**

### Changelog (`docs/changelog.md`)
- Version history
- Notable changes
- Eval metric improvements
- **Update after completing features**

### Why Document in Version Control?

- ✅ Context persists across sessions
- ✅ AI assistants (Claude Code/ChatGPT Codex etc) can reference it
- ✅ Decisions are tracked with rationale
- ✅ Issues and resolutions are recorded
- ✅ Project history is preserved

## Best Practices

1. **Before starting work**: Read the project's CLAUDE.md
2. **Tool versions**: Respect mise configurations, don't change without reason
3. **Dependencies**: Keep them minimal and documented
4. **Documentation**: Update README.md when adding features
5. **Testing**: Include tests and Braintrust evals for each project
6. **Braintrust patterns**: Always check the official docs and cookbook before implementing custom solutions
7. **API usage**: Follow SDK best practices from https://www.braintrust.dev/docs

## Troubleshooting

### Mise issues
```bash
mise doctor           # Check mise installation
mise trust            # Trust local config
mise install          # Install all tools
```

### Python/UV issues
```bash
uv sync               # Sync dependencies
uv lock --upgrade     # Update lock file
uv cache clean        # Clear cache
```

### TypeScript issues
```bash
rm -rf node_modules package-lock.json
npm install           # Fresh install
```

## Notes for Claude Code

- This is a **showcase/demo repository**, not a production system
- Prioritize clarity and educational value over optimization
- Each project should be self-contained and runnable
- Document Braintrust setup steps clearly
- Include example outputs and eval results in READMEs
- When in doubt, reference the Braintrust docs (https://www.braintrust.dev/docs) and cookbook
- Check the docs for API reference and best practices
- Check the cookbook for implementation examples

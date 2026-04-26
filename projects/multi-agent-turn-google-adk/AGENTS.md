# AGENTS.md

This file is the source of truth for project-level agent guidance.

## Project overview

Demonstrates multi-agent turn-based orchestration using Google Agent Development Kit (ADK) with Braintrust observability, evaluation, and custom scoring.

**Type**: Python
**Focus**: Observability & Tracing, LLM Evaluation, Custom Scorers

## Working context

This project is part of the Braintrust workbench. Keep it isolated, runnable,
and easy to understand as a standalone demo.

## Read order

Before non-trivial work:

1. This file
2. `README.md`
3. `docs/planning.md`
4. `docs/issues.md`
5. `docs/implementation.md`

## Project structure

```text
multi-agent-turn-google-adk/
├── .mise.toml          # Tool versions
├── AGENTS.md           # Source of truth for agent guidance
├── CLAUDE.md           # Compatibility shim
├── README.md           # Public documentation
├── docs/               # Planning, implementation, issues, changelog
├── .env.example        # Environment template
├── pyproject.toml      # Python dependencies
├── src/                # Project code
└── tests/              # Tests
```

## Working model

- Prefer clarity and educational value over unnecessary complexity.
- Keep dependencies minimal and documented.
- Respect the local `.mise.toml`.
- Reference Braintrust docs and cookbook before inventing custom patterns:
  `https://www.braintrust.dev/docs`
  `https://github.com/braintrustdata/braintrust-cookbook`
- Reference Google ADK docs: `https://google.github.io/adk-docs/`

## Tooling

- Use `uv` for Python package management.
- Use `mise install` and `mise trust` when entering the project for the first
  time or after toolchain changes.

### Setup and running

```bash
cd projects/multi-agent-turn-google-adk
mise install
mise trust
uv sync
cp .env.example .env
uv run python src/main.py
uv run python src/eval.py
uv run pytest
```

## Documentation workflow

- Update `docs/implementation.md` when making technical decisions.
- Log new bugs or limitations in `docs/issues.md`.
- Update `docs/changelog.md` after meaningful changes.
- Keep `README.md` accurate when setup steps or user-facing behavior change.

## Braintrust-specific expectations

- Run evals after meaningful changes when the project includes them.
- Document datasets, metrics, scorers, and experiment expectations clearly.
- Keep setup steps for API keys and Braintrust configuration explicit.

### Reference resources

- Official docs: `https://www.braintrust.dev/docs`
- Cookbook: `https://github.com/braintrustdata/braintrust-cookbook`

### Environment variables

Typical variables in `.env`:

```bash
BRAINTRUST_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

## File hygiene

- Commit source, tests, config, lock files, project docs, and `.env.example`.
- Do not commit `.env`, `.venv`, `node_modules`, build artifacts, or caches.

## Compatibility

If `CLAUDE.md` exists, treat it as a compatibility shim. If it ever disagrees
with this file, follow `AGENTS.md` and update the shim.

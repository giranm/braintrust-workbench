# AGENTS.md

This file is the source of truth for project-level agent guidance.

## Project overview

[Describe what this project demonstrates about Braintrust]

**Type**: Python | TypeScript | Fullstack
**Focus**: [e.g., LLM Evaluation, Prompt Engineering, A/B Testing, etc.]

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
[project-name]/
├── .mise.toml          # Tool versions
├── AGENTS.md           # Source of truth for agent guidance
├── CLAUDE.md           # Compatibility shim, if present
├── README.md           # Public documentation
├── docs/               # Planning, implementation, issues, changelog
├── .env.example        # Environment template
├── pyproject.toml      # Python dependencies, when applicable
├── package.json        # TypeScript dependencies, when applicable
├── Dockerfile.backend  # Fullstack backend container, when applicable
├── Dockerfile.frontend # Fullstack frontend container, when applicable
├── docker-compose.yml  # Fullstack orchestration, when applicable
├── Makefile            # Unified command interface, when applicable
└── src/ or app dirs    # Project code
```

## Working model

- Prefer clarity and educational value over unnecessary complexity.
- Keep dependencies minimal and documented.
- Respect the local `.mise.toml`.
- Reference Braintrust docs and cookbook before inventing custom patterns:
  `https://www.braintrust.dev/docs`
  `https://github.com/braintrustdata/braintrust-cookbook`

## Tooling

- For Python work, prefer `uv`.
- For TypeScript work, prefer `pnpm` for manual package management unless the
  project already standardizes on another tool.
- Use `mise install` and `mise trust` when entering the project for the first
  time or after toolchain changes.

### Setup and running

Typical local setup:

```bash
cd projects/[project-name]
mise install
mise trust
```

Python projects typically continue with:

```bash
uv sync
cp .env.example .env
uv run python src/main.py
uv run python src/eval.py
uv run pytest
```

Fullstack projects may use Docker and Make:

```bash
make setup
make up
make logs
make test
make down
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

Common patterns to reference:

- eval setup and scorers
- datasets and experiments
- logging and tracing
- prompt comparison
- observability in production

### Environment variables

Typical variables in `.env`:

```bash
BRAINTRUST_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

## File hygiene

- Commit source, tests, config, lock files, project docs, and `.env.example`.
- Do not commit `.env`, `.venv`, `node_modules`, build artifacts, or caches.

## Expected outputs

Document what success looks like for the project:

- expected console output
- expected Braintrust dashboard results
- expected evaluation metrics or thresholds

## Compatibility

If `CLAUDE.md` exists, treat it as a compatibility shim. If it ever disagrees
with this file, follow `AGENTS.md` and update the shim.

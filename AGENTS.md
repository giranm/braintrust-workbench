# AGENTS.md

This file is the source of truth for agent guidance in this repository.

## Working context

This repository is a workbench of isolated demo projects that showcase
Braintrust evals and observability capabilities. Each project under
`projects/` is self-contained with its own tooling, dependencies, and docs.

## Startup

Read these in order before non-trivial work:

1. `.agent/AGENTS.md`
2. `.agent/memory/personal/PREFERENCES.md`
3. `.agent/memory/working/REVIEW_QUEUE.md`
4. `.agent/memory/semantic/LESSONS.md`
5. `.agent/protocols/permissions.md`

## Skills

Repository-scoped skills live in `.agent/skills/`.

- Read `.agent/skills/_index.md` first.
- Load a full `SKILL.md` only when its triggers match the task.
- Edit skills in `.agent/skills/`.
- `.agents/skills/` may exist as a compatibility mirror path for tools that
  expect that layout; it should resolve to the same files.

## Recall before non-trivial tasks

For deploy, ship, release, migration, schema change, timestamp, timezone,
date, failing test, debug, investigate, or refactor work, run:

```bash
python3 .agent/tools/recall.py "<one-line description of what you're about to do>"
```

Surface results in a `Consulted lessons before acting:` block. If a surfaced
lesson would be violated by your intended action, stop and explain why.

## Memory discipline

- Update `.agent/memory/working/WORKSPACE.md` as you work.
- After significant actions, run:
  `python3 .agent/tools/memory_reflect.py <skill> <action> <outcome>`
- Never delete memory entries; archive only.
- Quick state:
  `python3 .agent/tools/show.py`
- Teach a rule in one shot:
  `python3 .agent/tools/learn.py "<rule>" --rationale "<why>"`

## Hard rules

- No force push to `main`, `production`, or `staging`.
- No modification of `.agent/protocols/permissions.md`.
- Never hand-edit `.agent/memory/semantic/LESSONS.md`; use the review tools.
- If `REVIEW_QUEUE.md` shows pending > 10 or oldest staged > 7 days, review
  candidates before substantive work.

## Working model

- Prefer clarity and educational value over cleverness or over-optimization.
- Keep each project isolated; do not cross-pollinate dependencies or config.
- Respect local `.mise.toml` files and use project-local tooling.
- Check the Braintrust docs and cookbook before inventing custom patterns:
  `https://www.braintrust.dev/docs`
  `https://github.com/braintrustdata/braintrust-cookbook`

## Project structure

```text
braintrust-workbench/
├── .agent/                  # Agentic-stack brain (memory, skills, protocols)
├── .claude/                 # Optional Claude-specific command UX
├── AGENTS.md                # Source of truth for agent guidance
├── CLAUDE.md                # Compatibility shim
├── README.md                # Public documentation
├── .mise.toml               # Root mise config (reference only)
├── scripts/
│   └── new-project.sh       # Bootstrap new projects
└── projects/
    ├── README.md            # Index of all projects
    ├── _template/           # Template for new projects
    └── [project-name]/      # Individual isolated projects
        ├── AGENTS.md        # Project-specific guidance
        ├── CLAUDE.md        # Compatibility shim, if present
        ├── README.md        # Project documentation
        ├── docs/            # Development documentation
        │   ├── planning.md
        │   ├── implementation.md
        │   ├── issues.md
        │   └── changelog.md
        └── ...
```

## Project creation

If the user asks to create a new demo project:

- Load the repo skill `new-project` from `.agent/skills/new-project/SKILL.md`.
- Use `./scripts/new-project.sh <name> <type>` as the shared base scaffold.
- Ensure generated projects include `AGENTS.md` as the project-level source of
  truth.
- If `CLAUDE.md` exists in a generated project, keep it as a thin compatibility
  shim that defers to `AGENTS.md`.
- Finish placeholder replacement and project indexing after scaffolding.
- Ask before dependency installation.

## Entering projects

- Read `projects/<project-name>/AGENTS.md` first when working in a project.
- Then read `README.md`, `docs/planning.md`, `docs/issues.md`, and
  `docs/implementation.md` before making non-trivial changes.
- Follow the project's specific patterns and requirements.
- Maintain isolation; do not cross-pollinate dependencies between demos.
- Update `docs/implementation.md` as decisions are made.
- Update `docs/changelog.md` after meaningful feature work.
- Keep `docs/issues.md` current when you discover or resolve problems.

## Braintrust resources

Use these as the default references before inventing custom integrations:

- Official docs: `https://www.braintrust.dev/docs`
- Cookbook: `https://github.com/braintrustdata/braintrust-cookbook`

Common areas to reference:

- evaluations and scoring
- datasets and experiments
- prompt engineering and comparison
- observability, logging, and tracing
- production monitoring
- custom scorers and metrics

## Tooling expectations

- For Python projects, prefer `uv` commands such as `uv sync`, `uv add`,
  `uv run python`, and `uv run pytest`.
- For TypeScript projects, prefer `pnpm` for manual package management unless
  the specific generated project already standardizes on another tool.
- Use `mise install` and `mise trust` when entering a project for the first
  time or after changing `.mise.toml`.

## Environment variables

Projects typically need:

```bash
BRAINTRUST_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here  # or another LLM provider
```

Store secrets in `.env` and keep `.env.example` as the committed template.

## Commands and workflows

When asked to create or modify projects:

1. Check whether you are working in the repo root or inside a specific project.
2. If inside a project, respect its `.mise.toml` and use local tools.
3. For Python work, prefer `uv` commands.
4. For TypeScript work, prefer `pnpm` for manual package management unless the
   project already standardizes on another tool.
5. Run the smallest relevant tests and evals after changes.

### Running code

```bash
# Python projects
cd projects/<project-name>
uv run python src/main.py
uv run pytest

# TypeScript projects
cd projects/<project-name>
pnpm dev
pnpm test
```

## File hygiene

- Commit source, tests, config, lock files, project docs, and `.env.example`.
- Do not commit `.env`, `.venv`, `node_modules`, build artifacts, or caches.
- Keep project READMEs and setup steps accurate when behavior changes.

## Documentation workflow

Each project's `docs/` directory exists to preserve context across sessions:

- `docs/planning.md`: goals, scope, implementation strategy, success criteria
- `docs/implementation.md`: technical decisions, architecture notes, progress
- `docs/issues.md`: known bugs, workarounds, technical debt
- `docs/changelog.md`: version history and notable changes

Keep these files current. They are part of the agent contract, not optional notes.

## Troubleshooting references

- Mise issues:
  `mise doctor`
  `mise trust`
  `mise install`
- Python and uv issues:
  `uv sync`
  `uv lock --upgrade`
  `uv cache clean`
- TypeScript dependency resets:
  remove `node_modules` and the existing lockfile, then reinstall with the
  package manager the project standardizes on.

## Notes

- This is a showcase repository, not a production monolith.
- Every demo should stay runnable and understandable in isolation.
- When adding Braintrust functionality, document the relevant setup steps
  clearly in the project README and docs.
- Include example outputs and eval results in READMEs when they materially
  improve the educational value of the demo.

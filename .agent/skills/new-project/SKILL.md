---
name: new-project
description: Create a new Braintrust demo project in `projects/` by gathering project details, scaffolding from the template, and finishing repo documentation.
version: 2026-04-26
triggers: ["new project", "create new project", "bootstrap project", "/new-project"]
tools: [bash, memory_reflect]
preconditions: ["projects/_template exists", "scripts/new-project.sh exists"]
constraints: ["validate project name before scaffolding", "keep each project isolated", "ask before dependency installation"]
---

# New Project — Codex adapter for the Braintrust workbench

Use this skill when the user wants a new demo project under `projects/`.
This is the repository's agent-facing project creation flow.

## Inputs to gather
If the user does not provide them up front, ask concise follow-up questions for:
- project name, using lowercase letters, numbers, and hyphens only
- project type: `python`, `typescript`, `fullstack`, or `custom`
- one-line description
- Braintrust focus area
- 2-3 key features or patterns to demonstrate

## Workflow
1. **Validate first.**
   - Reject invalid names.
   - Stop if `projects/<name>` already exists.
   - Confirm the requested type is supported by `scripts/new-project.sh`.
2. **Scaffold the base project.**
   - Run `./scripts/new-project.sh <name> <type>` from the repo root.
   - Treat this script as the shared backend for directory creation and base files.
3. **Finish project-specific content.**
   - Replace any remaining placeholders or generic boilerplate in the generated
     `README.md`, `AGENTS.md`, and `docs/*.md`.
   - If a generated `CLAUDE.md` is present, keep it as a thin compatibility
     shim that points back to `AGENTS.md`.
   - Ensure the description, focus area, and feature list reflect the user's inputs.
   - Preserve the generated project structure unless the user asks for a broader change.
4. **Update the project index.**
   - Add an entry to `projects/README.md` for the new project.
5. **Handle environment setup carefully.**
   - If the user explicitly wants setup completed, run the smallest appropriate
     install step for that project type.
   - Ask before dependency installation because installs modify local environments
     and can be expensive or policy-gated.
6. **Provide next steps.**
   - Show the project path.
   - Show the minimal run/setup commands for the chosen project type.

## Repo-specific guidance
- Prefer the existing template and bootstrap script over recreating scaffolds by hand.
- For Python projects, keep the generated flow aligned with `mise` + `uv`.
- For TypeScript projects, preserve generated project conventions, but prefer
  `pnpm` for any manual follow-up package management unless the project already
  standardizes on something else.
- For `custom` projects, keep the blank-canvas structure lean and docs-first.
- Generated projects should treat `AGENTS.md` as the project-level source of truth.

## Examples
- "Create a new project called `sentiment-eval` for LLM evaluation."
- "Bootstrap a fullstack demo for prompt observability."
- "/new-project"

## Self-rewrite hook
After every 5 uses, or after any project scaffold failure:
1. Review the last 5 `new-project` episodic entries.
2. If the bootstrap script and the skill have drifted, update this skill to match the real flow.
3. If the same placeholder or setup step is repeatedly fixed by hand, add that step here.

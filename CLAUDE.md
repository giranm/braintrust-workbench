# Claude Compatibility Note

`AGENTS.md` is the source of truth for repository guidance in this project.

When working here with Claude:

1. Read [AGENTS.md](./AGENTS.md) first.
2. Apply the instructions in `.agent/` exactly as described there.
3. Use `.claude/commands/` only for Claude-specific command UX such as
   `/new-project`; those command docs should stay consistent with `AGENTS.md`.

If this file and `AGENTS.md` ever disagree, follow `AGENTS.md` and update the
Claude-specific wrapper or command docs to match.

# Claude Code Configuration

This directory contains Claude Code configuration for the Braintrust Workbench.

## Structure

- `commands/` - Custom Claude Code skills and commands

## Available Skills

### `/new-project`

Creates a new Braintrust demo project with interactive setup.

**Usage**: `/new-project` or `Skill(skill="new-project")`

**What it does**:
- Asks interactive questions about your project
- Creates project structure from template
- Replaces all placeholders with your inputs
- Sets up mise environment and dependencies
- Initializes the project ready to use

**Replaces**: The static `scripts/new-project.sh` with a dynamic, interactive experience.

See `commands/new-project.md` for details.

## Notes

- Claude Code will automatically read the root `CLAUDE.md` for project guidance
- Project-specific `CLAUDE.md` files provide context when working in subdirectories
- Skills provide interactive, intelligent project management

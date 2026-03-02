# new-project

Creates a new Braintrust demo project with interactive setup.

## Description

This skill guides you through creating a new isolated Braintrust project in the `projects/` directory. It uses the template structure and asks interactive questions to properly configure your project.

## Behavior

When invoked, this skill will:

1. **Ask interactive questions** about the project:
   - Project name (lowercase with hyphens)
   - Project type (Python, TypeScript, or Fullstack)
   - Brief description
   - Braintrust focus area
   - Key features/patterns to demonstrate

2. **Create project structure** from template:
   - Copy template files to `projects/<project-name>/`
   - Copy `docs/` directory with planning and tracking templates
   - Replace all placeholders with user-provided values
   - Generate appropriate project files based on type

3. **Set up the environment**:
   - Create `.mise.toml` with appropriate tool versions
   - For Python: Create `pyproject.toml`, source structure
   - For TypeScript: Create `package.json`, `tsconfig.json`
   - Create `.env.example` with necessary API keys

4. **Initialize the project**:
   - Run `mise install` to install tools
   - For Python: Run `uv sync` to install dependencies
   - For TypeScript: Run `npm install`

5. **Provide next steps** for the user

## Usage

```
/new-project
```

Or via the Skill tool from Claude Code.

## Interactive Questions

The skill will ask:

1. **Project name**: What should the project be called? (e.g., "sentiment-eval", "chat-ui")
2. **Project type**: Python, TypeScript, or Fullstack?
3. **Description**: Brief one-line description of the project
4. **Focus area**: What Braintrust capability does this showcase? (e.g., "LLM Evaluation", "Prompt Engineering", "A/B Testing")
5. **Key features**: What are 2-3 key patterns or features this demonstrates?

## Template Replacements

The skill will replace these placeholders:

- `[Project Name]` → Proper case project name
- `[project-name]` → Lowercase project name with hyphens
- `[Brief description...]` → User-provided description
- `[Braintrust capability]` → User-provided focus area
- `[Feature/pattern 1]`, `[Feature/pattern 2]`, etc. → User-provided features
- `[Type]` → Python | TypeScript | Fullstack

## Example Flow

```
User: /new-project

Claude: I'll help you create a new Braintrust project. Let me ask you a few questions...

[Interactive prompts appear]

Claude: Great! Creating your project "sentiment-eval"...
- ✅ Created project structure
- ✅ Configured mise for Python 3.12
- ✅ Generated pyproject.toml
- ✅ Created source files
- ✅ Installed dependencies

Your project is ready at: projects/sentiment-eval/

Next steps:
  cd projects/sentiment-eval
  cp .env.example .env
  # Add your API keys to .env
  uv run python src/main.py
```

## Notes

- Uses the existing template structure in `projects/_template/`
- Maintains isolation via mise configuration
- Follows Braintrust patterns from docs and cookbook
- Creates runnable projects with sensible defaults

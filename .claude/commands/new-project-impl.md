# Implementation Guide for new-project Skill

This file provides detailed implementation instructions for Claude Code when executing the `new-project` skill.

## Step-by-Step Implementation

### 1. Gather Project Information

Use `AskUserQuestion` to collect:

```typescript
questions: [
  {
    question: "What should the project be called? (use lowercase with hyphens)",
    header: "Project name",
    options: [
      { label: "sentiment-eval", description: "Example: sentiment evaluation" },
      { label: "chat-ui", description: "Example: chat interface" },
      { label: "rag-system", description: "Example: RAG implementation" },
      { label: "Other", description: "Custom name" }
    ]
  },
  {
    question: "What type of project?",
    header: "Type",
    options: [
      { label: "Python", description: "Python project with UV" },
      { label: "TypeScript", description: "TypeScript/Node project" },
      { label: "Fullstack", description: "Python backend + TypeScript frontend" }
    ]
  },
  {
    question: "Brief one-line description?",
    header: "Description",
    options: [
      { label: "LLM evaluation demo", description: "Evaluating model outputs" },
      { label: "Prompt engineering showcase", description: "Comparing prompts" },
      { label: "Observability demo", description: "Logging and tracing" },
      { label: "Other", description: "Custom description" }
    ]
  },
  {
    question: "What Braintrust capability does this showcase?",
    header: "Focus",
    options: [
      { label: "LLM Evaluation", description: "Eval framework and metrics" },
      { label: "Prompt Engineering", description: "Prompt comparison and optimization" },
      { label: "Observability", description: "Logging and tracing" },
      { label: "A/B Testing", description: "Experiment tracking" }
    ]
  }
]
```

### 2. Validate Project Name

- Check if `projects/<project-name>/` already exists
- Validate name format (lowercase, hyphens only)
- Confirm with user if needed

### 3. Create Project Structure

```python
# Pseudocode
project_path = f"projects/{project_name}"

# Create directory
os.makedirs(project_path, exist_ok=False)

# Copy template files
copy_file("projects/template/.mise.toml", f"{project_path}/.mise.toml")
copy_file("projects/template/.env.example", f"{project_path}/.env.example")
copy_file("projects/template/README.md", f"{project_path}/README.md")
copy_file("projects/template/CLAUDE.md", f"{project_path}/CLAUDE.md")
```

### 4. Replace Template Placeholders

For each copied file, replace:

```python
replacements = {
    "[Project Name]": project_name.replace("-", " ").title(),
    "[project-name]": project_name,
    "[Brief description of what this project demonstrates]": user_description,
    "[Braintrust capability]": user_focus,
    "[description of the demo]": user_description.lower(),
    "[e.g., LLM Evaluation, Prompt Engineering, A/B Testing, etc.]": user_focus,
    "[Describe what this project demonstrates about Braintrust]": f"Demonstrates {user_focus} using Braintrust",
}

# For features, ask for 2-3 key patterns
# Replace [Feature/pattern 1], [Feature/pattern 2], etc.
```

### 5. Generate Project Files Based on Type

#### For Python Projects:

Create:
- `.mise.toml` (Python 3.12, UV)
- `pyproject.toml` with project name and dependencies
- `src/__init__.py`, `src/main.py`, `src/eval.py`
- `tests/__init__.py`, `tests/test_main.py`

#### For TypeScript Projects:

Create:
- `.mise.toml` (Node 20)
- `package.json` with project name
- `tsconfig.json`
- `src/index.ts`

#### For Fullstack:

Create:
- `.mise.toml` (Python + Node)
- `backend/` and `frontend/` directories
- Leave instructions for manual setup

### 6. Initialize Environment

```bash
cd projects/<project-name>
mise install
mise trust

# For Python
uv sync

# For TypeScript
npm install
```

### 7. Update Projects Index

Add entry to `projects/README.md`:

```markdown
### [Project Name](./project-name/)

**Type**: Python | TypeScript | Fullstack
**Focus**: [User's focus area]

[User's description]

Key features:
- [Feature 1]
- [Feature 2]

See [project README](./project-name/README.md) for details.
```

### 8. Provide Next Steps

Output to user:

```
✅ Project created successfully!

Location: projects/<project-name>

Next steps:
  cd projects/<project-name>
  cp .env.example .env
  # Add your Braintrust API key to .env

  [Type-specific run commands]

Your project is ready to use!
```

## Error Handling

- If project already exists: Ask if user wants to overwrite or choose different name
- If mise not installed: Provide installation instructions
- If template files missing: Alert and provide guidance

## Implementation Tips

1. Use `Glob` to check for existing projects
2. Use `Read` to get template contents
3. Use `Write` or `Edit` to create/modify files
4. Use `Bash` for mise/uv/npm commands
5. Keep user informed with progress updates
6. Handle errors gracefully with clear messages

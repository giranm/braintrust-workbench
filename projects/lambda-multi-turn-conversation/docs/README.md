# Development Documentation

This directory contains living documentation for the Lambda Multi Turn Conversation project.

## Files

### 📋 [planning.md](./planning.md)
**Read this first** before starting work.

Contains:
- Project goals and scope
- Technical approach and architecture
- Implementation plan and phases
- Success criteria and metrics
- Risks and mitigations

**When to use**: Before beginning implementation, when clarifying project direction

---

### 🔧 [implementation.md](./implementation.md)
**Update this during development.**

Contains:
- Implementation log (chronological entries)
- Architecture decisions and rationale
- Braintrust integration notes
- Code organization details
- Performance considerations

**When to use**: While coding, when making technical decisions, documenting progress

---

### 🐛 [issues.md](./issues.md)
**Check before starting, update when finding problems.**

Contains:
- Open issues and bugs
- Resolved issues with solutions
- Known limitations
- Technical debt items
- Troubleshooting notes

**When to use**: Before starting work (to avoid known issues), when encountering bugs, when resolving problems

---

### 📝 [changelog.md](./changelog.md)
**Update after completing features.**

Contains:
- Version history
- Notable changes
- Braintrust evaluation results
- Release notes

**When to use**: After completing features, when cutting releases, when tracking progress over time

---

## Documentation Workflow

### Before Starting Work
1. Read `planning.md` to understand goals and approach
2. Check `issues.md` for known problems and blockers
3. Review `implementation.md` for recent technical decisions

### During Development
1. Log decisions and progress in `implementation.md`
2. Document new issues in `issues.md`
3. Update architecture notes as design evolves

### After Completing Work
1. Update `changelog.md` with changes
2. Move resolved issues in `issues.md`
3. Update metrics/results in `planning.md` if applicable

---

## Why This Matters

✅ **Context Persists**: Documentation survives across sessions and team members
✅ **AI-Friendly**: Claude Code and other AI assistants can reference this context
✅ **Decision History**: Understand *why* choices were made, not just *what*
✅ **Onboarding**: New contributors can quickly understand the project
✅ **Debugging**: Past issues and solutions are documented

---

## Tips for Maintaining Docs

- **Be concise**: Clear and brief is better than verbose
- **Include dates**: Context about when decisions were made matters
- **Link to code**: Reference specific files and line numbers
- **Update continuously**: Don't wait until the end to document
- **Archive old content**: Move outdated sections to keep docs relevant

---

**Last Updated**: 2026-03-10
**Status**: Implemented

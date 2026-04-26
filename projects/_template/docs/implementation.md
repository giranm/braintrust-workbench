# Implementation Notes - [Project Name]

## Overview

This document tracks implementation decisions, technical notes, and progress during development.

**Last Updated**: [Date]

## Implementation Log

### [Date] - Initial Setup
- Created project structure
- Configured mise for [tools]
- Installed dependencies
- Set up environment

**Decisions**:
- [Key decision 1 and rationale]
- [Key decision 2 and rationale]

---

### [Date] - [Feature/Component Name]

**What was implemented**:
- [Description of work completed]

**Technical approach**:
- [How it was implemented]
- [Libraries/patterns used]

**Challenges encountered**:
- [Challenge 1]: [How it was resolved]
- [Challenge 2]: [How it was resolved]

**Code locations**:
- `src/[file.py]:[line]` - [Description]
- `src/[file.py]:[line]` - [Description]

**Testing**:
- [What tests were added]
- [How to verify it works]

**Decisions**:
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

---

## Architecture Decisions

### [Decision Title]

**Date**: [Date]
**Status**: Accepted | Proposed | Deprecated

**Context**:
[What is the issue we're trying to solve?]

**Decision**:
[What did we decide to do?]

**Consequences**:
- **Positive**: [Benefits of this decision]
- **Negative**: [Trade-offs or limitations]

**Alternatives Considered**:
1. **[Alternative 1]**: [Why not chosen]
2. **[Alternative 2]**: [Why not chosen]

---

## Braintrust Integration Notes

### Logging & Tracing
- **Implementation**: [How logging is set up]
- **Location**: `src/[file]:[line]`
- **Patterns used**: [Reference to cookbook/docs]

### Evaluations
- **Framework**: [How evals are structured]
- **Location**: `src/eval.py` or `tests/`
- **Metrics**: [What metrics are being tracked]
- **Scorers**: [Custom scorers if any]

### Datasets
- **Creation**: [How datasets are created/managed]
- **Location**: [Where datasets are stored/defined]
- **Format**: [Structure of data]

### Experiments
- **Setup**: [How experiments are configured]
- **Comparison**: [What is being compared]
- **Results**: [Reference to results or Braintrust dashboard]

---

## Code Organization

### Directory Structure
```
[project-name]/
├── src/
│   ├── [file1.py] - [Purpose]
│   ├── [file2.py] - [Purpose]
│   └── [file3.py] - [Purpose]
├── tests/
│   └── [test files and purpose]
└── docs/
    └── [documentation files]
```

### Key Modules

#### `src/[main.py]`
**Purpose**: [What this module does]

**Key functions**:
- `function_name()`: [Description]
- `function_name()`: [Description]

**Dependencies**: [What it imports/uses]

---

## Performance Considerations

### Optimization Notes
- [Optimization 1]: [What was done and impact]
- [Optimization 2]: [What was done and impact]

### Known Limitations
- [Limitation 1]: [Description and potential improvements]
- [Limitation 2]: [Description and potential improvements]

---

## Testing Strategy

### Unit Tests
- **Coverage**: [Coverage percentage or areas covered]
- **Location**: `tests/`
- **Run with**: `uv run pytest` or `pnpm test`

### Braintrust Evaluations
- **Eval suite**: [Description of eval approach]
- **Run with**: `uv run python src/eval.py`
- **Success criteria**: [What metrics indicate success]

### Manual Testing
- [Steps for manual testing]
- [Expected outcomes]

---

## Configuration

### Environment Variables
```bash
# Required
BRAINTRUST_API_KEY=xxx
OPENAI_API_KEY=xxx  # or other provider

# Optional
[OTHER_CONFIG]=xxx
```

### Mise Configuration
```toml
[tools]
python = "3.12"  # or node = "20"
```

**Why these versions**: [Rationale for tool versions]

---

## Dependencies

### Core Dependencies
- **braintrust**: [Version and why]
- **[library]**: [Version and why]

### Development Dependencies
- **pytest**: Testing framework
- **ruff**: Linting and formatting

### Adding Dependencies
```bash
# Python
uv add [package-name]

# TypeScript
pnpm add [package-name]
```

---

## Deployment Notes

[If applicable, notes on deploying or running in production]

---

## Future Improvements

### Potential Enhancements
- [ ] [Enhancement 1]
- [ ] [Enhancement 2]
- [ ] [Enhancement 3]

### Technical Debt
- [ ] [Tech debt item 1]
- [ ] [Tech debt item 2]

---

## Lessons Learned

### What Worked Well
- [Learning 1]
- [Learning 2]

### What Could Be Improved
- [Learning 1]
- [Learning 2]

### Best Practices
- [Practice 1]
- [Practice 2]

---

## References

### Braintrust Resources
- **Docs**: [Links to specific doc pages used]
- **Cookbook**: [Links to specific cookbook examples]

### External Resources
- [Other documentation, blog posts, papers, etc.]

---

**Maintained By**: [Your name or team]
**Last Updated**: [Date]

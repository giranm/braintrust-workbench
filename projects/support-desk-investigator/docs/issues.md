# Issues & Bugs - Support Desk Investigator

## Overview

This document tracks known issues, bugs, and their resolutions.

**Last Updated**: 2026-02-17

---

## Open Issues

_No open issues yet. Issues will be added as they are discovered during development._

---

## Resolved Issues

_No resolved issues yet. Resolved issues will be documented here as they are fixed._

---

## Braintrust-Specific Issues

### Evaluation Issues

_No evaluation issues yet._

### Logging/Tracing Issues

_No logging issues yet._

### Dataset Issues

_No dataset issues yet._

---

## Known Limitations

These are not bugs, but known limitations of the current implementation:

### Limitation 1: Single-Turn Conversations Only
**Description**: Agent processes one query at a time without conversation context
**Workaround**: For multi-turn scenarios, concatenate previous messages into context
**Future**: May add conversation state management in future versions

### Limitation 2: English Language Only
**Description**: Prompts and evaluations optimized for English text only
**Workaround**: None currently - use English support tickets
**Future**: Could add multi-language support with localized prompts and scorers

### Limitation 3: Synchronous LLM Calls
**Description**: No async/parallel processing for batch evaluation
**Workaround**: Acceptable for demo purposes with small datasets
**Future**: Could add async support for production use cases

---

## Technical Debt

Items that should be addressed to improve code quality:

_Technical debt will be tracked as the project develops._

---

## Performance Issues

_No performance issues yet._

---

## Environment Issues

### Dependency Conflicts

_No dependency conflicts yet._

### Setup Issues

_No setup issues yet._

---

## Testing Issues

### Test Failures

_No test failures yet._

### Coverage Gaps

Areas lacking sufficient test coverage:
- [ ] [To be identified after initial test suite is written]

---

## Issue Tracking Workflow

### For New Issues

1. Add issue to "Open Issues" section above
2. Assign priority and status
3. Document reproduction steps and impact
4. Update CLAUDE.md if needed for context

### For Resolved Issues

1. Move to "Resolved Issues" section
2. Document the resolution
3. Add tests to prevent regression
4. Update related documentation

### For Claude Code

When working on this project:
- **Check this file first** to understand known issues
- **Update this file** when encountering new issues
- **Document resolutions** when fixing issues
- **Reference issue numbers** in commit messages

---

## Quick Reference

### High Priority Open Issues
_None currently._

### Blockers
_None currently._

### Quick Wins
_None currently._

---

**Maintained By**: Braintrust Workbench
**Last Updated**: 2026-02-17

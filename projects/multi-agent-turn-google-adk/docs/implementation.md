# Implementation Notes - Multi Agent Turn Google ADK

## Overview

This document tracks implementation decisions, technical notes, and progress during development.

**Last Updated**: 2026-04-26

## Implementation Log

### 2026-04-26 - Initial Setup
- Created project structure from template
- Configured mise for Python 3.12 + UV
- Added `google-adk` and `braintrust` as core dependencies
- Set up environment variables for Braintrust, OpenAI, and Google API keys

**Decisions**:
- Using Google ADK as the multi-agent framework (project focus)
- Python-only project (ADK is Python-native)

---

## Architecture Decisions

### Google ADK for Agent Framework

**Date**: 2026-04-26
**Status**: Accepted

**Context**:
Need a multi-agent framework that supports turn-based orchestration with tool use.

**Decision**:
Use Google Agent Development Kit (ADK) as the primary agent framework.

**Consequences**:
- **Positive**: Native Python, well-documented, supports multi-agent patterns
- **Negative**: Tied to Google/Gemini ecosystem for model access

---

## Braintrust Integration Notes

### Logging & Tracing
- **Implementation**: TBD
- **Patterns used**: Multi-turn tracing similar to lambda-multi-turn-conversation project

### Evaluations
- **Framework**: TBD
- **Metrics**: Agent response quality, turn coherence, task completion

### Custom Scorers
- **Purpose**: Score multi-turn agent interactions
- **Approach**: TBD

---

## Code Organization

### Directory Structure
```
multi-agent-turn-google-adk/
├── src/
│   ├── __init__.py  - Package init
│   ├── main.py      - Main entry point
│   └── eval.py      - Braintrust evaluations (TBD)
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── docs/
```

---

## Dependencies

### Core Dependencies
- **braintrust**: Observability, evaluation, and scoring
- **google-adk**: Multi-agent orchestration framework

### Development Dependencies
- **pytest**: Testing framework
- **ruff**: Linting and formatting

---

**Maintained By**: Giran Moodley
**Last Updated**: 2026-04-26

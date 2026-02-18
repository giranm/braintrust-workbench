# Changelog - Support Desk Investigator

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- OpenTelemetry instrumentation and Braintrust integration (Day 5)
- Custom evaluation scorers and experiments (Day 6)
- Test dataset creation with record/replay fixtures
- Experiment tracking framework
- Connect to real Frappe API for ticket data
- Integrate real log aggregation system

---

## [0.2.1] - 2026-02-18

### Added - Local Embeddings & Idempotent Deployment
- Local sentence-transformers for embeddings (no external API dependencies)
- Automatic initialization system with backend entrypoint script
- Idempotent Qdrant ingestion (skips if data already exists)
- 20 sample incidents with proper incident IDs and resolved timestamps
- `scripts/backend-entrypoint.sh` for automated startup workflow
- `EMBEDDING_MODEL` environment variable configuration

### Changed
- **BREAKING**: Removed OpenAI dependency for embeddings
- Upgraded Qdrant from v1.7.4 to v1.16.3
- Vector dimensions: 1536 (OpenAI) → 384 (MiniLM-L6-v2)
- Qdrant now starts by default (removed from "tools" profile)
- Backend waits for Qdrant before starting
- Fixed Qdrant API usage: `query_points()` with proper `QueryResponse` handling

### Removed
- `openai` dependency from pyproject.toml
- `OPENAI_API_KEY` requirement for backend service
- Manual Qdrant ingestion step (now automatic)

### Technical Details
- Model: sentence-transformers/all-MiniLM-L6-v2 (~80MB, runs on CPU)
- Deployment: Fully idempotent, zero manual setup required
- Performance: ~20-50ms per embedding, ~10-30ms per search
- Architecture: Clear separation - local embeddings for tools, commercial LLM for reasoning

### Benefits
- Zero commercial API dependencies for vector search
- Automatic initialization on deployment
- Reproducible and idempotent setup
- Lower operational costs (no embedding API calls)

---

## [0.2.0] - 2026-02-18

### Changed - ADK Migration
- **BREAKING**: Migrated from custom workflow to Google Agent Development Kit (ADK)
- Replaced rule-based logic with LLM-driven reasoning using Claude 3.5 Sonnet
- Implemented SequentialAgent pattern with 4 specialized sub-agents:
  - TriageAgent: Categorizes tickets and determines investigation approach
  - GatherAgent: Collects evidence using 5 ADK function tools
  - VerifyAgent: Analyzes evidence and calculates confidence
  - FinalizeAgent: Generates customer replies and internal notes
- Created ADK function tools wrapping backend HTTP endpoints
- Maintained backward compatibility with existing HTTP interface

### Added
- `src/agent/adk_tools.py`: 5 ADK function tools for backend integration
- `src/agent/adk_workflow.py`: SequentialAgent-based investigation workflow
- `google-adk>=1.25.0` dependency in pyproject.toml
- `ADK_MODEL` environment variable configuration

### Deprecated
- `src/agent/workflow.py` → renamed to `workflow_legacy.py` for reference
- Custom 4-phase workflow (preserved for rollback if needed)

### Technical Details
- Model: claude-3-5-sonnet-20241022 (configurable via ADK_MODEL)
- State management: ADK automatically passes state between agents
- Tool binding: Function tools with rich docstrings for LLM context
- Investigation time: +2-5 seconds due to LLM latency
- Architecture: Aligns with original planning.md specification for ADK

### Migration Impact
- **Performance**: Increased latency (LLM calls) but improved reasoning quality
- **Maintainability**: Industry-standard agent framework vs custom logic
- **Observability**: ADK provides built-in tracing (prepares for Day 5)
- **Quality**: Natural language generation vs templates

---

## [0.1.0] - 2026-02-17

### Added
- Initial project setup and structure
- Python 3.12 environment with mise configuration
- UV-based dependency management
- Braintrust SDK integration (placeholder)
- Project documentation (CLAUDE.md, README.md)
- Development documentation templates (planning, implementation, issues, changelog)
- Environment configuration (.env.example)

### Documentation
- Created planning.md with project goals and implementation plan
- Created implementation.md for tracking technical decisions
- Created issues.md for bug and issue tracking
- Created README.md with quick start and usage guide

---

## Version History Notes

### [0.2.0] - [Future]

**Focus**: Core support agent and evaluation implementation

**Planned**:
- [ ] Support agent with LLM integration
- [ ] Braintrust logging for all LLM calls
- [ ] Custom scorers (quality, empathy, resolution)
- [ ] Test dataset with diverse support scenarios
- [ ] Basic experiment tracking

### [0.3.0] - [Future]

**Focus**: Enhanced evaluation and documentation

**Planned**:
- [ ] Expanded test dataset (20+ scenarios)
- [ ] Additional custom scorers
- [ ] A/B testing examples
- [ ] Performance optimizations
- [ ] Comprehensive examples and screenshots

---

## Braintrust Evaluation History

### Baseline Evaluation
**Date**: [TBD]
**Metrics**: [To be filled after first evaluation run]

---

## Links

- Project Repository: [Local workbench project]
- Braintrust Dashboard: https://www.braintrust.dev/app

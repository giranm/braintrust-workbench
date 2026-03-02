# Changelog - Multi Agent Chat Demo

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add evaluations for weather agent performance
- Add unit tests for weather tool
- Add conversation memory/history persistence
- Deploy to Reflex Cloud

---

## [0.2.1] - 2026-03-02

### Added
- **Docker Support**: Complete containerization for easy deployment
  - `Dockerfile` with multi-stage build (dev and prod targets)
  - `docker-compose.yml` for orchestration
  - `.dockerignore` for optimized builds
  - `Makefile` with 30+ convenience commands
  - Docker documentation integrated into README.md
- **Health Checks**: Container health monitoring
- **Volume Management**: Persistent storage for Reflex database
- **Development Workflow**: Hot-reload support in Docker containers

### Changed
- Updated README.md with Docker-first quick start
- Added Docker commands to all running instructions
- Updated project structure to include Docker files

### Technical Details
- **Base Image**: python:3.12-slim
- **Build Stages**: base → dev/prod (optimized)
- **Ports**: 3000 (frontend), 8000 (backend)
- **Volumes**: reflex-db for persistent state
- **User**: Non-root user in production image

---

## [0.1.0] - 2026-03-02

### Added
- Initial project setup
- Basic multi-agent architecture (Agent, Orchestrator)
- Braintrust logging and tracing integration
- Three example agents (Analyst, Writer, Reviewer)
- Multi-agent conversation workflow
- Basic evaluation framework
- Unit tests for core functionality

### Documentation
- Created planning.md
- Created implementation.md
- Created issues.md
- Created README.md

---

## [0.2.0] - 2026-03-02

### Added
- **Reflex Web UI**: Interactive chat interface for weather queries
- **Weather Tool**: Integration with Open-Meteo API for real-time weather data
  - `get_weather_for_city()`: Combined geocoding + weather fetch
  - `get_coordinates()`: City name to lat/lon conversion
  - `get_weather()`: Current weather data retrieval
  - `format_weather_response()`: Human-readable formatting
- **WeatherAgent**: Specialized agent with Anthropic tool calling
  - Automatic tool use detection
  - Multi-turn conversation support
  - Full Braintrust tracing of tool calls
- **Async HTTP**: httpx for non-blocking API calls
- **Component System**: Modular Reflex UI components
  - Chat message bubbles
  - Input area with send/clear buttons
  - Loading states and error handling

### Changed
- **Migrated from OpenAI to Anthropic**:
  - Using Claude Haiku 4.5 for cost-effectiveness ($1/MTok input, $5/MTok output)
  - Updated Agent class to use Anthropic Messages API
  - Replaced `OPENAI_API_KEY` with `ANTHROPIC_API_KEY`
- **Project Structure**: Organized code into agents/ and tools/ modules
- **Documentation**: Updated all docs to reflect new architecture

### Removed
- OpenAI dependency (replaced with Anthropic)

### Technical Details
- **LLM Model**: claude-haiku-4-5-20251001
- **Weather API**: Open-Meteo (free, no API key required)
- **Frontend Framework**: Reflex 0.8.27
- **Tracing**: All components use `@traced` decorator

---

## Braintrust Evaluation History

### Baseline Evaluation
**Date**: [Date]
**Metrics**:
- [Metric 1]: [Score]
- [Metric 2]: [Score]

### [Experiment Name]
**Date**: [Date]
**Changes**: [What was changed]
**Metrics**:
- [Metric 1]: [Score] (Δ [change])
- [Metric 2]: [Score] (Δ [change])

**Conclusion**: [What was learned]

---

## Links

- [Compare Unreleased](https://github.com/...)
- [View 0.1.0](https://github.com/...)

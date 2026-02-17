# Planning - Support Desk Investigator

## Overview

**Project**: Support Desk Investigator
**Type**: Python
**Focus**: Observability & Evaluations
**Status**: Planning

## Goals

### Primary Goal
Demonstrate how to use Braintrust for comprehensive observability and evaluation of LLM-powered support desk agents, enabling teams to monitor, debug, and continuously improve support quality.

### Secondary Goals
- [ ] Show how to build custom evaluation metrics for support scenarios
- [ ] Demonstrate dataset management for consistent evaluation
- [ ] Illustrate experiment tracking for A/B testing and optimization
- [ ] Provide a clear template for production support agent monitoring

## Scope

### In Scope
- LLM-powered support ticket response generation
- Full observability with Braintrust logging and tracing
- Custom scorers for support quality (accuracy, empathy, resolution)
- Test dataset creation and management
- Experiment framework for comparing prompts/models
- Example support scenarios (billing, technical, general inquiries)

### Out of Scope
- Production deployment infrastructure
- Multi-turn conversations (focus on single responses)
- Integration with actual ticketing systems (Zendesk, etc.)
- Advanced RAG or knowledge base integration

## Braintrust Integration

### Capabilities to Demonstrate
- [ ] Logging and tracing all LLM interactions
- [ ] Custom scorer development for domain-specific metrics
- [ ] Dataset creation and versioning for evaluation
- [ ] Experiment tracking and comparison
- [ ] Dashboard visualization of metrics and traces

### Reference Materials
- **Docs**: [Logging Guide](https://www.braintrust.dev/docs/guides/logging)
- **Docs**: [Custom Scorers](https://www.braintrust.dev/docs/guides/evals#custom-scorers)
- **Docs**: [Datasets](https://www.braintrust.dev/docs/guides/datasets)
- **Cookbook**: [LLM Evaluation Examples](https://github.com/braintrustdata/braintrust-cookbook)
- **Patterns**: Eval-driven development, observability-first design

## Technical Approach

### Architecture
Simple support agent that:
1. Receives a support ticket (text input)
2. Processes with LLM (OpenAI/Anthropic)
3. Logs interaction to Braintrust for observability
4. Returns response with metadata

Evaluation framework that:
1. Loads test dataset of support scenarios
2. Runs agent on each scenario
3. Scores responses with custom metrics
4. Tracks results as Braintrust experiments

### Key Components
1. **Support Agent** (`src/main.py`): Core LLM agent with Braintrust logging
2. **Evaluation Suite** (`src/eval.py`): Custom scorers and eval framework
3. **Test Dataset**: Sample support tickets with expected criteria
4. **Experiments**: Comparison of different prompts/models/parameters

### Data Flow
1. User query → Support Agent
2. Agent → LLM API (with context/prompt)
3. LLM response → Braintrust logging
4. Response → Quality scoring (custom metrics)
5. Scores → Braintrust experiment tracking

### Dependencies
```
# Python
braintrust           # Core observability and evaluation
openai               # LLM provider (can swap for anthropic, etc.)
python-dotenv        # Environment management
pytest               # Testing framework
ruff                 # Linting and formatting
```

## Implementation Plan

### Phase 1: Setup
- [x] Initialize project structure
- [x] Configure mise environment
- [x] Create pyproject.toml with dependencies
- [ ] Set up environment variables
- [ ] Install dependencies with uv

### Phase 2: Core Implementation
- [ ] Build basic support agent with LLM integration
- [ ] Add prompt engineering for support scenarios
- [ ] Implement basic response generation
- [ ] Add error handling and validation

### Phase 3: Braintrust Integration
- [ ] Set up Braintrust logging for all LLM calls
- [ ] Create custom scorers (accuracy, empathy, resolution)
- [ ] Build test dataset with sample support tickets
- [ ] Implement evaluation framework in `src/eval.py`
- [ ] Set up experiment tracking

### Phase 4: Testing & Documentation
- [ ] Write unit tests for agent logic
- [ ] Create comprehensive eval suite
- [ ] Document usage in README
- [ ] Add example outputs and screenshots
- [ ] Update implementation.md with technical notes

## Success Criteria

### Functional Requirements
- [ ] Agent successfully responds to support tickets
- [ ] All LLM interactions logged to Braintrust
- [ ] Custom scorers evaluate responses on 3+ metrics
- [ ] Test dataset with 10+ diverse support scenarios
- [ ] Experiments compare at least 2 variants

### Braintrust Evaluation Metrics
- **Response Quality**: Target threshold ≥ 0.80
- **Tone & Empathy**: Target threshold ≥ 0.85
- **Resolution Score**: Target threshold ≥ 0.75

### Documentation Requirements
- [ ] README with clear quick start
- [ ] Code comments for key logic
- [ ] Architecture documented in implementation.md
- [ ] Braintrust setup clearly explained

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Custom scorers too complex/subjective | Medium | Medium | Use clear rubrics, reference cookbook examples |
| Dataset too small/biased | Medium | High | Create diverse scenarios, include edge cases |
| LLM API costs for evaluation | Low | Medium | Use smaller dataset for demos, cache when possible |
| Braintrust API changes | Low | Low | Pin SDK versions, follow official docs |

## Timeline

- **Planning**: 2026-02-17
- **Implementation**: 2026-02-17 to 2026-02-18
- **Testing**: 2026-02-18
- **Documentation**: 2026-02-18
- **Completion**: 2026-02-19

## Notes

This project prioritizes clarity and educational value over production-readiness. The goal is to showcase Braintrust capabilities in a realistic but simplified support desk scenario.

Key considerations:
- Keep prompts simple and well-documented
- Make scorers transparent and explainable
- Provide diverse test scenarios (billing, technical, general)
- Show clear before/after comparisons in experiments

## References

- Braintrust Docs: https://www.braintrust.dev/docs
- Braintrust Cookbook: https://github.com/braintrustdata/braintrust-cookbook
- LLM Evaluation Best Practices: https://www.braintrust.dev/docs/guides/evals#best-practices

---

**Last Updated**: 2026-02-17
**Status**: Planning

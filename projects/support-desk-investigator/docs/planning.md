# Planning - Support Desk Investigator

## Overview
**Project**: Support Desk Investigator  
**Type**: Python + Docker Compose  
**Focus**: Multi-step agent + tool calls + eval-driven improvement  
**Ticketing**: Frappe Helpdesk  
**Agent SDK**: Google ADK  
**Tracing**: OpenTelemetry → Braintrust  

---

## Goals

### Primary Goal
Build a support-ticket auto-investigator that demonstrates:
- multi-step agent workflows (planning + tool calls + verification)
- full OpenTelemetry traces visible in Braintrust
- eval-driven iteration with clear before/after improvements

### Secondary Goals
- Use mostly open-source infrastructure
- Run the entire demo locally with Docker Compose
- Support multiple LLM providers (OpenAI / Anthropic)

---

## Target Stack
- Ticketing: **Frappe Helpdesk**
- Agent orchestration: **Google Agent SDK (ADK)**
- LLM providers: **OpenAI / Anthropic**
- Retrieval: **Qdrant**
- Tracing: **OpenTelemetry → Braintrust**
- Runtime: **Docker + Compose**

---

## Core User Stories

### Ticket-to-Answer
When a new ticket arrives, the system should:
1. triage the issue
2. pull context (customer, deploys, similar incidents)
3. query logs for evidence
4. produce:
   - customer reply draft
   - internal notes (root cause hypothesis + evidence + next actions)
   - confidence + escalation guidance

### Bad → Good Improvement
As a developer, I want to:
- find poor outputs in traces
- convert them into a regression dataset
- add scorers + workflow changes
- re-run experiments and prove improvement

---

## Milestones

### Phase 1 — End-to-end demo loop (MVP) ✅ COMPLETE (v0.3.0)
- ✅ Frappe Helpdesk running in Compose
- ✅ Backend receives webhook events
- ✅ ADK agent invoked and produces a response
- ✅ Response posted back into ticket (internal notes + customer communication)
- ✅ Service accounts and demo customer configured
- ⏳ OpenTelemetry spans visible in Braintrust (Day 6 - next)

### Phase 2 — Add tools + retrieval ✅ COMPLETE (v0.3.0)
- ✅ Qdrant populated with sample incidents (20 samples)
- ✅ Agent uses incident retrieval tool via ADK
- ✅ Log querying tool (demo mode with mock data)
- ✅ Deploy history tool
- ✅ Customer context tool
- ✅ Evidence bundle included in outputs

### Phase 3 — Evals + variants 🚧 IN PROGRESS
- ⏳ Introduce `VARIANT=baseline` and `VARIANT=improved` (Day 7 - planned)
- ⏳ Record/replay tool outputs for deterministic runs (planned)
- ⏳ Add scorers (planned):
  - schema + evidence grounding
  - tool-call requirements
  - helpfulness/tone
  - escalation correctness

---

## Demo Plan (recommended)
1. Create 2–3 seeded tickets in Frappe
2. Run baseline and show:
   - wrong triage
   - no evidence
   - hallucinated root cause
3. Switch to improved and show:
   - correct tool usage
   - evidence citations
   - structured response + confidence gating
4. Show eval deltas in Braintrust

---

## Scope

### In Scope
- Frappe Helpdesk webhooks + API integration
- ADK agent workflow + tool bindings
- Qdrant retrieval
- OpenTelemetry tracing exported to Braintrust
- Offline eval pipeline + variants

### Out of Scope (for initial demo)
- Production auth/SSO
- Multi-tenant ticketing
- Full incident management system
- High-scale infra
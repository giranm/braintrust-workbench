# Issues & Limitations - Support Desk Investigator

**Last Updated**: 2026-02-17

---

## Open Issues

### 1) Webhook payload completeness
Frappe webhooks may not contain full ticket context.
Plan: store ticket id and fetch details via Frappe API.

### 2) Determinism for demos
Tool outputs and retrieval can introduce nondeterminism.
Plan: implement record/replay mode for tool calls and set model temperature=0.

### 3) Trace propagation across services
Backend → agent call must preserve trace context.
Plan: propagate trace headers explicitly.

---

## Known Limitations (acceptable for demo)
- simplified customer + deploy context (may be mocked)
- English-only prompts/evals
- single-ticket investigations (no long-running incident room)
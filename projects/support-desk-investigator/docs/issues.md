# Issues & Limitations - Support Desk Investigator

**Last Updated**: 2026-02-20

---

## Open Issues

### 1) Determinism for demos
Tool outputs and retrieval can introduce nondeterminism.
Plan: implement record/replay mode for tool calls and set model temperature=0.

### 2) Trace propagation across services
Backend → agent call must preserve trace context.
Plan: propagate trace headers explicitly with OpenTelemetry (Day 6).

### 3) Tag creation in Frappe
Tags require Tag doctype to exist first. Currently failing with "Could not find Document Tag: auto-investigated".
**Workaround**: Tags are logged but failures don't block the workflow.
**Plan**: Pre-create tags during initialization or handle gracefully.

### 4) Ticket attribution
Tickets created via API always set `raised_by` to the authenticated user (Administrator).
**Impact**: Demo tickets show admin@example.com instead of customer email in activity feed.
**Workaround**: Tickets created via Frappe UI properly show customer attribution.
**Plan**: For demos, create tickets via UI or document that webhook payload would contain proper customer context in production.

---

## Resolved Issues

### ✅ Webhook payload completeness (Resolved 2026-02-20)
- **Issue**: Frappe webhooks may not contain full ticket context
- **Solution**: Implemented full Frappe API integration with CaseFile normalization
- **Status**: Backend normalizes webhook payload and can fetch additional details if needed

### ✅ Customer portal visibility (Resolved 2026-02-20)
- **Issue**: Customer communications not appearing in portal view
- **Solution**: Use Communication doctype with `communication_medium: "Email"`
- **Status**: Customer-facing responses now visible at /helpdesk/tickets/{id}

### ✅ Message attribution (Resolved 2026-02-20)
- **Issue**: Communications showing "No name found" as sender
- **Solution**: Created "Helpdesk Assistant" service account and set sender/sender_full_name fields
- **Status**: All automated responses properly attributed to "Helpdesk Assistant"

---

## Known Limitations (acceptable for demo)
- Simplified customer + deploy context (may be mocked)
- English-only prompts/evals
- Single-ticket investigations (no long-running incident room)
- Tag creation requires pre-existing Tag doctypes in Frappe
- Service accounts created via initialization script (not via Frappe UI)
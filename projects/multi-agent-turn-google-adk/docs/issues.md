# Issues & Bugs - Multi Agent Turn Google ADK

## Overview

This document tracks known issues, bugs, and their resolutions.

**Last Updated**: 2026-04-27

---

## Open Issues

No open issues.

---

## Resolved Issues

### Issue #1: `logger.flush()` is not async

**Status**: Resolved
**Date**: 2026-04-26

**Description**: `await logger.flush()` raised `TypeError: 'NoneType' object can't be awaited`.

**Resolution**: `braintrust.Logger.flush()` is synchronous. Call without `await`.

### Issue #2: Order IDs passed with `#` prefix

**Status**: Resolved
**Date**: 2026-04-26

**Description**: LLMs pass `#12345` from user input, but mock tools only match `12345`.

**Resolution**: Added `_normalize_id()` to strip `#` prefix in all tool functions.

### Issue #3: `braintrust push` unsupported on Python 3.14

**Status**: Resolved (workaround)
**Date**: 2026-04-26

**Description**: `braintrust push` bundles code for server-side execution and rejects Python 3.14.

**Resolution**: Use `uvx --python 3.12` in Makefile to run push in an isolated Python 3.12 environment.

### Issue #4: Python SDK double-serializes `tools` on prompts

**Status**: Resolved (workaround)
**Date**: 2026-04-26

**Description**: `project.prompts.create(tools=[...])` stores the tools array as a JSON string instead of a proper array, causing the Braintrust UI not to render tool references.

**Resolution**: Publish prompts without tools via SDK, then PATCH `prompt_data.prompt.tools` as a JSON string via REST API (`PUT /v1/function/{id}`). The API expects `tools` as a serialized string.

### Issue #5: LLM scorers fail with "Missing required parameter: messages"

**Status**: Resolved
**Date**: 2026-04-27

**Description**: Online LLM-as-Judge scorers (`response_helpfulness`) failed when Braintrust ran them server-side. The OpenAI API returned `missing_required_parameter: messages`.

**Root cause**: Scorers were registered with `prompt=` (raw string) instead of `messages=[{"role": "user", "content": ...}]`. The `prompt` format doesn't produce a valid `messages` array for the OpenAI API.

**Resolution**: Changed `setup_managed.py` to use `messages=[{"role": "user", "content": config["prompt"]}]` when registering LLM scorers.

---

## Known Limitations

### Limitation 1: `braintrust push` requires Python <= 3.13

Braintrust's server-side runtime doesn't support Python 3.14. The Makefile uses `uvx --python 3.12` as a workaround for pushing code functions. This adds latency to `make setup-managed`.

### Limitation 2: Tool-prompt linking requires REST API workaround

The Python SDK's `project.prompts.create(tools=[...])` double-serializes the tools array. Prompt-to-tool linking must be done via REST API PATCH after SDK publish.

### Limitation 3: `response_format` code scorer runs server-side with 6-8s latency

The code-based `response_format` scorer takes 6-8 seconds in online scoring despite being a simple string check. This is server-side execution overhead, not scorer logic.

---

**Maintained By**: Giran Moodley
**Last Updated**: 2026-04-27

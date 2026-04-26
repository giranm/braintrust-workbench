"""Push datasets, prompts, and tools to Braintrust as managed objects.

Idempotent — safe to re-run. Tools are created via REST API as schema-only
definitions, then prompts are published with tool references via the SDK.

Run via:
    uv run python src/setup_managed.py
    # or
    make setup-managed
"""

import json
import os
import pathlib
import sys

import braintrust
import requests
from pydantic import BaseModel, Field

from src.prompts import AGENT_PROMPTS

BRAINTRUST_PROJECT = os.environ.get("BRAINTRUST_PROJECT", "multi-agent-turn-google-adk")
DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "eval_scenarios.json"


# ---------------------------------------------------------------------------
# Tool schemas (Pydantic models → JSON Schema for Braintrust)
# ---------------------------------------------------------------------------


class LookupOrderInput(BaseModel):
    order_id: str = Field(description="The order ID to look up")


class CancelOrderInput(BaseModel):
    order_id: str = Field(description="The order ID to cancel")
    reason: str = Field(description="Reason for cancellation")


class ProcessRefundInput(BaseModel):
    order_id: str = Field(description="The order ID to refund")
    amount: float = Field(description="Refund amount in dollars")


class GetInvoiceInput(BaseModel):
    order_id: str = Field(description="The order ID to retrieve the invoice for")


class SearchFaqInput(BaseModel):
    query: str = Field(description="Search query for the FAQ knowledge base")


# Tool definitions: (name, slug, schema_class, description)
TOOL_DEFS = [
    ("lookup_order", "lookup-order", LookupOrderInput,
     "Look up an order by its ID. Returns order status, tracking URL, ETA, items, and total."),
    ("cancel_order", "cancel-order", CancelOrderInput,
     "Cancel an order. Only orders that are still processing can be cancelled."),
    ("process_refund", "process-refund", ProcessRefundInput,
     "Process a refund for an order. Returns a confirmation with a reference number."),
    ("get_invoice", "get-invoice", GetInvoiceInput,
     "Retrieve the invoice for an order, including line items and a PDF link."),
    ("search_faq", "search-faq", SearchFaqInput,
     "Search the FAQ knowledge base. Returns the top 3 matching entries."),
]

# Agent → tool slug mapping
AGENT_TOOLS = {
    "router_agent": [],
    "order_agent": ["lookup-order", "cancel-order"],
    "billing_agent": ["process-refund", "get-invoice"],
    "faq_agent": ["search-faq"],
}


# ---------------------------------------------------------------------------
# REST API helper for creating tool definitions
# ---------------------------------------------------------------------------


def _get_api_headers():
    api_key = os.environ.get("BRAINTRUST_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _get_project_id(project_name: str) -> str:
    """Look up project ID by name."""
    resp = requests.get(
        "https://api.braintrust.dev/v1/project",
        headers=_get_api_headers(),
        params={"project_name": project_name},
    )
    resp.raise_for_status()
    data = resp.json()
    objects = data.get("objects", [])
    for obj in objects:
        if obj.get("name") == project_name:
            return obj["id"]
    raise ValueError(f"Project '{project_name}' not found")


def _upsert_tool(project_id: str, name: str, slug: str, description: str, schema_class) -> str:
    """Add parameter schema to an existing tool, or create one if it doesn't exist.

    When braintrust push has already created the tool (with code), this
    PATCHes the schema onto it without overwriting the code data.
    """
    json_schema = schema_class.model_json_schema()

    # Check if tool already exists (e.g. from braintrust push)
    existing = requests.get(
        "https://api.braintrust.dev/v1/function",
        headers=_get_api_headers(),
        params={"project_id": project_id, "slug": slug, "function_type": "tool"},
    )
    existing.raise_for_status()
    objects = existing.json().get("objects", [])

    if objects:
        # PATCH schema onto existing tool (preserves code data from push)
        func_id = objects[0]["id"]
        resp = requests.patch(
            f"https://api.braintrust.dev/v1/function/{func_id}",
            headers=_get_api_headers(),
            json={
                "name": name,
                "description": description,
                "function_schema": {"parameters": json_schema},
            },
        )
        resp.raise_for_status()
        return func_id
    else:
        # Create new (schema-only, no code)
        resp = requests.post(
            "https://api.braintrust.dev/v1/function",
            headers=_get_api_headers(),
            json={
                "project_id": project_id,
                "name": name,
                "slug": slug,
                "description": description,
                "function_type": "tool",
                "function_data": {"type": "prompt"},
                "function_schema": {"parameters": json_schema},
            },
        )
        resp.raise_for_status()
        return resp.json().get("id", "")


# ---------------------------------------------------------------------------
# Setup functions
# ---------------------------------------------------------------------------


def setup_dataset() -> None:
    """Upload eval scenarios as a managed golden dataset."""
    print("Uploading dataset: eval-scenarios")

    dataset = braintrust.init_dataset(
        project=BRAINTRUST_PROJECT,
        name="eval-scenarios",
        description="Golden evaluation scenarios for multi-agent customer support demo",
    )

    with open(DATA_PATH) as f:
        scenarios = json.load(f)

    for i, scenario in enumerate(scenarios):
        dataset.insert(
            input=scenario["input"],
            expected=scenario["expected"],
            metadata={"scenario_index": i},
        )

    dataset.flush()
    print(f"  Uploaded {len(scenarios)} scenarios")


def setup_tools(project_id: str) -> dict[str, str]:
    """Create tool definitions via REST API. Returns slug → id mapping."""
    print("Registering tools:")
    tool_ids = {}
    for name, slug, schema_class, description in TOOL_DEFS:
        try:
            tool_id = _upsert_tool(project_id, name, slug, description, schema_class)
            tool_ids[slug] = tool_id
            print(f"  {name} -> {slug}")
        except Exception as e:
            print(f"  {name}: failed ({e})", file=sys.stderr)
    return tool_ids


def setup_prompts(project_id: str, tool_ids: dict[str, str]) -> None:
    """Register agent prompts with tool references via SDK.

    Uses OpenAI function-calling format for the tools parameter, where
    function.name matches the tool slug. This is what Braintrust uses
    to link tools to prompts in the UI.
    """
    print("Registering prompts:")

    # Build a lookup: slug → (description, json_schema) for inline tool defs
    tool_schemas = {}
    for name, slug, schema_class, description in TOOL_DEFS:
        tool_schemas[slug] = {
            "description": description,
            "parameters": schema_class.model_json_schema(),
        }

    project = braintrust.projects.create(BRAINTRUST_PROJECT)

    for agent_name, prompt_def in AGENT_PROMPTS.items():
        agent_tool_slugs = AGENT_TOOLS.get(agent_name, [])

        # Build OpenAI function-calling tool definitions
        # function.name = tool slug → Braintrust links them in the UI
        openai_tools = []
        for slug in agent_tool_slugs:
            if slug in tool_schemas:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": slug,
                        "description": tool_schemas[slug]["description"],
                        "parameters": tool_schemas[slug]["parameters"],
                    },
                })

        # Strip LiteLLM provider prefix (e.g. "anthropic/claude-haiku-4-5" → "claude-haiku-4-5")
        model = prompt_def["model"]
        if "/" in model:
            model = model.split("/", 1)[1]

        prompt_kwargs = dict(
            name=agent_name,
            slug=prompt_def["slug"],
            description=prompt_def["description"],
            messages=[{"role": "system", "content": prompt_def["instruction"]}],
            model=model,
            params={"temperature": 0},
            if_exists="replace",
        )
        # Tools are linked via REST API PATCH after publish (SDK double-serializes them)
        project.prompts.create(**prompt_kwargs)
        tool_info = f" (tools: {', '.join(agent_tool_slugs)})" if agent_tool_slugs else ""
        print(f"  {agent_name} -> {prompt_def['slug']}{tool_info}")

    # Publish prompts first (without tools — SDK double-serializes them)
    print("Publishing prompts...")
    project.publish()

    # Then PATCH tools onto prompts via REST API (correct JSON format)
    print("Linking tools to prompts via API...")
    for agent_name, prompt_def in AGENT_PROMPTS.items():
        agent_tool_slugs = AGENT_TOOLS.get(agent_name, [])
        if not agent_tool_slugs:
            continue

        openai_tools = []
        for slug in agent_tool_slugs:
            if slug in tool_schemas:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": slug,
                        "description": tool_schemas[slug]["description"],
                        "parameters": tool_schemas[slug]["parameters"],
                    },
                })

        # Look up prompt by slug
        resp = requests.get(
            "https://api.braintrust.dev/v1/function",
            headers=_get_api_headers(),
            params={"project_id": project_id, "slug": prompt_def["slug"]},
        )
        resp.raise_for_status()
        objects = resp.json().get("objects", [])
        if not objects:
            continue

        prompt_obj = objects[0]
        prompt_data = prompt_obj.get("prompt_data", {})
        prompt_section = prompt_data.get("prompt", {})
        prompt_section["tools"] = openai_tools

        # API expects tools as a JSON string, not an array
        prompt_section["tools"] = json.dumps(openai_tools)

        resp = requests.patch(
            f"https://api.braintrust.dev/v1/function/{prompt_obj['id']}",
            headers=_get_api_headers(),
            json={"prompt_data": {**prompt_data, "prompt": prompt_section}},
        )
        resp.raise_for_status()
        print(f"  {prompt_def['slug']}: linked {len(openai_tools)} tools")


def setup_scorers() -> None:
    """Register LLM-as-Judge scorers as managed objects."""
    from src.scorers import LLM_SCORER_CONFIGS

    print("Registering LLM scorers:")

    project = braintrust.projects.create(BRAINTRUST_PROJECT)

    for config in LLM_SCORER_CONFIGS:
        project.scorers.create(
            name=config["name"],
            slug=config["slug"],
            description=config["description"],
            messages=[{"role": "user", "content": config["prompt"]}],
            model=config["model"],
            use_cot=config["use_cot"],
            choice_scores=config["choice_scores"],
            if_exists="replace",
        )
        print(f"  {config['name']} -> {config['slug']}")

    project.publish()


def _resolve_scorer_ref(project_id: str, slug: str) -> dict | None:
    """Look up a scorer by slug and return a versioned function reference."""
    resp = requests.get(
        "https://api.braintrust.dev/v1/function",
        headers=_get_api_headers(),
        params={"project_id": project_id, "slug": slug, "function_type": "scorer"},
    )
    resp.raise_for_status()
    objects = resp.json().get("objects", [])
    if not objects:
        return None
    obj = objects[0]
    return {"type": "function", "id": obj["id"], "version": obj["_xact_id"]}


# Online scoring rule definitions
ONLINE_RULES = [
    {
        "name": "Agent Response Quality",
        "description": "Score every agent turn span for format quality and helpfulness (100% sampling).",
        "scorer_slugs": ["response-format", "response-helpfulness"],
        "scope": {"type": "span"},
        "apply_to_span_names": [
            "turn:router_agent",
            "turn:order_agent",
            "turn:billing_agent",
            "turn:faq_agent",
        ],
        "btql_filter": "span_attributes.type = 'task'",
    },
    {
        "name": "Conversation Resolution",
        "description": "Score every full conversation trace for issue resolution (100% sampling).",
        "scorer_slugs": ["conversation-resolution"],
        "scope": {"type": "trace"},
        "btql_filter": None,
    },
]


def setup_online_rules(project_id: str) -> None:
    """Configure online scoring rules via PUT /v1/project_score."""
    print("Configuring online scoring rules:")

    for rule in ONLINE_RULES:
        # Resolve scorer slugs to versioned function refs
        scorer_refs = []
        for slug in rule["scorer_slugs"]:
            ref = _resolve_scorer_ref(project_id, slug)
            if ref:
                scorer_refs.append(ref)
            else:
                print(f"  WARNING: scorer '{slug}' not found, skipping", file=sys.stderr)

        if not scorer_refs:
            print(f"  {rule['name']}: no scorers resolved, skipping")
            continue

        # Build the online config
        online_config = {
            "sampling_rate": 1,  # 100%
            "scorers": scorer_refs,
            "scope": rule["scope"],
        }

        if rule.get("apply_to_span_names"):
            online_config["apply_to_span_names"] = rule["apply_to_span_names"]

        if rule.get("btql_filter"):
            online_config["btql_filter"] = rule["btql_filter"]

        payload = {
            "project_id": project_id,
            "name": rule["name"],
            "description": rule["description"],
            "score_type": "online",
            "config": {"online": online_config},
        }

        resp = requests.put(
            "https://api.braintrust.dev/v1/project_score",
            headers=_get_api_headers(),
            json=payload,
        )
        resp.raise_for_status()
        scorer_names = ", ".join(rule["scorer_slugs"])
        scope_type = rule["scope"]["type"]
        print(f"  {rule['name']} ({scope_type}-level, 100%): {scorer_names}")


def main() -> None:
    if not os.environ.get("BRAINTRUST_API_KEY"):
        print("Error: BRAINTRUST_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    print(f"Setting up managed objects for project: {BRAINTRUST_PROJECT}")
    print("=" * 50)

    # 1. Dataset
    setup_dataset()
    print()

    # 2. Tools (via REST API — must exist before prompts reference them)
    project_id = _get_project_id(BRAINTRUST_PROJECT)
    tool_ids = setup_tools(project_id)
    print()

    # 3. Prompts with tool references (via SDK)
    setup_prompts(project_id, tool_ids)
    print()

    # 4. LLM-as-Judge scorers (via SDK)
    setup_scorers()
    print()

    # 5. Online scoring rules (via REST API)
    setup_online_rules(project_id)
    print()

    print(f"View in Braintrust: https://www.braintrust.dev/app/{BRAINTRUST_PROJECT}")
    print()
    print("Verify with bt CLI:")
    print(f"  bt prompts list -p {BRAINTRUST_PROJECT}")
    print(f"  bt tools list -p {BRAINTRUST_PROJECT}")
    print(f"  bt scorers list -p {BRAINTRUST_PROJECT}")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    main()

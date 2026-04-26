"""Offline evaluation suite using Braintrust Eval().

Run with:
    uv run braintrust eval src/eval.py
"""

import asyncio
import json
import os
import pathlib

import braintrust

from src.orchestrator import BRAINTRUST_PROJECT, create_session, send_message
from src.scorers import routing_accuracy, task_completion, tool_selection

DATA_PATH = pathlib.Path(__file__).parent.parent / "data" / "eval_scenarios.json"


def load_eval_data() -> list[dict]:
    """Load multi-turn evaluation scenarios from JSON."""
    with open(DATA_PATH) as f:
        return json.load(f)


async def run_scenario(scenario: dict) -> dict:
    """Run a single eval scenario through the orchestrator and return the output."""
    session_id = await create_session(user_id="eval")
    responses = []

    for turn in scenario["turns"]:
        response = await send_message(
            session_id=session_id,
            message=turn["user_message"],
            user_id="eval",
        )
        responses.append(response)

    return {
        "final_response": responses[-1] if responses else "",
        "all_responses": responses,
    }


async def eval_task(input: dict, hooks: braintrust.EvalHooks) -> str:
    """Braintrust eval task function."""
    result = await run_scenario(input)
    hooks.meta(
        agent=input.get("expected_agent", ""),
        tools_called=input.get("expected_tools", []),
    )
    return result["final_response"]


braintrust.Eval(
    name=os.environ.get("BRAINTRUST_PROJECT", BRAINTRUST_PROJECT),
    data=load_eval_data,
    task=eval_task,
    scores=[routing_accuracy, tool_selection, task_completion],
)

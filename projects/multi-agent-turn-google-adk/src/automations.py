"""Provision Braintrust online scoring automations.

Registers LLM-graded scorers in the Braintrust project so they run
automatically against production-logged spans. Uses the framework2
Project + ScorerBuilder API and `braintrust push`.

Run via:
    uv run python src/automations.py
    # or
    make setup-automations
"""

import os
import sys

import braintrust

from src.scorers import LLM_SCORER_CONFIGS

BRAINTRUST_PROJECT = os.environ.get("BRAINTRUST_PROJECT", "multi-agent-turn-google-adk")


def setup_automations() -> None:
    """Register LLM scorers in the Braintrust project."""
    try:
        project = braintrust.projects.create(BRAINTRUST_PROJECT, if_exists="return")
    except Exception as e:
        print(f"Error connecting to Braintrust: {e}", file=sys.stderr)
        print("Make sure BRAINTRUST_API_KEY is set.", file=sys.stderr)
        sys.exit(1)

    print(f"Provisioning scorers for project: {BRAINTRUST_PROJECT}")

    for config in LLM_SCORER_CONFIGS:
        try:
            scorer = project.scorers.create(
                name=config["name"],
                prompt=config["prompt"],
                model=config["model"],
                use_cot=config["use_cot"],
                choice_scores=config["choice_scores"],
                if_exists="replace",
            )
            print(f"  Registered scorer: {config['name']}")
        except Exception as e:
            print(f"  Failed to register scorer {config['name']}: {e}", file=sys.stderr)

    print()
    print("Scorers registered. Enable online scoring in the Braintrust dashboard:")
    print(f"  https://www.braintrust.dev/app/{BRAINTRUST_PROJECT}/settings")
    print()
    print("To deploy as functions, run:")
    print("  uv run braintrust push src/automations.py")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if not os.environ.get("BRAINTRUST_API_KEY"):
        print("Error: BRAINTRUST_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    setup_automations()

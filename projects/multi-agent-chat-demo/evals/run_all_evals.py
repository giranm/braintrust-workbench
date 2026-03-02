#!/usr/bin/env python3
"""
Run all evaluation suites for weather chat.

This script runs:
1. Single-turn conversation evaluation
2. Multi-turn conversation evaluation

Run with: uv run python evals/run_all_evals.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "multi-agent-chat-demo")


def run_evaluation(script_name: str, description: str):
    """Run a single evaluation script."""
    print(f"\n{'=' * 60}")
    print(f"Running {description}")
    print(f"{'=' * 60}")

    try:
        # Import and run the evaluation
        if script_name == "weather_conversation":
            from . import weather_conversation
            weather_conversation.main()
        elif script_name == "multi_turn_conversation":
            from . import multi_turn_conversation
            multi_turn_conversation.main()

        print(f"\n✅ {description} complete!")

    except Exception as e:
        print(f"\n❌ {description} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Run all evaluations."""
    print("=" * 60)
    print("Weather Chat - Full Evaluation Suite")
    print("=" * 60)
    print(f"Project: {PROJECT_NAME}")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    results = {}

    # Run single-turn evaluation
    results["Single-Turn"] = run_evaluation(
        "weather_conversation",
        "Single-Turn Conversation Evaluation"
    )

    # Run multi-turn evaluation
    results["Multi-Turn"] = run_evaluation(
        "multi_turn_conversation",
        "Multi-Turn Conversation Evaluation"
    )

    # Print summary
    print(f"\n{'=' * 60}")
    print("Evaluation Summary")
    print(f"{'=' * 60}")

    all_passed = True
    for eval_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{eval_name:20s} {status}")
        if not passed:
            all_passed = False

    print(f"{'=' * 60}")

    if all_passed:
        print("\n🎉 All evaluations completed successfully!")
    else:
        print("\n⚠️  Some evaluations failed. Check logs above for details.")

    print(f"\n🔗 View results at: https://www.braintrust.dev/app/{PROJECT_NAME}")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

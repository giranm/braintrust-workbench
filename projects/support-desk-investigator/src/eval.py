"""
Support Desk Investigator - Evaluation Framework

This module implements custom evaluation scorers for support quality metrics
and runs experiments using Braintrust to compare different approaches.
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import braintrust
    from openai import OpenAI
except ImportError:
    print("Error: Required packages not installed. Run: uv sync")
    exit(1)


# Test dataset of support tickets with expected quality criteria
TEST_DATASET = [
    {
        "input": "My payment failed but I was charged twice. Can you help?",
        "category": "billing",
        "expected": {
            "should_acknowledge_frustration": True,
            "should_offer_solution": True,
            "should_request_details": True
        }
    },
    {
        "input": "I can't log in to my account. I keep getting an error message.",
        "category": "technical",
        "expected": {
            "should_offer_troubleshooting": True,
            "should_be_clear": True,
            "should_ask_for_error_details": True
        }
    },
    {
        "input": "What are your business hours?",
        "category": "general",
        "expected": {
            "should_be_concise": True,
            "should_be_professional": True
        }
    },
    {
        "input": "Your product is terrible and doesn't work!",
        "category": "general",
        "expected": {
            "should_remain_professional": True,
            "should_show_empathy": True,
            "should_offer_help": True
        }
    },
]


def quality_scorer(output: str, expected: Dict[str, Any]) -> float:
    """
    Custom scorer for response quality.

    Evaluates if the response meets basic quality criteria like being
    helpful, complete, and addressing the issue.

    Returns:
        Score between 0.0 and 1.0
    """
    # Simple heuristic scoring (in production, use LLM-as-judge)
    score = 0.0
    checks_passed = 0
    total_checks = len(expected)

    output_lower = output.lower()

    # Check for acknowledgment of frustration
    if expected.get("should_acknowledge_frustration"):
        if any(word in output_lower for word in ["understand", "apologize", "sorry", "frustrating"]):
            checks_passed += 1

    # Check for solution offering
    if expected.get("should_offer_solution"):
        if any(word in output_lower for word in ["will", "can", "help", "resolve", "fix"]):
            checks_passed += 1

    # Check for requesting details
    if expected.get("should_request_details"):
        if any(word in output_lower for word in ["could you", "please provide", "can you share", "?"]):
            checks_passed += 1

    # Check for troubleshooting
    if expected.get("should_offer_troubleshooting"):
        if any(word in output_lower for word in ["try", "check", "verify", "ensure"]):
            checks_passed += 1

    # Check for clarity
    if expected.get("should_be_clear"):
        checks_passed += 1 if len(output) > 50 and len(output) < 500 else 0

    # Check for error detail request
    if expected.get("should_ask_for_error_details"):
        if any(word in output_lower for word in ["error", "message", "details", "?"]):
            checks_passed += 1

    # Check for conciseness
    if expected.get("should_be_concise"):
        checks_passed += 1 if len(output) < 200 else 0

    # Check for professionalism
    if expected.get("should_be_professional"):
        checks_passed += 1 if not any(word in output_lower for word in ["dude", "bro", "lol"]) else 0

    # Check for remaining professional with angry customers
    if expected.get("should_remain_professional"):
        checks_passed += 1 if not any(word in output_lower for word in ["you're wrong", "that's not true"]) else 0

    # Check for empathy
    if expected.get("should_show_empathy"):
        if any(word in output_lower for word in ["understand", "hear you", "appreciate", "sorry"]):
            checks_passed += 1

    # Check for offering help
    if expected.get("should_offer_help"):
        if any(word in output_lower for word in ["help", "assist", "support", "resolve"]):
            checks_passed += 1

    score = checks_passed / total_checks if total_checks > 0 else 0.0
    return score


def empathy_scorer(output: str) -> float:
    """
    Custom scorer for empathy and tone.

    Evaluates if the response shows appropriate empathy and professionalism.

    Returns:
        Score between 0.0 and 1.0
    """
    output_lower = output.lower()

    # Empathy indicators
    empathy_words = [
        "understand", "appreciate", "sorry", "apologize",
        "hear you", "frustrating", "inconvenience", "concern"
    ]

    empathy_count = sum(1 for word in empathy_words if word in output_lower)

    # Professional tone (no informal language)
    unprofessional_words = ["dude", "bro", "lol", "whatever", "yeah"]
    has_unprofessional = any(word in output_lower for word in unprofessional_words)

    # Calculate score
    empathy_score = min(empathy_count / 2.0, 1.0)  # Max 2 empathy words expected
    tone_penalty = -0.3 if has_unprofessional else 0.0

    return max(0.0, empathy_score + tone_penalty)


def resolution_scorer(output: str) -> float:
    """
    Custom scorer for resolution effectiveness.

    Evaluates if the response offers a clear path to resolution or escalation.

    Returns:
        Score between 0.0 and 1.0
    """
    output_lower = output.lower()

    # Resolution indicators
    action_words = [
        "will", "can help", "resolve", "fix", "investigate",
        "escalate", "team will", "follow up"
    ]

    has_action = any(word in output_lower for word in action_words)

    # Vague responses (negative indicators)
    vague_words = ["maybe", "might", "possibly", "not sure"]
    has_vague = any(word in output_lower for word in vague_words)

    # Calculate score
    base_score = 0.8 if has_action else 0.3
    vague_penalty = -0.2 if has_vague else 0.0

    return max(0.0, min(1.0, base_score + vague_penalty))


def run_evaluation():
    """Run evaluation on the support agent using the test dataset."""
    print("🔬 Running Support Agent Evaluation\n")

    # Import agent from main module
    from main import SupportAgent

    # Initialize agent
    agent = SupportAgent()

    # Initialize Braintrust experiment
    experiment = braintrust.init(
        project="support-desk-investigator",
        experiment="baseline-evaluation",
        api_key=os.environ.get("BRAINTRUST_API_KEY")
    )

    # Run evaluation on each test case
    for test_case in TEST_DATASET:
        # Generate response
        result = agent.generate_response(
            ticket=test_case["input"],
            category=test_case["category"]
        )

        response = result["response"]

        # Score the response
        quality_score = quality_scorer(response, test_case["expected"])
        empathy_score = empathy_scorer(response)
        resolution_score = resolution_scorer(response)

        # Log to Braintrust experiment
        experiment.log(
            input=test_case["input"],
            output=response,
            expected=test_case["expected"],
            scores={
                "quality": quality_score,
                "empathy": empathy_score,
                "resolution": resolution_score,
                "overall": (quality_score + empathy_score + resolution_score) / 3.0
            },
            metadata={
                "category": test_case["category"],
                "model": result["model"]
            }
        )

        # Print results
        print(f"Ticket: {test_case['input'][:50]}...")
        print(f"  Quality: {quality_score:.2f}")
        print(f"  Empathy: {empathy_score:.2f}")
        print(f"  Resolution: {resolution_score:.2f}")
        print(f"  Overall: {(quality_score + empathy_score + resolution_score) / 3.0:.2f}\n")

    # Finalize experiment
    experiment_url = experiment.summarize()

    print("✅ Evaluation complete!")
    print(f"📈 View results at: {experiment_url}")
    print("\nTarget Thresholds:")
    print("  - Quality: ≥ 0.80")
    print("  - Empathy: ≥ 0.85")
    print("  - Resolution: ≥ 0.75")


if __name__ == "__main__":
    run_evaluation()

#!/usr/bin/env python3
"""
Setup script for weather chat evaluations.

This script:
1. Creates datasets in Braintrust
2. Uploads sample conversation data
3. Verifies the setup

Run with: uv run python evals/setup_evals.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from braintrust import init_dataset

# Load environment
load_dotenv()

PROJECT_NAME = os.getenv("PROJECT_NAME", "multi-agent-chat-demo")

# Dataset configurations
DATASETS = {
    "WeatherConversationDataset": {
        "file": "sample_conversations.json",
        "description": "Weather conversation test cases with single-turn queries",
    },
    "MultiTurnWeatherDataset": {
        "file": "multi_turn_conversations.json",
        "description": "Multi-turn weather conversation scenarios",
    },
}


def load_json_data(filename: str) -> list:
    """Load data from JSON file."""
    file_path = Path(__file__).parent / "datasets" / filename
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def setup_single_turn_dataset():
    """Create and populate the single-turn evaluation dataset."""
    dataset_name = "WeatherConversationDataset"
    config = DATASETS[dataset_name]

    print(f"\n{'=' * 60}")
    print(f"Setting up {dataset_name}")
    print(f"{'=' * 60}")

    # Load data
    print("📂 Loading sample data...")
    sample_data = load_json_data(config["file"])
    print(f"   Loaded {len(sample_data)} test cases")

    # Print categories breakdown
    categories = {}
    for item in sample_data:
        category = item.get("metadata", {}).get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1

    print("\n📊 Dataset breakdown:")
    for category, count in sorted(categories.items()):
        print(f"   - {category}: {count}")

    # Initialize dataset in Braintrust
    print(f"\n🔧 Initializing dataset in Braintrust...")
    dataset = init_dataset(
        project=PROJECT_NAME,
        name=dataset_name,
        description=config["description"],
    )

    # Insert data
    print("📤 Uploading test cases...")
    for item in sample_data:
        dataset.insert(
            input=item["input"],
            expected=item["expected"],
            metadata=item["metadata"],
        )

    print(f"\n✅ {dataset_name} setup complete!")
    print(f"   Test cases: {len(sample_data)}")
    print(f"   View at: https://www.braintrust.dev/app/{PROJECT_NAME}/datasets/{dataset_name}")


def setup_multi_turn_dataset():
    """Create and populate the multi-turn evaluation dataset."""
    dataset_name = "MultiTurnWeatherDataset"
    config = DATASETS[dataset_name]

    print(f"\n{'=' * 60}")
    print(f"Setting up {dataset_name}")
    print(f"{'=' * 60}")

    # Load data
    print("📂 Loading sample data...")
    sample_data = load_json_data(config["file"])
    print(f"   Loaded {len(sample_data)} conversation scenarios")

    # Print categories breakdown
    categories = {}
    for item in sample_data:
        category = item.get("metadata", {}).get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1

    print("\n📊 Dataset breakdown:")
    for category, count in sorted(categories.items()):
        print(f"   - {category}: {count}")

    # Initialize dataset in Braintrust
    print(f"\n🔧 Initializing dataset in Braintrust...")
    dataset = init_dataset(
        project=PROJECT_NAME,
        name=dataset_name,
        description=config["description"],
    )

    # Insert data
    print("📤 Uploading conversation scenarios...")
    for item in sample_data:
        dataset.insert(
            input={"messages": item["messages"]},
            metadata=item["metadata"],
        )

    print(f"\n✅ {dataset_name} setup complete!")
    print(f"   Scenarios: {len(sample_data)}")
    print(f"   View at: https://www.braintrust.dev/app/{PROJECT_NAME}/datasets/{dataset_name}")


def main():
    """Main setup function."""
    print("=" * 60)
    print("Weather Chat Evaluation Setup")
    print("=" * 60)
    print(f"Project: {PROJECT_NAME}")
    print()

    try:
        # Set up both datasets
        setup_single_turn_dataset()
        setup_multi_turn_dataset()

        print(f"\n{'=' * 60}")
        print("🎉 All datasets set up successfully!")
        print(f"{'=' * 60}")
        print("\nYou can now run evaluations:")
        print("  • Single-turn: uv run python evals/weather_conversation.py")
        print("  • Multi-turn:  uv run python evals/multi_turn_conversation.py")
        print(f"\nView all datasets at: https://www.braintrust.dev/app/{PROJECT_NAME}/datasets")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

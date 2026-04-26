"""Thin interactive CLI for the multi-agent customer support demo."""

import argparse
import asyncio
import os
import sys

import braintrust

from src.orchestrator import BRAINTRUST_PROJECT, create_session, send_message


async def main(verbose: bool = False) -> None:
    logger = braintrust.init_logger(project=BRAINTRUST_PROJECT)

    session_id = await create_session()

    print()
    print("Customer Support AI (type 'quit' to exit)")
    print("-" * 42)
    print()

    conversation_log = []

    with logger.start_span(name="conversation", type="task") as conversation_span:
        conversation_span.log(metadata={"session_id": session_id, "mode": "interactive"})

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                break

            response = await send_message(
                session_id=session_id,
                message=user_input,
                conversation_span=conversation_span,
                verbose=verbose,
            )

            conversation_log.append({"role": "user", "content": user_input})
            conversation_log.append({"role": "assistant", "content": response})

            print(f"Agent: {response}")
            print()

        conversation_span.log(
            input={"messages": [turn["content"] for turn in conversation_log if turn["role"] == "user"]},
            output={"conversation": conversation_log},
        )

    print()
    print(f"Session logged to Braintrust project: {BRAINTRUST_PROJECT}")
    logger.flush()


def cli() -> None:
    parser = argparse.ArgumentParser(description="Customer Support AI CLI")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show agent routing and tool calls",
    )
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        print("Error: Set ANTHROPIC_API_KEY or GOOGLE_API_KEY in .env", file=sys.stderr)
        sys.exit(1)

    asyncio.run(main(verbose=args.verbose))


if __name__ == "__main__":
    cli()

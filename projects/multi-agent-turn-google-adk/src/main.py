"""Main entry point — runs a scripted demo scenario for quick verification."""

import asyncio
import os
import sys

import braintrust

from src.orchestrator import BRAINTRUST_PROJECT, create_session, send_message

DEMO_MESSAGES = [
    "Where is my order #12345?",
    "Can I cancel it?",
    "What about order #11111 — can that one be cancelled?",
    "Will I get a refund for that?",
    "What is your return policy?",
]


async def main() -> None:
    logger = braintrust.init_logger(project=BRAINTRUST_PROJECT)

    session_id = await create_session()

    print(f"Running demo scenario (project: {BRAINTRUST_PROJECT})")
    print("=" * 50)
    print()

    conversation_log = []

    with logger.start_span(name="demo-conversation", type="task") as conversation_span:
        conversation_span.log(
            input={"messages": DEMO_MESSAGES},
            metadata={"session_id": session_id, "mode": "demo"},
        )

        for msg in DEMO_MESSAGES:
            print(f"User: {msg}")
            response = await send_message(
                session_id=session_id,
                message=msg,
                conversation_span=conversation_span,
                verbose=True,
            )
            conversation_log.append({"role": "user", "content": msg})
            conversation_log.append({"role": "assistant", "content": response})
            print(f"Agent: {response}")
            print()

        conversation_span.log(output={"conversation": conversation_log})

    print("=" * 50)
    print(f"Demo complete. View traces at: https://www.braintrust.dev/app")
    logger.flush()


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        print("Error: Set ANTHROPIC_API_KEY or GOOGLE_API_KEY in .env", file=sys.stderr)
        sys.exit(1)

    asyncio.run(main())

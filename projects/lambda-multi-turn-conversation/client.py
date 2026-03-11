#!/usr/bin/env python3
"""
Interactive Python client for testing Braintrust multi-turn Lambda tracing.

Usage:
    python client.py --function braintrust-conversation-lambda-dev --profile sandbox
"""

import boto3
import json
import uuid
import argparse
from datetime import datetime
from typing import List, Dict


class ConversationClient:
    """Client for invoking Lambda function and managing conversation state."""

    def __init__(self, function_name: str, profile: str = "sandbox", region: str = "us-east-1"):
        """
        Initialize conversation client.

        Args:
            function_name: Name of the Lambda function to invoke
            profile: AWS profile name for authentication
            region: AWS region
        """
        session = boto3.Session(profile_name=profile, region_name=region)
        self.lambda_client = session.client("lambda")
        self.function_name = function_name
        self.conversation_id = str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []
        self.message_count = 0

    def send_message(self, user_message: str) -> Dict:
        """
        Send a message to the Lambda function and get response.

        Args:
            user_message: User's message text

        Returns:
            Dict containing the response and metadata
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})

        # Prepare Lambda payload
        payload = {
            "body": json.dumps({
                "conversationId": self.conversation_id,
                "messages": self.messages,
                "userId": "test-user",
            })
        }

        try:
            # Invoke Lambda function
            print(f"\n[DEBUG] Invoking Lambda: {self.function_name}")
            print(f"[DEBUG] Conversation ID: {self.conversation_id}")
            print(f"[DEBUG] Message count: {len(self.messages)}")

            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            # Parse response
            result = json.loads(response["Payload"].read())

            print(f"[DEBUG] Lambda StatusCode: {response['StatusCode']}")
            print(f"[DEBUG] Response keys: {list(result.keys())}")

            if response["StatusCode"] != 200:
                print(f"[DEBUG] Full response: {json.dumps(result, indent=2)}")
                raise Exception(f"Lambda returned status code {response['StatusCode']}")

            if result.get("statusCode") != 200:
                print(f"[DEBUG] Error response body: {result.get('body', 'N/A')}")
                error_body = json.loads(result.get("body", "{}"))
                error_message = error_body.get("error", "Unknown error")
                error_detail = error_body.get("message", "")
                full_error = f"{error_message}: {error_detail}" if error_detail else error_message
                raise Exception(f"Lambda error (status {result.get('statusCode')}): {full_error}")

            body = json.loads(result["body"])
            assistant_message = body["response"]
            usage = body.get("usage", {})
            message_number = body.get("messageNumber", 0)

            # Add assistant response to history
            self.messages.append({"role": "assistant", "content": assistant_message})
            self.message_count = message_number

            return {
                "message": assistant_message,
                "usage": usage,
                "messageNumber": message_number,
            }

        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON decode error: {str(e)}")
            print(f"[DEBUG] Raw response: {response.get('Payload', 'N/A')}")
            raise Exception(f"Failed to parse Lambda response: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Exception type: {type(e).__name__}")
            print(f"[DEBUG] Exception details: {str(e)}")
            raise Exception(f"Failed to invoke Lambda: {str(e)}")

    def run(self):
        """Run interactive conversation loop."""
        print("=" * 70)
        print("Braintrust Multi-Turn Lambda Tracing Test Client")
        print("=" * 70)
        print(f"\nConversation ID: {self.conversation_id}")
        print(f"Lambda Function: {self.function_name}")
        print("\nCommands:")
        print("  Type your message to send it")
        print("  'exit' or 'quit' - Exit the program")
        print("  'reset' - Start a new conversation")
        print("  'info' - Show conversation info")
        print("=" * 70)
        print()

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["exit", "quit"]:
                    print("\nGoodbye!")
                    break

                elif user_input.lower() == "reset":
                    self.conversation_id = str(uuid.uuid4())
                    self.messages = []
                    self.message_count = 0
                    print(f"\n✓ New conversation started: {self.conversation_id}\n")
                    continue

                elif user_input.lower() == "info":
                    print(f"\n" + "=" * 70)
                    print("Conversation Info:")
                    print(f"  ID: {self.conversation_id}")
                    print(f"  Messages: {self.message_count}")
                    print(f"  Function: {self.function_name}")
                    print("=" * 70 + "\n")
                    continue

                # Send message to Lambda
                print("  [Sending to Lambda...]", end=" ", flush=True)
                result = self.send_message(user_input)
                print("✓")

                # Display response
                print(f"Assistant: {result['message']}")

                # Display usage stats
                usage = result['usage']
                print(f"  [Message #{result['messageNumber']} | "
                      f"Tokens: {usage.get('prompt_tokens', 0)} prompt + "
                      f"{usage.get('completion_tokens', 0)} completion = "
                      f"{usage.get('total_tokens', 0)} total]")
                print()

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit or continue chatting.\n")
                continue

            except Exception as e:
                print(f"✗ Error: {str(e)}\n")
                continue


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive client for testing Braintrust multi-turn Lambda tracing"
    )
    parser.add_argument(
        "--function",
        default="braintrust-conversation-lambda-dev",
        help="Lambda function name (default: braintrust-conversation-lambda-dev)"
    )
    parser.add_argument(
        "--profile",
        default="sandbox",
        help="AWS profile name (default: sandbox)"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )

    args = parser.parse_args()

    # Create and run client
    try:
        client = ConversationClient(
            function_name=args.function,
            profile=args.profile,
            region=args.region
        )
        client.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

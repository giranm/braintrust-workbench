"""Weather-augmented agent using Anthropic tool calling."""

import os
import asyncio
from typing import Optional
from anthropic import Anthropic
from braintrust import traced, init_logger, current_span, start_span, wrap_anthropic
from ..tools.weather import get_weather_for_city, format_weather_response

# Initialize logger
logger = init_logger(project=os.getenv("PROJECT_NAME", "multi-agent-chat-demo"))


class WeatherAgent:
    """Agent that can answer weather queries using Open-Meteo API."""

    def __init__(self):
        """Initialize WeatherAgent with Anthropic client and tool definitions."""
        self.name = "WeatherBot"
        self.role = "Weather Information Assistant"

        # Wrap Anthropic client with Braintrust for automatic LLM span instrumentation
        self.client = wrap_anthropic(
            Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        )

        # Track conversation-level spans for multi-turn conversations
        self._conversation_spans = {}

        # Define weather tool for Anthropic
        self.tools = [
            {
                "name": "get_weather",
                "description": (
                    "Get current weather information for a specific city. "
                    "Returns temperature, wind speed, humidity, and weather conditions."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name to get weather for (e.g., 'London', 'New York', 'Tokyo')",
                        }
                    },
                    "required": ["city"],
                },
            }
        ]

        self.system_prompt = (
            "You are a helpful weather assistant. You can provide current weather "
            "information for any city in the world. When users ask about weather, "
            "use the get_weather tool to fetch real-time data. Be friendly and "
            "provide context about what the weather means (e.g., 'It's quite cold' or "
            "'Perfect weather for outdoor activities')."
        )

    def _get_or_create_conversation_span(self, conversation_id: str):
        """
        Get or create a conversation-level span for multi-turn tracking.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Braintrust span object for the conversation
        """
        if conversation_id not in self._conversation_spans:
            # Create a new conversation-level span
            span = logger.start_span(
                name=f"conversation-{conversation_id}",
                span_attributes={
                    "conversation_id": conversation_id,
                    "agent": self.name,
                },
            )
            self._conversation_spans[conversation_id] = span
        return self._conversation_spans[conversation_id]

    async def respond(
        self,
        message: str,
        conversation_history: list = None,
        conversation_id: str = None,
    ) -> str:
        """
        Generate agent response with weather tool calling.

        Args:
            message: User message
            conversation_history: Optional conversation history
            conversation_id: Optional conversation ID for Braintrust tracing

        Returns:
            Agent response string
        """
        # Get or create conversation-level span for multi-turn tracking
        conv_span = None
        if conversation_id:
            conv_span = self._get_or_create_conversation_span(conversation_id)

        # Calculate turn number
        turn_number = len(conversation_history) // 2 if conversation_history else 0

        # Create a turn-level span as child of conversation span
        turn_span_name = f"turn-{turn_number}"

        # Execute the turn within the conversation span context
        async def _execute_turn():
            # Build messages list
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            # Initial API call with tools
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages,
                tools=self.tools,
                temperature=0.7,
            )

            # Handle tool use
            if response.stop_reason == "tool_use":
                # Extract tool calls and execute them with tracing
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        # Execute weather tool with explicit span
                        if tool_name == "get_weather":
                            # Create a tool execution span
                            @traced(name=f"tool_execution:{tool_name}")
                            async def execute_tool():
                                try:
                                    weather_data = await get_weather_for_city(tool_input["city"])
                                    formatted_weather = format_weather_response(weather_data)
                                    return {
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": formatted_weather,
                                    }
                                except Exception as e:
                                    error_msg = f"Error fetching weather: {str(e)}"
                                    return {
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": error_msg,
                                        "is_error": True,
                                    }

                            result = await execute_tool()
                            tool_results.append(result)

                # Continue conversation with tool results
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

                # Get final response
                final_response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=messages,
                    tools=self.tools,
                    temperature=0.7,
                )

                reply = final_response.content[0].text

            else:
                # No tool use, extract text response
                reply = response.content[0].text

            return reply

        # Execute within conversation span context if available
        if conv_span:
            # Use the conversation span object directly as parent
            with conv_span.start_span(
                name=turn_span_name,
                span_attributes={
                    "turn_number": turn_number,
                    "message": message,
                },
                input={"message": message, "conversation_history": conversation_history},
            ) as turn_span:
                result = await _execute_turn()
                turn_span.log(output=result)
                return result
        else:
            # No conversation tracking, just execute
            return await _execute_turn()

    def end_conversation(self, conversation_id: str):
        """
        End a conversation and flush its span.

        Args:
            conversation_id: Conversation ID to end
        """
        if conversation_id in self._conversation_spans:
            span = self._conversation_spans[conversation_id]
            span.end()
            del self._conversation_spans[conversation_id]

    def respond_sync(self, message: str, conversation_history: list = None) -> str:
        """
        Synchronous wrapper for respond() method.

        Args:
            message: User message
            conversation_history: Optional conversation history

        Returns:
            Agent response string
        """
        return asyncio.run(self.respond(message, conversation_history))

"""Weather chat application with Braintrust observability."""
import reflex as rx
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

from .agents.weather_agent import WeatherAgent


# Message model
class ChatMessage(BaseModel):
    """Chat message data model."""
    role: str
    content: str
    timestamp: str = ""
    is_loading: bool = False


# Conversation model
class Conversation(BaseModel):
    """Conversation data model."""
    id: str
    title: str
    messages: list[ChatMessage] = []
    created_at: str
    updated_at: str


# State
class ChatState(rx.State):
    """State management for chat interface with conversation history."""

    # Conversations
    conversations: list[Conversation] = []
    current_conversation_id: Optional[str] = None

    # UI state
    current_input: str = ""
    is_processing: bool = False
    sidebar_open: bool = True
    theme: str = "light"  # "light" or "dark" - default to light for better compilation

    # Agent instance
    _agent: WeatherAgent = None

    def _get_agent(self) -> WeatherAgent:
        """Get or create agent instance."""
        if ChatState._agent is None:
            ChatState._agent = WeatherAgent()
        return ChatState._agent

    def _get_current_conversation(self) -> Optional[Conversation]:
        """Get the current active conversation."""
        for conv in self.conversations:
            if conv.id == self.current_conversation_id:
                return conv
        return None

    def _update_conversation(self, conversation: Conversation):
        """Update a conversation in the list."""
        for i, conv in enumerate(self.conversations):
            if conv.id == conversation.id:
                self.conversations[i] = conversation
                break

    def new_conversation(self):
        """Create a new conversation."""
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        new_conv = Conversation(
            id=conv_id,
            title="New Conversation",
            messages=[],
            created_at=now,
            updated_at=now,
        )
        self.conversations.insert(0, new_conv)
        self.current_conversation_id = conv_id

    def select_conversation(self, conversation_id: str):
        """Switch to a different conversation."""
        self.current_conversation_id = conversation_id

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation."""
        self.conversations = [c for c in self.conversations if c.id != conversation_id]
        if self.current_conversation_id == conversation_id:
            self.current_conversation_id = self.conversations[0].id if self.conversations else None

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        self.sidebar_open = not self.sidebar_open

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.theme = "light" if self.theme == "dark" else "dark"

    @rx.var
    def current_messages(self) -> list[ChatMessage]:
        """Get messages for current conversation."""
        conv = self._get_current_conversation()
        return conv.messages if conv else []

    async def send_message(self):
        """Handle user message and get agent response."""
        if not self.current_input.strip():
            return

        # Create new conversation if none exists
        if not self.current_conversation_id:
            self.new_conversation()

        conv = self._get_current_conversation()
        if not conv:
            return

        # Add user message with timestamp
        user_msg = ChatMessage(
            role="user",
            content=self.current_input,
            timestamp=datetime.now().strftime("%I:%M %p")
        )
        conv.messages.append(user_msg)

        # Update conversation title from first message
        if len(conv.messages) == 1:
            conv.title = self.current_input[:50] + ("..." if len(self.current_input) > 50 else "")

        conv.updated_at = datetime.now().isoformat()

        user_input = self.current_input
        self.current_input = ""
        self.is_processing = True

        # Add loading message
        assistant_msg = ChatMessage(
            role="assistant",
            content="",
            timestamp=datetime.now().strftime("%I:%M %p"),
            is_loading=True
        )
        conv.messages.append(assistant_msg)
        self._update_conversation(conv)
        yield

        try:
            agent = self._get_agent()
            conversation_history = []
            for msg in conv.messages[:-1]:
                if not msg.is_loading:
                    conversation_history.append({"role": msg.role, "content": msg.content})

            # Pass conversation ID to agent for Braintrust tracing
            response = await agent.respond(
                user_input,
                conversation_history,
                conversation_id=conv.id
            )

            conv.messages[-1].content = response
            conv.messages[-1].is_loading = False
            conv.messages[-1].timestamp = datetime.now().strftime("%I:%M %p")
            conv.updated_at = datetime.now().isoformat()
            self._update_conversation(conv)
        except Exception as e:
            conv.messages[-1].content = f"Sorry, I encountered an error: {str(e)}"
            conv.messages[-1].is_loading = False
            self._update_conversation(conv)
        finally:
            self.is_processing = False


# Components
def message_bubble(msg: ChatMessage) -> rx.Component:
    """Render a single chat message bubble with markdown support."""
    is_user = msg.role == "user"

    return rx.box(
        rx.vstack(
            rx.cond(
                msg.is_loading,
                rx.hstack(
                    rx.spinner(size="3"),
                    rx.text("Thinking...", size="2"),
                    spacing="2"
                ),
                rx.cond(
                    is_user,
                    rx.text(msg.content, white_space="pre-wrap", size="3"),
                    rx.markdown(msg.content, size="3"),  # Markdown for agent responses
                ),
            ),
            rx.text(
                msg.timestamp,
                size="1",
                color=rx.cond(ChatState.theme == "dark", "#9ca3af", "#6b7280"),
                align_self="end",
            ),
            align_items="start",
            spacing="2",
            width="100%",
        ),
        background=rx.cond(
            is_user,
            rx.cond(ChatState.theme == "dark", "#2563eb", "#2563eb"),  # Blue for user in both modes
            rx.cond(ChatState.theme == "dark", "#374151", "#e5e7eb")  # Gray for assistant
        ),
        color=rx.cond(
            is_user,
            "white",  # White text for user messages (both modes)
            rx.cond(ChatState.theme == "dark", "#f9fafb", "#1f2937")  # Dark text for assistant in light mode
        ),
        padding="1rem",
        border_radius="0.75rem",
        max_width="75%",
        align_self=rx.cond(is_user, "flex-end", "flex-start"),
        box_shadow="sm",
    )


def conversation_item(conv: Conversation) -> rx.Component:
    """Render a conversation item in the sidebar."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    conv.title,
                    size="3",
                    weight=rx.cond(
                        ChatState.current_conversation_id == conv.id,
                        "bold",
                        "regular"
                    ),
                    color=rx.cond(
                        ChatState.current_conversation_id == conv.id,
                        rx.cond(ChatState.theme == "dark", "#60a5fa", "#2563eb"),
                        rx.cond(ChatState.theme == "dark", "#f9fafb", "#111827")
                    ),
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                rx.text(
                    rx.cond(
                        conv.messages.length() == 1,
                        "1 message",
                        f"{conv.messages.length()} messages"
                    ),
                    size="1",
                    color=rx.cond(ChatState.theme == "dark", "#9ca3af", "#6b7280"),
                ),
                align_items="start",
                spacing="1",
                flex="1",
                min_width="0",
            ),
            rx.icon_button(
                rx.icon("trash-2", size=16),
                on_click=lambda: ChatState.delete_conversation(conv.id),
                variant="ghost",
                size="1",
                color_scheme="red",
            ),
            spacing="2",
            width="100%",
        ),
        padding="0.75rem",
        border_radius="0.5rem",
        background=rx.cond(
            ChatState.current_conversation_id == conv.id,
            rx.cond(ChatState.theme == "dark", "#1e3a8a", "#dbeafe"),
            "transparent"
        ),
        cursor="pointer",
        on_click=lambda: ChatState.select_conversation(conv.id),
        _hover={"background": rx.cond(
            ChatState.theme == "dark",
            "#374151",
            "#f3f4f6"
        )},
    )


def sidebar() -> rx.Component:
    """Sidebar with conversation history."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading(
                    "Conversations",
                    size="5",
                    color=rx.cond(ChatState.theme == "dark", "#f9fafb", "#111827")
                ),
                rx.icon_button(
                    rx.icon("x", size=18),
                    on_click=ChatState.toggle_sidebar,
                    variant="ghost",
                    size="2",
                ),
                justify="between",
                width="100%",
            ),

            # New conversation button
            rx.button(
                rx.icon("plus", size=18),
                "New Conversation",
                on_click=ChatState.new_conversation,
                width="100%",
                color_scheme="blue",
            ),

            # Conversation list
            rx.box(
                rx.cond(
                    ChatState.conversations.length() > 0,
                    rx.vstack(
                        rx.foreach(ChatState.conversations, conversation_item),
                        spacing="2",
                        width="100%",
                    ),
                    rx.text(
                        "No conversations yet",
                        size="2",
                        color=rx.cond(ChatState.theme == "dark", "#9ca3af", "#6b7280")
                    ),
                ),
                width="100%",
                overflow_y="auto",
                flex="1",
            ),

            spacing="4",
            height="100vh",
            padding="1.5rem",
        ),
        width="300px",
        border_right=f"1px solid {rx.cond(ChatState.theme == 'dark', '#374151', '#e5e7eb')}",
        background=rx.cond(ChatState.theme == "dark", "#1f2937", "#f9fafb"),
        display=rx.cond(ChatState.sidebar_open, "block", "none"),
    )


def chat_area() -> rx.Component:
    """Main chat area."""
    return rx.vstack(
        # Header with theme toggle
        rx.hstack(
            rx.hstack(
                rx.cond(
                    ChatState.sidebar_open == False,
                    rx.icon_button(
                        rx.icon("menu", size=18),
                        on_click=ChatState.toggle_sidebar,
                        variant="ghost",
                        size="2",
                    ),
                    rx.fragment(),
                ),
                rx.heading(
                    "🌤️ Weather Chat Assistant",
                    size="7",
                    color=rx.cond(ChatState.theme == "dark", "#f9fafb", "#111827")
                ),
                spacing="3",
            ),
            rx.icon_button(
                rx.icon(
                    rx.cond(ChatState.theme == "dark", "sun", "moon"),
                    size=18
                ),
                on_click=ChatState.toggle_theme,
                variant="ghost",
                size="2",
            ),
            justify="between",
            width="100%",
            padding="1rem",
            border_bottom=f"1px solid {rx.cond(ChatState.theme == 'dark', '#374151', '#e5e7eb')}",
        ),

        # Messages - centered with max width
        rx.box(
            rx.cond(
                ChatState.current_messages.length() > 0,
                rx.center(
                    rx.vstack(
                        rx.foreach(ChatState.current_messages, message_bubble),
                        spacing="4",
                        width="100%",
                        max_width="1000px",
                        padding="1.5rem",
                    ),
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.text("🌤️", font_size="4rem"),
                        rx.heading(
                            "Weather Chat Assistant",
                            size="6",
                            color=rx.cond(ChatState.theme == "dark", "#f9fafb", "#111827")
                        ),
                        rx.text(
                            "Ask me about the weather in any city!",
                            size="3",
                            color=rx.cond(ChatState.theme == "dark", "#d1d5db", "#4b5563"),
                            class_name="empty-state-text",
                        ),
                        rx.button(
                            "Start New Conversation",
                            on_click=ChatState.new_conversation,
                            color_scheme="blue",
                            size="3",
                        ),
                        spacing="3",
                    ),
                    height="100%",
                ),
            ),
            flex="1",
            overflow_y="auto",
            width="100%",
            background=rx.cond(ChatState.theme == "dark", "#111827", "#ffffff"),
        ),

        # Input - centered like ChatGPT
        rx.box(
            rx.box(
                rx.hstack(
                    rx.input(
                        placeholder="Ask about weather in a city...",
                        value=ChatState.current_input,
                        on_change=ChatState.set_current_input,
                        disabled=ChatState.is_processing,
                        size="3",
                        flex="1",
                        background=rx.cond(ChatState.theme == "dark", "#1f2937", "white"),
                        color=rx.cond(ChatState.theme == "dark", "#f9fafb", "#111827"),
                        border_color=rx.cond(ChatState.theme == "dark", "#374151", "#9ca3af"),
                        _placeholder={"color": rx.cond(ChatState.theme == "dark", "#9ca3af", "#4b5563")},
                        _focus={"border_color": "#3b82f6"},
                    ),
                    rx.button(
                        rx.icon("send", size=18),
                        on_click=ChatState.send_message,
                        disabled=ChatState.is_processing,
                        loading=ChatState.is_processing,
                        size="3",
                        color_scheme="blue",
                    ),
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                max_width="1000px",
                margin="0 auto",  # Center horizontally
                padding_x="2rem",
                padding_y="1rem",
            ),
            border_top=f"1px solid {rx.cond(ChatState.theme == 'dark', '#374151', '#e5e7eb')}",
            background=rx.cond(ChatState.theme == "dark", "#1f2937", "white"),
            width="100%",
        ),

        spacing="0",
        height="100vh",
        width="100%",
        background=rx.cond(ChatState.theme == "dark", "#111827", "white"),
    )


def chat_interface() -> rx.Component:
    """Main chat interface with sidebar."""
    return rx.box(
        rx.hstack(
            sidebar(),
            chat_area(),
            spacing="0",
            width="100%",
            height="100vh",
        ),
        data_theme=ChatState.theme,
    )


# Create app with custom stylesheet
app = rx.App(
    stylesheets=[
        "/custom.css",  # Custom CSS for light mode fixes
    ]
)
app.add_page(chat_interface, route="/", title="Weather Chat Assistant")

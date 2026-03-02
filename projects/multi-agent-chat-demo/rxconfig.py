"""Reflex configuration file."""

import reflex as rx

config = rx.Config(
    app_name="multi_agent_chat_demo",
    db_url="sqlite:///data/reflex.db",
    env=rx.Env.PROD,
)

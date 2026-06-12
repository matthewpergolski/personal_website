from __future__ import annotations

import json
import os

import fasthtml.common as ft

from src.assets.loader import asset_script, asset_style
from src.config import get_config


class ChatWidget:
    """Small persistent site chat widget."""

    def __init__(self, *, mode: str = "widget", api_endpoint: str = "/api/rag/chat"):
        self.mode = mode
        self.api_endpoint = api_endpoint

    @classmethod
    def professional_mode(cls) -> tuple:
        return cls(mode="widget").render()

    @classmethod
    def full_page(cls) -> tuple:
        return cls(mode="page").render()

    def render(self) -> tuple:
        return (
            self._styles(),
            self._script(),
            self._shell(),
        )

    def _shell(self):
        config = get_config()
        owner_first_name = (
            config.owner_name.split()[0] if config.owner_name else "this site"
        )
        is_page = self.mode == "page"
        title = (
            config.text("chat", "page_title", "Experience Chat")
            if is_page
            else config.text("chat", "widget_title", "Ask About My Experience")
        )
        ai_polish_enabled = bool(
            os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        )
        chat_placeholder = (
            config.text(
                "chat",
                "advanced_placeholder",
                "Ask about my skills, projects, background, or fit...",
            )
            if ai_polish_enabled
            else config.text(
                "chat", "free_placeholder", "Free-tier chat. Limited answers."
            )
        )
        chat_status = (
            config.text(
                "chat",
                "advanced_status",
                "Advanced chat mode is enabled for more conversational answers.",
            )
            if ai_polish_enabled
            else config.text(
                "chat",
                "free_status",
                "Free-tier chat. Limited answers. Advanced models available.",
            )
        )
        suggestions = config.text_list(
            "chat",
            "suggestions",
            [
                "What AI/ML work have you done?",
                "How have you used Python in your AI/ML work?",
                "Summarize your Lockheed Martin experience.",
                "What kind of roles are you targeting?",
            ],
        )

        return ft.Div(
            ft.Button(
                config.text("chat", "toggle_label", "Chat"),
                id="chat-toggle",
                cls="chat-toggle" if not is_page else "chat-toggle chat-toggle-hidden",
                type="button",
                aria_label=config.text("chat", "toggle_aria_label", "Open chat"),
            ),
            ft.Div(
                ft.Div(
                    ft.Div(
                        ft.H3(title, cls="chat-title"),
                        ft.P(
                            config.text(
                                "chat",
                                "subtitle",
                                "Ask about Matthew's experience, projects, and role fit.",
                            ),
                            cls="chat-subtitle",
                        ),
                    ),
                    ft.Div(
                        ft.A(
                            config.text("chat", "full_chat_label", "Full chat"),
                            href="/chat",
                            cls="chat-full-link"
                            if not is_page
                            else "chat-full-link chat-toggle-hidden",
                        ),
                        ft.Button(
                            config.text("chat", "new_label", "New"),
                            id="chat-reset",
                            cls="chat-reset",
                            type="button",
                            title=config.text("chat", "new_title", "Start a new chat"),
                            aria_label=config.text(
                                "chat", "new_title", "Start a new chat"
                            ),
                        ),
                        ft.Button(
                            config.text("chat", "copy_label", "Copy"),
                            id="chat-copy",
                            cls="chat-copy",
                            type="button",
                            title=config.text(
                                "chat", "copy_title", "Copy conversation"
                            ),
                            aria_label=config.text(
                                "chat",
                                "copy_aria_label",
                                "Copy conversation to clipboard",
                            ),
                        ),
                        ft.Button(
                            config.text("chat", "close_label", "x"),
                            id="chat-close",
                            cls="chat-close"
                            if not is_page
                            else "chat-close chat-toggle-hidden",
                            type="button",
                            aria_label=config.text(
                                "chat", "close_aria_label", "Close chat"
                            ),
                        ),
                        cls="chat-header-actions",
                    ),
                    cls="chat-header",
                ),
                ft.Div(id="chat-messages", cls="chat-messages"),
                ft.Div(
                    *[
                        ft.Button(
                            q, type="button", cls="chat-suggestion", data_question=q
                        )
                        for q in suggestions
                    ],
                    id="chat-suggestions",
                    cls="chat-suggestions",
                ),
                ft.Div(
                    chat_status,
                    id="chat-status",
                    cls="chat-status",
                    role="status",
                    aria_live="polite",
                ),
                ft.Form(
                    ft.Textarea(
                        "",
                        id="chat-input",
                        name="message",
                        rows="2",
                        maxlength="700",
                        placeholder=chat_placeholder,
                        cls="chat-input",
                        aria_label=config.text(
                            "chat", "input_aria_label", "Chat message"
                        ),
                    ),
                    ft.Button(
                        config.text("chat", "send_label", "Send"),
                        type="submit",
                        cls="chat-send",
                        id="chat-send",
                    ),
                    id="chat-form",
                    cls="chat-form",
                    data_endpoint=self.api_endpoint,
                ),
                id="chat-panel",
                cls="chat-panel chat-panel-page"
                if is_page
                else "chat-panel chat-panel-closed",
            ),
            id="experience-chat",
            data_mode=self.mode,
            data_initial=json.dumps(
                [
                    {
                        "role": "assistant",
                        "content": (
                            f"Hi, I can answer questions about "
                            f"{owner_first_name}'s experience, "
                            + config.text(
                                "chat",
                                "initial_message_suffix",
                                "skills, projects, education, and fit for technical roles.",
                            )
                        ),
                    }
                ]
            ),
            cls="experience-chat experience-chat-page"
            if is_page
            else "experience-chat",
        )

    def _script(self):
        return asset_script("chat.js")

    def _styles(self):
        return asset_style("chat.css")

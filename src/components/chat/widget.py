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
        title = "Experience Chat" if is_page else "Ask About My Experience"
        subtitle = "Ask about Matthew's experience, projects, and role fit."
        ai_polish_enabled = bool(
            os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        )
        chat_placeholder = (
            "Ask about my skills, projects, background, or fit..."
            if ai_polish_enabled
            else "Free-tier chat. Limited answers."
        )
        chat_status = (
            "Advanced chat mode is enabled for more conversational answers."
            if ai_polish_enabled
            else ("Free-tier chat. Limited answers. Advanced models available.")
        )
        suggestions = [
            "What AI/ML work have you done?",
            "How have you used Python in your AI/ML work?",
            "Summarize your Lockheed Martin experience.",
            "What kind of roles are you targeting?",
        ]

        return ft.Div(
            ft.Button(
                "Chat",
                id="chat-toggle",
                cls="chat-toggle" if not is_page else "chat-toggle chat-toggle-hidden",
                type="button",
                aria_label="Open chat",
            ),
            ft.Div(
                ft.Div(
                    ft.Div(
                        ft.H3(title, cls="chat-title"),
                        ft.P(subtitle, cls="chat-subtitle"),
                    ),
                    ft.Div(
                        ft.A(
                            "Full chat",
                            href="/chat",
                            cls="chat-full-link"
                            if not is_page
                            else "chat-full-link chat-toggle-hidden",
                        ),
                        ft.Button(
                            "New",
                            id="chat-reset",
                            cls="chat-reset",
                            type="button",
                            title="Start a new chat",
                            aria_label="Start a new chat",
                        ),
                        ft.Button(
                            "Copy",
                            id="chat-copy",
                            cls="chat-copy",
                            type="button",
                            title="Copy conversation",
                            aria_label="Copy conversation to clipboard",
                        ),
                        ft.Button(
                            "x",
                            id="chat-close",
                            cls="chat-close"
                            if not is_page
                            else "chat-close chat-toggle-hidden",
                            type="button",
                            aria_label="Close chat",
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
                        aria_label="Chat message",
                    ),
                    ft.Button("Send", type="submit", cls="chat-send", id="chat-send"),
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
                            f"Hi, I can answer questions about {owner_first_name}'s experience, "
                            "skills, projects, education, and fit for technical roles."
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

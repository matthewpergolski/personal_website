import fasthtml.common as ft

from src.components.chat.widget import ChatWidget
from src.config import get_config


def build_chat_page():
    config = get_config()
    return ft.Section(
        ft.H2(
            config.text("chat", "page_title", "Experience Chat"),
            cls="section-title chat-page-title",
        ),
        ft.Div(
            *ChatWidget.full_page(),
            cls="container chat-page-container",
        ),
        cls="chat-page-section",
    )

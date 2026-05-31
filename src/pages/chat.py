import fasthtml.common as ft

from src.components.chat.widget import ChatWidget


def build_chat_page():
    return ft.Section(
        ft.H2("Experience Chat", cls="section-title chat-page-title"),
        ft.Div(
            *ChatWidget.full_page(),
            cls="container chat-page-container",
        ),
        cls="chat-page-section",
    )

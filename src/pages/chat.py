import fasthtml.common as ft

from src.components.chat.widget import ChatWidget


def build_chat_page():
    return ft.Section(
        ft.H2("Experience Chat", cls="section-title"),
        ft.Div(
            *ChatWidget.full_page(),
            cls="container section",
        ),
    )

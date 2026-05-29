import fasthtml.common as ft
from src.components.ui import Navigation, SiteFooter, MobileTabBar
from src.components.chat.widget import ChatWidget


def render_page(title: str, *content):
    return (
        ft.Title(title),
        Navigation(),
        # Subtle asteroid-belt canvas (fixed, behind content)
        ft.Canvas(id="asteroid-belt"),
        *content,
        MobileTabBar(),
        ChatWidget.professional_mode(),  # Add RAG chat widget to all pages
        SiteFooter(),
    )

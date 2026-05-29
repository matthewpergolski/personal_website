import fasthtml.common as ft
from src.components.ui import Navigation, SiteFooter, MobileTabBar
from src.components.chat.widget import ChatWidget


def render_page(title: str, *content, include_chat: bool = True):
    return (
        ft.Title(title),
        Navigation(),
        # Subtle asteroid-belt canvas (fixed, behind content)
        ft.Canvas(id="asteroid-belt"),
        *content,
        MobileTabBar(),
        *(ChatWidget.professional_mode() if include_chat else ()),
        SiteFooter(),
    )

import fasthtml.common as ft
from src.components.ui import Navigation, SiteFooter


def render_page(title: str, *content):
    return (
        ft.Title(title),
        Navigation(),
        # Subtle asteroid-belt canvas (fixed, behind content)
        ft.Canvas(id="asteroid-belt"),
        *content,
        SiteFooter(),
    )

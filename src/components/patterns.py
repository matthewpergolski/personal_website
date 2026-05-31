from __future__ import annotations

import fasthtml.common as ft


def css_classes(*values: str | None) -> str:
    return " ".join(value for value in values if value)


def Card(*children, cls: str | None = None):
    return ft.Div(*children, cls=css_classes("card", cls))


def ChipList(items, *, cls: str | None = None):
    return ft.Div(
        *[ft.Span(item, cls="chip") for item in items],
        cls=css_classes("chips", cls),
    )


def MutedText(*children, cls: str | None = None):
    return ft.P(*children, cls=css_classes("muted", cls))


def BulletList(items, *, limit: int | None = None, cls: str | None = None):
    visible_items = list(items or [])
    if limit is not None:
        visible_items = visible_items[:limit]
    return ft.Ul(
        *[ft.Li(item) for item in visible_items],
        cls=css_classes("bullet-list", cls),
    )


def InlineActions(*children, cls: str | None = None):
    return ft.Div(*children, cls=css_classes("inline-actions", cls))


def StatCard(value, label: str):
    return ft.Div(
        ft.Div(str(value), cls="stat-num"),
        ft.Div(label, cls="stat-label"),
        cls="stat-card",
    )


def TimelineItem(title: str, subtitle: str, bullets):
    return ft.Div(
        ft.H4(title),
        MutedText(subtitle),
        BulletList(bullets, limit=3, cls="bullet-list-tight"),
        cls="timeline-item",
    )


def IconLink(label: str, href: str | None, *, target: str = "_blank"):
    return ft.A(
        label,
        href=href,
        cls="icon-link",
        target=target,
        rel="noopener noreferrer",
    )

import re
from datetime import datetime
from dataclasses import dataclass

import fasthtml.common as ft
from fasthtml.common import Nav, Div, A, Button, Section, H1, P, Img, Footer, Span

from src.config import get_config


@dataclass(frozen=True)
class NavItem:
    label: str
    href: str
    tab_id: str
    icon: str


NAV_ITEMS = (
    NavItem("Home", "/", "tab-home", "🏠"),
    NavItem("About", "/about", "tab-about", "👤"),
    NavItem("Projects", "/projects", "tab-projects", "🧩"),
    NavItem("Resume", "/resume", "tab-resume", "📄"),
    NavItem("Contact", "/contact", "tab-contact", "✉️"),
    NavItem("Chat", "/chat", "tab-chat", "💬"),
)


def ensure_url(url: str | None) -> str | None:
    """Ensure external links have a scheme (https)."""
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://" + url.lstrip("/")


def display_role_title(title: str | None) -> str:
    if not title:
        return "AI/ML Engineer"
    return re.sub(r"\s*\([^)]*hours per week[^)]*\)", "", title).strip()


def display_skill_category(category: str | None) -> str:
    labels = {
        "Application Software": "Programming & Data",
        "Production Software": "Cloud & Enterprise Platforms",
        "Other": "Productivity & Analysis",
    }
    if not category:
        return "Skills"
    return labels.get(category, category)


def Navigation():
    config = get_config()
    gh_user = config.github_username
    gh_url = ensure_url(f"https://github.com/{gh_user}") if gh_user else None
    brand_avatar = f"https://github.com/{gh_user}.png?size=40" if gh_user else None
    li_url = ensure_url(config.linkedin_url)
    return Nav(
        Div(
            Div(
                A(
                    *(
                        [Img(src=brand_avatar, alt="Avatar", cls="brand-logo")]
                        if brand_avatar
                        else []
                    ),
                    Span(config.brand_initials, cls="brand-initials"),
                    Span(config.brand_subtitle, cls="brand-sub"),
                    href="/",
                    cls="nav-brand",
                ),
                Button(
                    "☰",
                    id="nav-toggle",
                    cls="nav-toggle",
                    aria_label="Toggle navigation",
                    aria_controls="nav-links",
                    aria_expanded="false",
                    title="Menu",
                ),
                Div(
                    Button(
                        "×", id="nav-close", cls="nav-close", aria_label="Close menu"
                    ),
                    *[
                        A(item.label, href=item.href, cls="nav-link")
                        for item in NAV_ITEMS
                    ],
                    id="nav-links",
                    cls="nav-links",
                ),
                Div(
                    *(
                        (
                            [
                                A(
                                    "GitHub",
                                    href=gh_url,
                                    cls="icon-link",
                                    target="_blank",
                                    rel="noopener noreferrer",
                                )
                            ]
                            if gh_url
                            else []
                        )
                        + (
                            [
                                A(
                                    "LinkedIn",
                                    href=li_url,
                                    cls="icon-link",
                                    target="_blank",
                                    rel="noopener noreferrer",
                                )
                            ]
                            if li_url
                            else []
                        )
                        + [
                            Button(
                                "🌗",
                                id="theme-toggle",
                                cls="icon-link theme-toggle",
                                title="Toggle theme",
                            )
                        ]
                    ),
                    cls="nav-actions",
                ),
                cls="nav-container container",
            ),
            cls="nav",
        )
    )


def HeroSection(profile: dict | None = None, experience: dict | None = None):
    config = get_config()
    name = (profile or {}).get("name") or config.owner_name
    gh_user = config.github_username
    summary = (experience or {}).get("summary")
    bio = summary or (profile or {}).get("bio") or config.site_description
    avatar = (profile or {}).get("avatar_url") or (
        f"https://github.com/{gh_user}.png?size=320" if gh_user else None
    )
    current_role = ((experience or {}).get("experience") or [{}])[0]
    return Section(
        Div(
            Div(
                Div(config.hero_kicker, cls="hero-kicker"),
                H1(name, cls="hero-title"),
                P(config.site_title, cls="hero-subtitle"),
                P(bio, cls="hero-description"),
                Div(
                    ft.A(config.hero_primary_cta, href="/projects", cls="btn"),
                    ft.A(config.hero_chat_cta, href="/chat", cls="btn btn-secondary"),
                    cls="hero-actions",
                ),
                cls="hero-copy",
            ),
            Div(
                *(
                    [Img(src=avatar, alt=name, cls="avatar avatar-lg")]
                    if avatar
                    else []
                ),
                Div(
                    Span("Current Role", cls="hero-meta-label"),
                    Span(
                        display_role_title(current_role.get("title")),
                        cls="hero-meta-main",
                    ),
                    Span(
                        f"{current_role.get('company', 'Portfolio')} • {current_role.get('period', '')}",
                        cls="hero-meta-sub",
                    ),
                    cls="hero-current",
                ),
                cls="hero-aside",
            ),
            cls="container hero-layout",
        ),
        cls="hero-section",
    )


def SiteFooter():
    config = get_config()
    year = datetime.now().year
    return Footer(
        Div(
            P(f"© {year} {config.owner_name}. Built with FastHTML."),
            P(config.footer_tagline),
            cls="container",
        ),
        cls="footer",
    )


def MobileTabBar():
    """Fixed bottom tab bar for mobile only (CSS controls visibility)."""
    return Div(
        *[
            A(
                Span(item.icon, cls="tab-ico"),
                Span(item.label, cls="tab-txt"),
                href=item.href,
                id=item.tab_id,
                cls="tab",
            )
            for item in NAV_ITEMS
        ],
        id="mobile-tabbar",
        cls="mobile-tabbar",
    )

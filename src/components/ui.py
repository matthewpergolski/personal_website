import os
import re
from datetime import datetime
import fasthtml.common as ft
from fasthtml.common import Nav, Div, A, Button, Section, H1, P, Img, Footer, Span


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
    gh_user = os.getenv("GITHUB_USERNAME")
    gh_url = ensure_url(f"https://github.com/{gh_user}") if gh_user else None
    brand_avatar = f"https://github.com/{gh_user}.png?size=40" if gh_user else None
    li_url = ensure_url(os.getenv("LINKEDIN_URL"))
    return Nav(
        Div(
            Div(
                A(
                    *(
                        [Img(src=brand_avatar, alt="Avatar", cls="brand-logo")]
                        if brand_avatar
                        else []
                    ),
                    Span("MLP", cls="brand-initials"),
                    Span("Portfolio", cls="brand-sub"),
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
                    A("Home", href="/", cls="nav-link"),
                    A("About", href="/about", cls="nav-link"),
                    A("Projects", href="/projects", cls="nav-link"),
                    A("Resume", href="/resume", cls="nav-link"),
                    A("Contact", href="/contact", cls="nav-link"),
                    A("Chat", href="/chat", cls="nav-link"),
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
    name = (profile or {}).get("name") or "Matthew L. Pergolski"
    gh_user = os.getenv("GITHUB_USERNAME")
    summary = (experience or {}).get("summary")
    bio = (
        summary
        or (profile or {}).get("bio")
        or os.getenv("SITE_DESCRIPTION", "AI/ML engineer and data scientist")
    )
    avatar = (profile or {}).get("avatar_url") or (
        f"https://github.com/{gh_user}.png?size=320" if gh_user else None
    )
    current_role = ((experience or {}).get("experience") or [{}])[0]
    return Section(
        Div(
            Div(
                Div("AI/ML Engineering Portfolio", cls="hero-kicker"),
                H1(name, cls="hero-title"),
                P(
                    os.getenv("SITE_TITLE", "AI/ML Engineer & Data Scientist"),
                    cls="hero-subtitle",
                ),
                P(bio, cls="hero-description"),
                Div(
                    ft.A("View Projects", href="/projects", cls="btn"),
                    ft.A("Experience Chat", href="/chat", cls="btn btn-secondary"),
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
    year = datetime.now().year
    return Footer(
        Div(
            P(f"© {year} Matthew L. Pergolski. Built with FastHTML."),
            P("Data Science • Machine Learning • AI Engineering"),
            cls="container",
        ),
        cls="footer",
    )


def MobileTabBar():
    """Fixed bottom tab bar for mobile only (CSS controls visibility)."""
    return Div(
        A(
            Span("🏠", cls="tab-ico"),
            Span("Home", cls="tab-txt"),
            href="/",
            id="tab-home",
            cls="tab",
        ),
        A(
            Span("📦", cls="tab-ico"),
            Span("About", cls="tab-txt"),
            href="/about",
            id="tab-about",
            cls="tab",
        ),
        A(
            Span("👤", cls="tab-ico"),
            Span("Projects", cls="tab-txt"),
            href="/projects",
            id="tab-projects",
            cls="tab",
        ),
        A(
            Span("📄", cls="tab-ico"),
            Span("Resume", cls="tab-txt"),
            href="/resume",
            id="tab-resume",
            cls="tab",
        ),
        A(
            Span("✉️", cls="tab-ico"),
            Span("Contact", cls="tab-txt"),
            href="/contact",
            id="tab-contact",
            cls="tab",
        ),
        A(
            Span("💬", cls="tab-ico"),
            Span("Chat", cls="tab-txt"),
            href="/chat",
            id="tab-chat",
            cls="tab",
        ),
        id="mobile-tabbar",
        cls="mobile-tabbar",
    )

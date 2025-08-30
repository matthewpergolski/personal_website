import os
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


def Navigation():
    gh_user = os.getenv("GITHUB_USERNAME")
    gh_url = ensure_url(f"https://github.com/{gh_user}") if gh_user else None
    brand_avatar = f"https://github.com/{gh_user}.png?size=40" if gh_user else None
    li_url = ensure_url(os.getenv("LINKEDIN_URL"))
    return Nav(
        Div(
            Div(
                A(
                    *( [Img(src=brand_avatar, alt="Avatar", cls="brand-logo")] if brand_avatar else [] ),
                    Span("MLP", cls="brand-initials"),
                    Span("Portfolio", cls="brand-sub"),
                    href="/",
                    cls="nav-brand",
                ),
                Button("☰", id="nav-toggle", cls="nav-toggle", aria_label="Toggle navigation", aria_controls="nav-links", aria_expanded="false", title="Menu"),
                Div(
                    Button("×", id="nav-close", cls="nav-close", aria_label="Close menu"),
                    A("Home", href="/", cls="nav-link"),
                    A("Projects", href="/projects", cls="nav-link"),
                    A("About", href="/about", cls="nav-link"),
                    A("Resume", href="/resume", cls="nav-link"),
                    A("Contact", href="/contact", cls="nav-link"),
                    id="nav-links", cls="nav-links",
                ),
                Div(
                    *(
                        ([A("GitHub", href=gh_url, cls="icon-link", target="_blank", rel="noopener noreferrer")] if gh_url else [])
                        + ([A("LinkedIn", href=li_url, cls="icon-link", target="_blank", rel="noopener noreferrer")] if li_url else [])
                        + [Button("🌗", id="theme-toggle", cls="icon-link theme-toggle", title="Toggle theme")]
                    ),
                    cls="nav-actions",
                ),
                cls="nav-container container",
            ),
            cls="nav",
        )
    )


def HeroSection(profile: dict | None = None):
    name = (profile or {}).get("name") or "Matthew L. Pergolski"
    bio = (profile or {}).get("bio") or os.getenv(
        "SITE_DESCRIPTION", "AI/ML Engineer & Data Scientist"
    )
    avatar = (profile or {}).get("avatar_url")
    return Section(
        Div(
            *([Img(src=avatar, alt=name, cls="avatar avatar-lg")] if avatar else []),
            H1(name, cls="hero-title"),
            P(os.getenv("SITE_TITLE", "Data Scientist & AI/ML Engineer"), cls="hero-subtitle"),
            P(bio, cls="hero-description"),
            Div(
                ft.A("View My Work", href="/projects", cls="btn"),
                ft.A("Get In Touch", href="/contact", cls="btn btn-secondary"),
                style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;",
            ),
            cls="container",
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

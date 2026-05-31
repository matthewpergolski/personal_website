from __future__ import annotations

import fasthtml.common as ft
from fasthtml.common import A, Img

from src.components.ui import display_role_title, display_skill_category, ensure_url
from src.config import SiteConfig


def build_about_page(data: dict, profile: dict | None, config: SiteConfig):
    summary = (
        data.get("summary")
        or config.site_description
        or "AI/ML engineer turning data into product value."
    )
    avatar = (profile or {}).get("avatar_url") or (
        f"https://github.com/{config.github_username}.png"
        if config.github_username
        else None
    )

    highlights = data.get("highlights") or []
    experience = data.get("experience", [])[:3]
    snapshot = data.get("snapshot") or {}
    years = snapshot.get("years") or None
    public_repos = (profile or {}).get("public_repos") or 0
    followers = (profile or {}).get("followers") or 0

    skills = data.get("skills") or {}
    skill_cards = [
        ft.Div(
            ft.H4(display_skill_category(category)),
            ft.Div(*[ft.Span(skill, cls="chip") for skill in items], cls="chips"),
            cls="card",
        )
        for category, items in skills.items()
    ]

    hero = ft.Div(
        *([Img(src=avatar, alt="Avatar", cls="avatar")] if avatar else []),
        ft.Div(
            ft.H3("Professional Background"),
            ft.P(summary),
            ft.Div(
                A("View Projects", href="/projects", cls="btn"),
                A("Download Resume", href="/resume/download", cls="btn btn-secondary"),
                cls="hero-cta",
            ),
        ),
        cls="about-hero",
    )

    left_col = ft.Div(
        ft.H3("Highlights"),
        ft.Ul(
            *[ft.Li(highlight) for highlight in highlights],
            style="margin-left:1.25rem; margin-bottom:1.25rem;",
        ),
        ft.H3("Recent Roles"),
        ft.Div(
            *[
                ft.Div(
                    ft.H4(display_role_title(role.get("title"))),
                    ft.P(
                        f"{role.get('company', 'Company')} • {role.get('period', '')}",
                        style="color: var(--secondary-color);",
                    ),
                    ft.Ul(
                        *[ft.Li(bullet) for bullet in (role.get("bullets") or [])[:3]],
                        style="margin-left:1.25rem; margin-bottom:.75rem;",
                    ),
                    cls="timeline-item",
                )
                for role in experience
            ],
            cls="timeline",
        ),
        cls="card",
    )

    right_col = ft.Div(
        ft.H3("Snapshot"),
        ft.Div(
            *(
                [
                    ft.Div(
                        ft.Div(str(years), cls="stat-num"),
                        ft.Div("Years", cls="stat-label"),
                        cls="stat-card",
                    )
                ]
                if years
                else []
            ),
            ft.Div(
                ft.Div(str(public_repos), cls="stat-num"),
                ft.Div("Public Repos", cls="stat-label"),
                cls="stat-card",
            ),
            *(
                [
                    ft.Div(
                        ft.Div(str(followers), cls="stat-num"),
                        ft.Div("Followers", cls="stat-label"),
                        cls="stat-card",
                    )
                ]
                if followers > 0
                else []
            ),
            cls="stats-grid",
            style="margin-bottom:1rem;",
        ),
        ft.H3("Links"),
        ft.Div(
            A(
                "💼 LinkedIn",
                href=ensure_url(config.linkedin_url),
                cls="icon-link",
                target="_blank",
                rel="noopener noreferrer",
            ),
            A(
                "🐙 GitHub",
                href=ensure_url(f"https://github.com/{config.github_username}")
                if config.github_username
                else "https://github.com/",
                cls="icon-link",
                target="_blank",
                rel="noopener noreferrer",
            ),
            A(
                "⬇️ Resume",
                href="/resume/download",
                cls="icon-link",
                target="_blank",
                rel="noopener noreferrer",
            ),
            style="display:flex; gap:.5rem; flex-wrap:wrap;",
        ),
        cls="card",
    )

    return ft.Section(
        ft.H2("About Me", cls="section-title"),
        hero,
        ft.Div(left_col, right_col, cls="grid-2-1", style="margin-top:1.5rem;"),
        ft.Div(*skill_cards, cls="card-grid", style="margin-top:1.5rem;"),
        cls="container section",
    )


def build_resume_page(data: dict):
    experience = data.get("experience", [])
    education = data.get("education", [])
    skills = data.get("skills", {})

    experience_blocks = []
    if experience:
        experience_blocks.append(ft.H3("Experience"))
        for role in experience:
            bullets = role.get("bullets") or []
            experience_blocks.append(
                ft.Div(
                    ft.H4(display_role_title(role.get("title"))),
                    ft.P(
                        f"{role.get('company', 'Company')} • {role.get('period', '')}",
                        style="color: var(--secondary-color);",
                    ),
                    ft.Ul(
                        *[ft.Li(bullet) for bullet in bullets],
                        style="margin-left: 1.5rem; margin-bottom: 1.25rem;",
                    ),
                )
            )
    if education:
        experience_blocks.append(ft.H3("Education"))
        for item in education:
            experience_blocks.append(
                ft.Div(
                    ft.H4(item.get("degree", "Degree")),
                    ft.P(
                        (
                            f"{item.get('institution', 'University')} • "
                            f"{item.get('period', '')}"
                        ),
                        style="color: var(--secondary-color);",
                    ),
                )
            )
    left_col = ft.Div(*experience_blocks, cls="card")

    skill_blocks = []
    if skills:
        skill_blocks.append(ft.H3("Skills"))
        for category, items in skills.items():
            skill_blocks.append(ft.H4(display_skill_category(category)))
            skill_blocks.append(
                ft.Div(
                    *[ft.Span(skill, cls="chip") for skill in items],
                    cls="chips",
                    style="margin-bottom: .75rem;",
                )
            )
    right_col = ft.Div(*skill_blocks, cls="card")

    return ft.Section(
        ft.H2("Professional Resume", cls="section-title"),
        ft.Div(
            ft.Div(
                ft.H3("Want the PDF version?"),
                ft.P(
                    "Download the formatted resume, or browse the expanded "
                    "experience details below."
                ),
            ),
            ft.A("Download Resume", href="/resume/download", cls="btn"),
            cls="resume-callout",
        ),
        ft.Div(left_col, right_col, cls="grid-2-1"),
        cls="container section",
    )

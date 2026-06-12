from __future__ import annotations

import fasthtml.common as ft
from fasthtml.common import A, Img

from src.components.patterns import (
    BulletList,
    Card,
    ChipList,
    IconLink,
    InlineActions,
    MutedText,
    StatCard,
    TimelineItem,
)
from src.components.ui import display_role_title, display_skill_category, ensure_url
from src.config import SiteConfig


def build_about_page(data: dict, profile: dict | None, config: SiteConfig):
    summary = data.get("summary") or config.site_description
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
        Card(
            ft.H4(display_skill_category(category)),
            ChipList(items),
        )
        for category, items in skills.items()
    ]

    hero = ft.Div(
        *([Img(src=avatar, alt="Avatar", cls="avatar")] if avatar else []),
        ft.Div(
            ft.H3(config.text("about", "background_title", "Professional Background")),
            ft.P(summary),
            ft.Div(
                A(
                    config.text("about", "primary_cta", "View Projects"),
                    href="/projects",
                    cls="btn",
                ),
                A(
                    config.text("about", "resume_cta", "Download Resume"),
                    href="/resume/download",
                    cls="btn btn-secondary",
                ),
                cls="hero-cta",
            ),
        ),
        cls="about-hero",
    )

    highlights_card = Card(
        ft.H3(config.text("about", "highlights_title", "Highlights")),
        BulletList(highlights, cls="bullet-list-loose"),
    )

    roles_card = Card(
        ft.H3(config.text("about", "roles_title", "Recent Roles")),
        ft.Div(
            *[
                TimelineItem(
                    display_role_title(role.get("title")),
                    f"{role.get('company', 'Company')} • {role.get('period', '')}",
                    role.get("bullets") or [],
                )
                for role in experience
            ],
            cls="timeline",
        ),
    )

    left_col = ft.Div(highlights_card, roles_card, cls="about-content-stack")

    right_col = Card(
        ft.H3(config.text("about", "snapshot_title", "Snapshot")),
        ft.Div(
            *([StatCard(years, "Years")] if years else []),
            StatCard(
                public_repos,
                config.text("about", "public_repos_label", "Public Repos"),
            ),
            *([StatCard(followers, "Followers")] if followers > 0 else []),
            cls="stats-grid stats-grid-spaced",
        ),
        ft.H3(config.text("about", "links_title", "Links")),
        InlineActions(
            IconLink(
                config.text("about", "linkedin_label", "💼 LinkedIn"),
                href=ensure_url(config.linkedin_url),
            ),
            IconLink(
                config.text("about", "github_label", "🐙 GitHub"),
                href=ensure_url(f"https://github.com/{config.github_username}")
                if config.github_username
                else "https://github.com/",
            ),
            IconLink(
                config.text("about", "resume_link_label", "⬇️ Resume"),
                href="/resume/download",
            ),
        ),
    )

    return ft.Section(
        ft.H2(config.text("about", "title", "About Me"), cls="section-title"),
        hero,
        ft.Div(left_col, right_col, cls="grid-2-1 stack-gap"),
        ft.Div(*skill_cards, cls="card-grid stack-gap"),
        cls="container section",
    )


def build_resume_page(data: dict, config: SiteConfig):
    experience = data.get("experience", [])
    education = data.get("education", [])
    skills = data.get("skills", {})

    experience_blocks = []
    if experience:
        experience_blocks.append(
            ft.H3(config.text("resume", "experience_title", "Experience"))
        )
        for role in experience:
            bullets = role.get("bullets") or []
            experience_blocks.append(
                ft.Div(
                    ft.H4(display_role_title(role.get("title"))),
                    MutedText(
                        (
                            f"{role.get('company', config.text('resume', 'fallback_company', 'Company'))} "
                            f"• {role.get('period', '')}"
                        ),
                    ),
                    BulletList(bullets, cls="bullet-list-loose"),
                )
            )
    if education:
        experience_blocks.append(
            ft.H3(config.text("resume", "education_title", "Education"))
        )
        for item in education:
            experience_blocks.append(
                ft.Div(
                    ft.H4(
                        item.get(
                            "degree", config.text("resume", "fallback_degree", "Degree")
                        )
                    ),
                    MutedText(
                        (
                            f"{item.get('institution', config.text('resume', 'fallback_institution', 'University'))} • "
                            f"{item.get('period', '')}"
                        ),
                    ),
                )
            )
    left_col = Card(*experience_blocks)

    skill_blocks = []
    if skills:
        skill_blocks.append(ft.H3(config.text("resume", "skills_title", "Skills")))
        for category, items in skills.items():
            skill_blocks.append(ft.H4(display_skill_category(category)))
            skill_blocks.append(ChipList(items, cls="chips-spaced"))
    right_col = Card(*skill_blocks)

    return ft.Section(
        ft.H2(
            config.text("resume", "title", "Professional Resume"), cls="section-title"
        ),
        ft.Div(
            ft.Div(
                ft.H3(config.resume_pdf_prompt),
                ft.P(config.resume_pdf_description),
            ),
            ft.A(
                config.text("resume", "download_cta", "Download Resume"),
                href="/resume/download",
                cls="btn",
            ),
            cls="resume-callout",
        ),
        ft.Div(left_col, right_col, cls="grid-2-1"),
        cls="container section",
    )

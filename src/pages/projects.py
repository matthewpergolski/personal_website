from __future__ import annotations

from fasthtml.common import A, Div, H2, H3, P, Section, Span


def build_projects_page(
    projects_data: list[dict] | None,
    profile: dict | None,
    github_username: str | None,
):
    if not projects_data:
        return Div(
            H2("Projects", cls="section-title"),
            Div(
                P(
                    "Unable to load projects at this time. Please check back later.",
                    cls="error",
                ),
                cls="container",
            ),
        )

    github_url = (profile or {}).get("html_url") or (
        f"https://github.com/{github_username}" if github_username else None
    )
    project_cards = [
        Div(
            H3(project["name"].replace("_", "_\u200b"), cls="card-title"),
            P(f"Language: {project['language']}", cls="card-subtitle"),
            P(project["description"], cls="card-description"),
            (
                Div(
                    *[
                        Span(topic, cls="chip")
                        for topic in (project.get("topics") or [])
                    ],
                    cls="chips",
                )
                if project.get("topics")
                else Div()
            ),
            Div(
                A("View Project", href=project["url"], cls="btn", target="_blank"),
                P(
                    f"⭐ {project['stars']} • Updated {project['updated']}",
                    style=(
                        "margin-top: 1rem; font-size: 0.9rem; "
                        "color: var(--secondary-color);"
                    ),
                ),
                style=(
                    "display: flex; justify-content: space-between; "
                    "align-items: center; flex-wrap: wrap; gap: 1rem;"
                ),
            ),
            cls="card",
        )
        for project in projects_data
    ]

    return Section(
        H2("Featured Projects", cls="section-title"),
        Div(
            P(
                f"Showing {len(projects_data)} repositories",
                (" • " if github_url else ""),
                (
                    A(
                        "View GitHub Profile →",
                        href=github_url,
                        target="_blank",
                        rel="noopener noreferrer",
                    )
                    if github_url
                    else ""
                ),
                style=(
                    "text-align:center;color:var(--secondary-color);margin-top:-1.5rem;"
                ),
            ),
            cls="container",
        ),
        Div(Div(*project_cards, cls="card-grid"), cls="container"),
        cls="section",
    )


def build_projects_error(error: Exception):
    return Div(
        H2("Projects", cls="section-title"),
        Div(P(f"Error loading projects: {error}", cls="error"), cls="container"),
    )

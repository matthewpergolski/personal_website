from __future__ import annotations

import json

from fasthtml.common import Button, Div, H2, P, Script, Section, Span

from src.assets.loader import load_asset_text
from src.components.ui import HeroSection


def _top_language_items(values: dict | None, limit: int = 8) -> list[tuple[str, int]]:
    items = sorted(
        [(name, value) for name, value in (values or {}).items() if value > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    top = items[:limit]
    if len(items) > limit:
        top.append(("Others", sum(v for _, v in items[limit:])))
    return top


def _repo_language_counts(repos: list[dict] | None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for repo in repos or []:
        language = repo.get("language") or "Other"
        counts[language] = counts.get(language, 0) + 1
    return counts


def build_home_page(
    profile: dict | None,
    lang_bytes: dict | None,
    repos: list[dict] | None,
    experience_data: dict | None,
    github_username: str | None,
):
    experience_data = experience_data or {}
    highlights = [str(item) for item in experience_data.get("highlights", [])[:6]]

    byte_items = _top_language_items(lang_bytes)
    repo_items = _top_language_items(_repo_language_counts(repos))
    labels_bytes = [name for name, _ in byte_items]
    values_bytes = [value for _, value in byte_items]
    labels_repos = [name for name, _ in repo_items]
    values_repos = [value for _, value in repo_items]

    highlights_section = (
        Section(
            H2("Highlights", cls="section-title"),
            Div(
                *[
                    Div(
                        Span(f"{idx:02d}", cls="highlight-index"),
                        P(highlight, cls="highlight-copy"),
                        cls="highlight-card",
                    )
                    for idx, highlight in enumerate(highlights[:3], start=1)
                ],
                cls="container highlight-grid",
            ),
            cls="section",
        )
        if highlights
        else Div()
    )

    chart_section = (
        Section(
            H2("Tech Stack Snapshot", cls="section-title"),
            Div(
                Div(
                    Div(
                        Div(
                            Span("View", cls="chart-control-label"),
                            Div(
                                Button(
                                    "Donut",
                                    id="chart-donut",
                                    cls="icon-link chart-option",
                                    title="Shows proportional share of the tech stack.",
                                    data_chart_tip="Shows proportional share of the tech stack.",
                                ),
                                Button(
                                    "Bar",
                                    id="chart-bar",
                                    cls="icon-link chart-option",
                                    title="Compares absolute totals across languages.",
                                    data_chart_tip="Compares absolute totals across languages.",
                                ),
                                Button(
                                    "Treemap",
                                    id="chart-tree",
                                    cls="icon-link chart-option",
                                    title="Shows mix and relative size in one compact map.",
                                    data_chart_tip="Shows mix and relative size in one compact map.",
                                ),
                                cls="chart-segment",
                            ),
                            cls="chart-control-group",
                        ),
                        Div(
                            Span("Metric", cls="chart-control-label"),
                            Div(
                                Button(
                                    "Repos",
                                    id="metric-repos",
                                    cls="icon-link chart-option",
                                    title="Counts how often each language appears across repositories.",
                                    data_chart_tip="Counts how often each language appears across repositories.",
                                ),
                                Button(
                                    "Bytes",
                                    id="metric-bytes",
                                    cls="icon-link chart-option",
                                    title="Weights languages by code volume.",
                                    data_chart_tip="Weights languages by code volume.",
                                ),
                                cls="chart-segment",
                            ),
                            cls="chart-control-group",
                        ),
                        Button(
                            "Download PNG",
                            id="chart-export",
                            cls="icon-link chart-export",
                            title="Download chart as PNG",
                        ),
                        cls="chart-toolbar",
                    ),
                    P(id="chart-hint", cls="chart-hint"),
                    Div(id="lang-chart", cls="chart-canvas"),
                    Div(id="chart-key", cls="chart-key"),
                    cls="chart-shell",
                ),
            ),
            Script(
                json.dumps(
                    {
                        "labelsBytes": labels_bytes,
                        "valuesBytes": values_bytes,
                        "labelsRepos": labels_repos,
                        "valuesRepos": values_repos,
                        "githubUsername": github_username or "",
                    }
                ),
                id="tech-stack-chart-data",
                type="application/json",
            ),
            Script(
                load_asset_text("tech-stack-chart.js"),
            ),
            cls="section",
        )
        if labels_bytes and values_bytes
        else Div()
    )

    return (
        HeroSection(profile, experience_data),
        highlights_section,
        chart_section,
    )

from pathlib import Path

from scripts.check_pr_body import check_pr_body


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "pr_bodies"
REQUIRED_HEADINGS = (
    "TL;DR",
    "How it works",
    "Summary",
    "Files changed",
    "How to test",
    "Review",
)


def test_missing_sections_names_each_heading_to_add():
    body = (FIXTURES / "missing_sections.md").read_text(encoding="utf-8")

    problems = check_pr_body(body)

    for heading in REQUIRED_HEADINGS:
        assert f'pr-body: Add a markdown heading "{heading}".' in problems
    assert "pr-body: Add a fenced code block that starts with ```mermaid." in problems

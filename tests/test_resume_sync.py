import json
from pathlib import Path

from scripts.sync_resume_content import (
    normalize_source_url,
    parse_resume_text,
)


FIXTURE = Path(__file__).parent / "fixtures" / "resume_sample.txt"


def test_parse_resume_text_into_experience_schema():
    data = parse_resume_text(FIXTURE.read_text(), existing={"snapshot": {"years": 6}})

    assert data["summary"].startswith("Data scientist and AI/ML engineer")
    assert data["highlights"][0] == "Built ML models serving roughly 100K users"
    assert (
        data["experience"][0]["title"]
        == "Senior Automation/Artificial Intelligence Engineer"
    )
    assert data["experience"][0]["company"] == "Lockheed Martin"
    assert data["experience"][0]["period"] == "2025 - Present"
    assert "document-aware AI search tool" in data["experience"][0]["bullets"][1]
    assert data["education"][0]["institution"] == "Syracuse University"
    assert data["skills"]["Programming"] == ["Python", "R", "SQL"]
    assert data["snapshot"] == {"years": 6}
    assert "resume_text" in data
    assert data["resume_source"]["parser"] == "scripts/sync_resume_content.py"


def test_google_docs_url_normalizes_to_text_export():
    url = "https://docs.google.com/document/d/abc123/edit?tab=t.0"
    assert normalize_source_url(url) == (
        "https://docs.google.com/document/d/abc123/export?format=txt"
    )


def test_parse_resume_text_preserves_timestamp_when_content_is_unchanged():
    text = FIXTURE.read_text()
    initial = parse_resume_text(
        text,
        existing={"snapshot": {"years": 6}},
        source_url="https://example.com/resume.txt",
        content_type="text/plain",
    )
    initial["resume_source"]["synced_at"] = "2026-05-01T12:00:00+00:00"

    parsed = parse_resume_text(
        text,
        existing=initial,
        source_url="https://example.com/resume.txt",
        content_type="text/plain",
    )

    assert parsed["resume_source"]["synced_at"] == "2026-05-01T12:00:00+00:00"


def test_parsed_resume_json_is_serializable():
    data = parse_resume_text(FIXTURE.read_text())
    json.dumps(data)

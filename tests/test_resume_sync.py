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


def test_parse_resume_text_handles_company_heading_then_title():
    text = """
Work Experience
Lockheed Martin, Remote 04/25-Present
A/AI Machine Learning Engineer Senior (40 hours per week, full-time schedule)
* Led development of machine learning models
Lockheed Martin, Orlando, FL 01/18-11/19 Manufacturing Planner Associate
* Maintained production systems integrity

Additional Information
Software
* Application Software: R, Python, SQL
Other Qualifications
* Lean Six Sigma Green Belt Certified
"""

    data = parse_resume_text(text)

    assert data["experience"] == [
        {
            "title": "A/AI Machine Learning Engineer Senior (40 hours per week, full-time schedule)",
            "company": "Lockheed Martin",
            "period": "04/25-Present",
            "bullets": ["Led development of machine learning models"],
            "location": "Remote",
        },
        {
            "title": "Manufacturing Planner Associate",
            "company": "Lockheed Martin",
            "period": "01/18-11/19",
            "bullets": ["Maintained production systems integrity"],
            "location": "Orlando, FL",
        },
    ]
    assert "Software" not in {entry["title"] for entry in data["experience"]}
    assert data["skills"]["Application Software"] == ["R", "Python", "SQL"]


def test_parse_resume_text_redacts_contact_details_from_raw_resume_text():
    text = """
Matthew L. Pergolski
matthew@example.com | 555-123-4567
Professional Summary
Data scientist focused on useful systems.
"""

    data = parse_resume_text(text)

    assert "matthew@example.com" not in data["resume_text"]
    assert "555-123-4567" not in data["resume_text"]
    assert "[email redacted]" in data["resume_text"]
    assert "[phone redacted]" in data["resume_text"]


def test_parse_resume_text_groups_education_heading_with_degree():
    text = """
Education
Syracuse University, Syracuse, NY Conferred 05/24
M.S., Applied Data Science
* Grade: 4.0
University of Wisconsin-Eau Claire, Eau Claire, WI Conferred 12/17
B.B.A., Operations/Supply Chain Management
* Graduated Cum Laude
"""

    data = parse_resume_text(text)

    assert data["education"] == [
        {
            "degree": "M.S., Applied Data Science",
            "institution": "Syracuse University, Syracuse, NY",
            "period": "05/24",
        },
        {
            "degree": "B.B.A., Operations/Supply Chain Management",
            "institution": "University of Wisconsin-Eau Claire, Eau Claire, WI",
            "period": "12/17",
        },
    ]


def test_parsed_resume_json_is_serializable():
    data = parse_resume_text(FIXTURE.read_text())
    json.dumps(data)

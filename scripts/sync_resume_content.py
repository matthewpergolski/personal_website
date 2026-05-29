#!/usr/bin/env python3
"""Sync resume text into data/experience.json.

The app reads committed structured JSON at runtime. This script is the bridge
from an editable resume source, such as Google Docs, Drive-hosted PDF/DOCX, or
plain text, into that stable data file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from xml.etree import ElementTree


SECTION_ALIASES = {
    "summary": {
        "summary",
        "profile",
        "professional summary",
        "career summary",
        "objective",
    },
    "highlights": {
        "highlights",
        "selected highlights",
        "career highlights",
        "key achievements",
        "achievements",
    },
    "experience": {
        "experience",
        "professional experience",
        "work experience",
        "employment",
        "employment history",
    },
    "education": {"education", "academic background"},
    "skills": {
        "skills",
        "technical skills",
        "core skills",
        "tools",
        "technologies",
    },
}


BULLET_PREFIX_RE = re.compile(r"^[\s\-\*\u2022\u25e6\u2013\u2014]+")
DATE_RE = re.compile(
    r"(?P<period>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s*"
    r"\d{4}\s*(?:-|–|—|to)\s*(?:Present|Current|Now|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s*\d{4})|"
    r"\d{4}\s*(?:-|–|—|to)\s*(?:Present|Current|Now|\d{4})|"
    r"\d{4})",
    re.IGNORECASE,
)


@dataclass
class ResumeDocument:
    text: str
    content_type: str
    source_url: str


def normalize_google_url(source_url: str) -> str:
    """Prefer Google Docs plain-text export when given a document URL."""
    parsed = urlparse(source_url)
    if parsed.netloc != "docs.google.com":
        return source_url
    match = re.search(r"/document/d/([^/]+)", parsed.path)
    if not match:
        return source_url
    query = parse_qs(parsed.query)
    if query.get("format") == ["txt"]:
        return source_url
    doc_id = match.group(1)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            f"/document/d/{doc_id}/export",
            "",
            urlencode({"format": "txt"}),
            "",
        )
    )


def normalize_drive_url(source_url: str) -> str:
    """Convert common Drive file links to direct downloads."""
    parsed = urlparse(source_url)
    if parsed.netloc not in {"drive.google.com", "www.drive.google.com"}:
        return source_url
    match = re.search(r"/file/d/([^/]+)", parsed.path)
    if not match:
        return source_url
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            "/uc",
            "",
            urlencode({"export": "download", "id": match.group(1)}),
            "",
        )
    )


def normalize_source_url(source_url: str) -> str:
    return normalize_drive_url(normalize_google_url(source_url))


def fetch_resume(source_url: str, timeout: float = 30.0) -> ResumeDocument:
    url = normalize_source_url(source_url)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "fasthtml-portfolio-resume-sync/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        content_type = response.headers.get("content-type", "")
    text = extract_text(raw, content_type, url)
    return ResumeDocument(text=text, content_type=content_type, source_url=url)


def extract_text(raw: bytes, content_type: str = "", source_url: str = "") -> str:
    lowered_type = content_type.lower()
    lowered_url = source_url.lower()
    if "pdf" in lowered_type or lowered_url.endswith(".pdf"):
        return extract_pdf_text(raw)
    if (
        "officedocument.wordprocessingml.document" in lowered_type
        or lowered_url.endswith(".docx")
        or raw.startswith(b"PK")
    ):
        return extract_docx_text(raw)
    return raw.decode("utf-8", errors="replace")


def extract_pdf_text(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependency is in dev deps.
        raise RuntimeError("Install pypdf to parse PDF resumes.") from exc

    reader = PdfReader(BytesIO(raw))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_docx_text(raw: bytes) -> str:
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        parts = [
            node.text or ""
            for node in paragraph.findall(".//w:t", namespace)
            if node.text
        ]
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def clean_line(line: str) -> str:
    line = line.replace("\u00a0", " ")
    line = re.sub(r"\s+", " ", line).strip()
    return line


def normalize_section_name(line: str) -> str | None:
    candidate = clean_line(line).strip(":").lower()
    if len(candidate) > 40:
        return None
    for canonical, aliases in SECTION_ALIASES.items():
        if candidate in aliases:
            return canonical
    return None


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"intro": []}
    current = "intro"
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        section = normalize_section_name(line)
        if section:
            current = section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def strip_bullet(line: str) -> str:
    return BULLET_PREFIX_RE.sub("", line).strip()


def is_bullet(line: str) -> bool:
    return bool(BULLET_PREFIX_RE.match(line))


def parse_summary(sections: dict[str, list[str]]) -> str:
    candidates = sections.get("summary") or sections.get("intro") or []
    clean = [strip_bullet(line) for line in candidates if not looks_like_contact(line)]
    paragraphs = [line for line in clean if len(line.split()) >= 5]
    return " ".join(paragraphs[:2]).strip()


def parse_highlights(sections: dict[str, list[str]]) -> list[str]:
    explicit = [strip_bullet(line) for line in sections.get("highlights", [])]
    if explicit:
        return explicit[:6]
    experience_bullets = [
        strip_bullet(line)
        for line in sections.get("experience", [])
        if is_bullet(line) and len(strip_bullet(line)) > 20
    ]
    return experience_bullets[:3]


def looks_like_contact(line: str) -> bool:
    lowered = line.lower()
    return "@" in lowered or "linkedin.com" in lowered or "github.com" in lowered


def parse_experience_line(line: str) -> tuple[str, str, str]:
    cleaned = strip_bullet(line)
    period = ""
    date_match = DATE_RE.search(cleaned)
    if date_match:
        period = date_match.group("period").strip()
        cleaned = (cleaned[: date_match.start()] + cleaned[date_match.end() :]).strip()
        cleaned = cleaned.strip(" -–—|,()")

    for sep in (" | ", " – ", " — ", " - "):
        parts = [part.strip(" ,") for part in cleaned.split(sep) if part.strip(" ,")]
        if len(parts) >= 2:
            title, company = parts[0], parts[1]
            return title, company, period

    at_match = re.match(r"(?P<title>.+?)\s+at\s+(?P<company>.+)", cleaned, re.I)
    if at_match:
        return (
            at_match.group("title").strip(),
            at_match.group("company").strip(),
            period,
        )

    comma_parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    if len(comma_parts) >= 2:
        return comma_parts[0], comma_parts[1], period
    return cleaned, "", period


def parse_experience(sections: dict[str, list[str]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line in sections.get("experience", []):
        body = strip_bullet(line)
        if not body:
            continue
        if is_bullet(line):
            if current is None:
                current = {
                    "title": "Experience",
                    "company": "",
                    "period": "",
                    "bullets": [],
                }
                entries.append(current)
            current.setdefault("bullets", []).append(body)
            continue

        title, company, period = parse_experience_line(line)
        current = {
            "title": title,
            "company": company,
            "period": period,
            "bullets": [],
        }
        entries.append(current)

    return [
        entry
        for entry in entries
        if entry.get("title") or entry.get("company") or entry.get("bullets")
    ]


def parse_education(sections: dict[str, list[str]]) -> list[dict[str, str]]:
    education: list[dict[str, str]] = []
    for line in sections.get("education", []):
        body = strip_bullet(line)
        if not body or looks_like_contact(body):
            continue
        period = ""
        date_match = DATE_RE.search(body)
        if date_match:
            period = date_match.group("period").strip()
            body = (body[: date_match.start()] + body[date_match.end() :]).strip(" ,-|")
        institution = ""
        degree = body
        for sep in (" | ", " – ", " — ", " - "):
            parts = [part.strip() for part in body.split(sep) if part.strip()]
            if len(parts) >= 2:
                degree, institution = parts[0], parts[1]
                break
        education.append(
            {"degree": degree, "institution": institution, "period": period}
        )
    return education


def parse_skills(sections: dict[str, list[str]]) -> dict[str, list[str]]:
    skills: dict[str, list[str]] = {}
    uncategorized: list[str] = []
    for line in sections.get("skills", []):
        body = strip_bullet(line)
        if not body:
            continue
        if ":" in body:
            category, values = body.split(":", 1)
            items = split_skill_values(values)
            if items:
                skills[category.strip()] = items
        else:
            uncategorized.extend(split_skill_values(body))
    if uncategorized:
        skills.setdefault("Skills", [])
        skills["Skills"].extend(
            item for item in uncategorized if item not in skills["Skills"]
        )
    return skills


def split_skill_values(value: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"[,;|]", value)
        if item.strip() and len(item.strip()) <= 40
    ]


def merge_nonempty(existing: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key in ("summary", "highlights", "experience", "education", "skills"):
        value = parsed.get(key)
        if value:
            merged[key] = value
    if existing.get("snapshot"):
        merged["snapshot"] = existing["snapshot"]
    return merged


def without_synced_at(data: dict[str, Any]) -> dict[str, Any]:
    comparable = json.loads(json.dumps(data, sort_keys=True))
    if isinstance(comparable.get("resume_source"), dict):
        comparable["resume_source"].pop("synced_at", None)
    return comparable


def parse_resume_text(
    text: str,
    *,
    existing: dict[str, Any] | None = None,
    source_url: str = "",
    content_type: str = "",
) -> dict[str, Any]:
    existing = existing or {}
    sections = split_sections(text)
    parsed = {
        "summary": parse_summary(sections),
        "highlights": parse_highlights(sections),
        "experience": parse_experience(sections),
        "education": parse_education(sections),
        "skills": parse_skills(sections),
    }
    data = merge_nonempty(existing, parsed)
    data["resume_source"] = {
        "source_url": source_url,
        "content_type": content_type,
        "synced_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "parser": "scripts/sync_resume_content.py",
    }
    data["resume_text"] = "\n".join(
        clean_line(line) for line in text.splitlines() if clean_line(line)
    )
    existing_synced_at = (existing.get("resume_source") or {}).get("synced_at")
    if existing_synced_at and without_synced_at(existing) == without_synced_at(data):
        data["resume_source"]["synced_at"] = existing_synced_at
    return data


def load_existing(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-url",
        default=os.getenv("RESUME_SOURCE_URL") or os.getenv("RESUME_URL"),
        help="Resume source URL. Defaults to RESUME_SOURCE_URL or RESUME_URL.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Local resume file fixture to parse instead of fetching a URL.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/experience.json"),
        help="Structured JSON output path.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print JSON without writing."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    existing = load_existing(args.output)

    if args.input:
        raw = args.input.read_bytes()
        text = extract_text(raw, source_url=str(args.input))
        document = ResumeDocument(
            text=text,
            content_type="local-file",
            source_url=str(args.input),
        )
    elif args.source_url:
        document = fetch_resume(args.source_url)
    else:
        print("Set RESUME_SOURCE_URL or pass --source-url/--input.", file=sys.stderr)
        return 2

    data = parse_resume_text(
        document.text,
        existing=existing,
        source_url=document.source_url,
        content_type=document.content_type,
    )
    if args.dry_run:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        write_json(args.output, data)
        print(f"Updated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

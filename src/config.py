from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from src.themes import normalize_appearance, normalize_theme

ROOT_DIR = Path(__file__).resolve().parent.parent

# On Vercel (serverless), writes must go to /tmp. Use that for ephemeral data.
BASE_DATA_DIR = Path("/tmp") if os.getenv("VERCEL") else (ROOT_DIR / "data")


@dataclass(frozen=True)
class SiteConfig:
    owner_name: str
    brand_initials: str
    brand_subtitle: str
    site_title: str
    site_description: str
    hero_kicker: str
    hero_primary_cta: str
    hero_chat_cta: str
    footer_tagline: str
    public_email: Optional[str]
    linkedin_url: Optional[str]
    github_username: Optional[str]
    resume_url: Optional[str]
    default_theme: str
    default_appearance: str
    contact_intro: str
    contact_response_time: str
    resume_pdf_prompt: str
    resume_pdf_description: str
    content: dict[str, Any]

    def text(self, section: str, key: str, default: str) -> str:
        section_data = self.content.get(section)
        if not isinstance(section_data, dict):
            return default
        value = section_data.get(key)
        return str(value) if value not in (None, "") else default

    def text_list(self, section: str, key: str, default: list[str]) -> list[str]:
        section_data = self.content.get(section)
        if not isinstance(section_data, dict):
            return default
        value = section_data.get(key)
        if not isinstance(value, list):
            return default
        items = [str(item).strip() for item in value if str(item).strip()]
        return items or default


def _read_site_json() -> dict[str, Any]:
    """Read optional public site configuration from data/site.json.

    This file is meant for non‑secret knobs (copy, public email alias, etc.).
    It is safe to commit. Secrets should remain in environment variables.
    """
    for fname in ("site.json", "site.config.json", "site_content.json"):
        p = ROOT_DIR / "data" / fname
        if p.exists():
            try:
                return json.loads(p.read_text()) or {}
            except Exception:
                return {}
    return {}


def get_config() -> SiteConfig:
    data = _read_site_json()
    content = data.get("content") if isinstance(data.get("content"), dict) else {}
    # Public email logic: explicit public value > contact alias > SMTP destination.
    public_email = (
        os.getenv("PUBLIC_EMAIL")
        or str(data.get("public_email") or "").strip()
        or os.getenv("CONTACT_EMAIL")
        or os.getenv("SMTP_TO")
    )
    return SiteConfig(
        owner_name=os.getenv(
            "OWNER_NAME", str(data.get("owner_name") or "Matthew L. Pergolski")
        ),
        brand_initials=os.getenv(
            "BRAND_INITIALS", str(data.get("brand_initials") or "MLP")
        ),
        brand_subtitle=os.getenv(
            "BRAND_SUBTITLE", str(data.get("brand_subtitle") or "Portfolio")
        ),
        site_title=os.getenv(
            "SITE_TITLE", str(data.get("site_title") or "Professional Portfolio")
        ),
        site_description=os.getenv(
            "SITE_DESCRIPTION",
            str(data.get("site_description") or "AI/ML Engineer & Data Scientist"),
        ),
        hero_kicker=str(data.get("hero_kicker") or "AI/ML Engineering Portfolio"),
        hero_primary_cta=str(data.get("hero_primary_cta") or "View Projects"),
        hero_chat_cta=str(data.get("hero_chat_cta") or "Experience Chat"),
        footer_tagline=str(
            data.get("footer_tagline")
            or "Data Science • Machine Learning • AI Engineering"
        ),
        public_email=public_email,
        linkedin_url=os.getenv("LINKEDIN_URL") or (data.get("linkedin_url") or None),
        github_username=os.getenv("GITHUB_USERNAME")
        or (data.get("github_username") or None),
        resume_url=os.getenv("RESUME_URL") or (data.get("resume_url") or None),
        default_theme=normalize_theme(
            os.getenv("SITE_THEME") or str(data.get("theme") or "")
        ),
        default_appearance=normalize_appearance(
            os.getenv("SITE_APPEARANCE") or str(data.get("appearance") or "")
        ),
        contact_intro=str(
            data.get("contact_intro")
            or (
                "I'm always interested in discussing new opportunities, "
                "interesting projects, or just having a chat about data science and AI."
            )
        ),
        contact_response_time=str(
            data.get("contact_response_time")
            or "I typically respond to emails within 24 hours."
        ),
        resume_pdf_prompt=str(data.get("resume_pdf_prompt") or "Want the PDF version?"),
        resume_pdf_description=str(
            data.get("resume_pdf_description")
            or (
                "Download the formatted resume, or browse the expanded "
                "experience details below."
            )
        ),
        content=content,
    )

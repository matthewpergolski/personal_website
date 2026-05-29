from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


ROOT_DIR = Path(__file__).resolve().parent.parent

# On Vercel (serverless), writes must go to /tmp. Use that for ephemeral data.
BASE_DATA_DIR = Path("/tmp") if os.getenv("VERCEL") else (ROOT_DIR / "data")


@dataclass(frozen=True)
class SiteConfig:
    site_title: str
    site_description: str
    public_email: Optional[str]
    linkedin_url: Optional[str]
    github_username: Optional[str]
    resume_url: Optional[str]


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
    # Public email logic: explicit env > json > CONTACT_EMAIL > SMTP_TO
    public_email = (
        os.getenv("SMTP_TO")
        or str(data.get("public_email") or "").strip()
        or os.getenv("CONTACT_EMAIL")
        or os.getenv("PUBLIC_EMAIL")
    )
    return SiteConfig(
        site_title=os.getenv(
            "SITE_TITLE", str(data.get("site_title") or "Professional Portfolio")
        ),
        site_description=os.getenv(
            "SITE_DESCRIPTION",
            str(data.get("site_description") or "AI/ML Engineer & Data Scientist"),
        ),
        public_email=public_email,
        linkedin_url=os.getenv("LINKEDIN_URL") or (data.get("linkedin_url") or None),
        github_username=os.getenv("GITHUB_USERNAME")
        or (data.get("github_username") or None),
        resume_url=os.getenv("RESUME_URL") or (data.get("resume_url") or None),
    )

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


ROOT_DIR = Path(__file__).resolve().parent.parent


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


@dataclass(frozen=True)
class RAGConfig:
    """Configuration for RAG system components."""
    model_name: str = field(default="microsoft/phi-2")
    embedding_model: str = field(default="sentence-transformers/all-MiniLM-L6-v2")
    vector_db_path: str = field(default="data/rag/vectors.db")
    chunk_size: int = field(default=512)
    chunk_overlap: int = field(default=128)
    cache_dir: str = field(default=str(Path("/tmp") / "rag_cache"))
    memory_limit_mb: int = field(default=1024)
    max_response_tokens: int = field(default=150)
    temperature: float = field(default=0.7)
    # Vercel deployment strategy
    vector_store_source: str = field(default="build")  # "build", "runtime", "persistent"


def get_rag_config() -> RAGConfig:
    """Get RAG configuration with environment variable overrides."""
    return RAGConfig(
        model_name=os.getenv("RAG_MODEL_NAME", "microsoft/phi-2"),
        embedding_model=os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        vector_db_path=os.getenv("RAG_VECTOR_DB_PATH", str(ROOT_DIR / "data" / "rag" / "vectors.db")),
        cache_dir=os.getenv("RAG_CACHE_DIR", str(Path("/tmp") / "rag_cache")),
        memory_limit_mb=int(os.getenv("RAG_MEMORY_LIMIT_MB", "1024")),
        max_response_tokens=int(os.getenv("RAG_MAX_RESPONSE_TOKENS", "150")),
        temperature=float(os.getenv("RAG_TEMPERATURE", "0.7")),
        vector_store_source=os.getenv("RAG_VECTOR_STORE_SOURCE", "build"),
    )


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
        site_title=os.getenv("SITE_TITLE", str(data.get("site_title") or "Professional Portfolio")),
        site_description=os.getenv("SITE_DESCRIPTION", str(data.get("site_description") or "AI/ML Engineer & Data Scientist")),
        public_email=public_email,
        linkedin_url=os.getenv("LINKEDIN_URL") or (data.get("linkedin_url") or None),
        github_username=os.getenv("GITHUB_USERNAME") or (data.get("github_username") or None),
        resume_url=os.getenv("RESUME_URL") or (data.get("resume_url") or None),
    )

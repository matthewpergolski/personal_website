from __future__ import annotations

import os
from pathlib import Path

from fasthtml import FastHTML
from fasthtml.common import Link, Script, Style
from starlette.staticfiles import StaticFiles

from src.assets.scripts import DARK_MODE_SCRIPT, GLOBAL_INTERACTIONS_SCRIPT
from src.assets.styles import GLOBAL_STYLES
from src.config import ROOT_DIR, get_config


def create_app(session_key_fname: str, session_secret: str | None) -> FastHTML:
    return FastHTML(
        # On Vercel's serverless runtime, the filesystem is read-only except for /tmp.
        # Ensure FastHTML does not try to write the default .sesskey in CWD.
        key_fname=session_key_fname,
        secret_key=session_secret,
        sess_https_only=bool(os.getenv("VERCEL")),
        title=get_config().site_title,
        hdrs=(
            Link(
                rel="stylesheet",
                href=(
                    "https://fonts.googleapis.com/css2?"
                    "family=Inter:wght@300;400;500;600;700&display=swap"
                ),
            ),
            Link(rel="icon", type="image/svg+xml", href="/static/favicon.svg"),
            Style(GLOBAL_STYLES),
            Script(src="https://cdn.plot.ly/plotly-2.35.2.min.js"),
            Script(DARK_MODE_SCRIPT),
            Script(GLOBAL_INTERACTIONS_SCRIPT),
        ),
    )


def mount_static(app: FastHTML) -> None:
    static_dir = Path(os.getenv("STATIC_DIR", ROOT_DIR / "data" / "static"))
    try:
        static_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    except Exception:
        # Safe no-op if mounting fails in some environments.
        pass

"""
Vercel Serverless adapter for the FastHTML app.

Exposes the ASGI `app` from `src.main` so Vercel's Python runtime
can serve it as a serverless function at "/".
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path when executing from api/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the ASGI application
from src.main import app  # noqa: E402,F401

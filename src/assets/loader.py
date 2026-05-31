from __future__ import annotations

from functools import lru_cache
from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_asset_text(filename: str) -> str:
    return (ASSET_DIR / filename).read_text(encoding="utf-8")

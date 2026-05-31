from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import fasthtml.common as ft


ASSET_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_asset_text(filename: str) -> str:
    return (ASSET_DIR / filename).read_text(encoding="utf-8")


def asset_script(filename: str):
    return ft.Script(load_asset_text(filename))


def asset_style(filename: str):
    return ft.Style(load_asset_text(filename))

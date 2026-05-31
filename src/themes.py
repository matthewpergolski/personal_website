from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeOption:
    slug: str
    label: str
    description: str


@dataclass(frozen=True)
class AppearanceOption:
    slug: str
    label: str
    description: str


THEME_OPTIONS: tuple[ThemeOption, ...] = (
    ThemeOption(
        "cosmic",
        "Cosmic",
        "Current portfolio look with deep surfaces and blue accents.",
    ),
    ThemeOption(
        "graphite",
        "Graphite",
        "Neutral, product-like interface with restrained contrast.",
    ),
    ThemeOption(
        "evergreen",
        "Evergreen",
        "Calm technical palette with green accents.",
    ),
    ThemeOption(
        "atelier",
        "Atelier",
        "Editorial warm-neutral theme for content-heavy pages.",
    ),
    ThemeOption(
        "sunrise",
        "Sunrise",
        "Bright professional palette with amber and coral accents.",
    ),
    ThemeOption(
        "spectrum",
        "Spectrum",
        "Modern blue-violet palette for portfolio or product demos.",
    ),
)

APPEARANCE_OPTIONS: tuple[AppearanceOption, ...] = (
    AppearanceOption("system", "System", "Match this device setting."),
    AppearanceOption("light", "Light", "Use the light version."),
    AppearanceOption("dark", "Dark", "Use the dark version."),
)

DEFAULT_THEME = "cosmic"
DEFAULT_APPEARANCE = "dark"


def theme_slugs() -> set[str]:
    return {theme.slug for theme in THEME_OPTIONS}


def appearance_slugs() -> set[str]:
    return {appearance.slug for appearance in APPEARANCE_OPTIONS}


def normalize_theme(value: str | None) -> str:
    if value in theme_slugs():
        return str(value)
    return DEFAULT_THEME


def normalize_appearance(value: str | None) -> str:
    if value in appearance_slugs():
        return str(value)
    return DEFAULT_APPEARANCE

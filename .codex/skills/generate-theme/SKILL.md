---
name: generate-theme
description: Create or extend this FastHTML portfolio's theme system from a URL, screenshot, brand colors, or style brief. Use when Codex is asked to add a new visual theme, derive a theme from reference material, emulate high-level design traits without copying another site, update `src/themes.py`, or add light/dark CSS token sets for the portfolio template.
---

# Generate Theme

## Workflow

1. Gather the reference input: URL, screenshot, brand colors, industry, audience, or written style brief.
2. Inspect the current implementation before editing:
   - `src/themes.py`
   - `src/assets/global.css`
   - `src/config.py`
   - `data/site.json.example`
   - `scripts/verify_ui_browser.py`
3. Read `references/theme-contract.md` for the required token contract and verification checklist.
4. Add or revise one theme at a time:
   - Add one `ThemeOption` in `src/themes.py`.
   - Add matching light and dark token blocks in `src/assets/global.css`.
   - Keep `data/site.json.example`, README, and browser smoke checks aligned.
5. Validate the theme across desktop and mobile:
   - `bun run check`
   - `uv run python scripts/verify_ui_smoke.py`
   - `uv run python scripts/verify_ui_browser.py`
   - `uv run pre-commit run --all-files`

## Design Rules

- Extract high-level traits from references; do not clone layouts, trademarks, proprietary artwork, or distinctive brand expression.
- Preserve the existing FastHTML component structure. A theme should change tokens, not page layout.
- Every theme must support `light`, `dark`, and `system` appearance behavior.
- Favor professional, reusable palettes for real portfolio/business sites.
- Avoid one-note palettes where nearly every surface, border, chip, and accent is the same hue.
- Keep contrast readable on cards, buttons, chips, chart labels, chat UI, and the mobile tab bar.
- Do not introduce new dependencies for a theme-only change.

## Output Shape

When proposing or implementing a new theme, include:

- Theme slug and display label.
- Intended use case or mood.
- Light/dark palette notes.
- Files changed.
- Verification commands and results.

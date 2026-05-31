# Theme Contract

This project separates theme family from appearance mode:

- `data-theme`: visual family, such as `cosmic` or `graphite`.
- `data-appearance`: resolved appearance, either `light` or `dark`.
- `data-appearance-choice`: visitor preference, one of `system`, `light`, or `dark`.

## Required Files

- `src/themes.py`: register the theme slug, label, and short description.
- `src/assets/global.css`: define light and dark token blocks for the slug.
- `data/site.json.example`: keep example defaults valid if defaults change.
- `README.md`: document new public config values or theme options.
- `scripts/verify_ui_browser.py`: include new theme slugs in the theme matrix.

## Required CSS Blocks

Each theme must define both selectors:

```css
html[data-theme="theme-slug"][data-appearance="light"] {
}

html[data-theme="theme-slug"][data-appearance="dark"] {
}
```

Each block must define:

- `--primary-color`
- `--primary-strong`
- `--secondary-color`
- `--accent-color`
- `--dark-color`
- `--light-color`
- `--text-color`
- `--muted-text`
- `--border-color`
- `--surface-1`
- `--surface-2`
- `--surface-3`
- `--chip-bg`
- `--chip-border`
- `--chip-fg`
- `--starfield-opacity`
- `--mobile-chrome-bg` when the default value is not suitable

Do not redefine spacing, layout, or component structure in a theme block unless the user explicitly requested a theme-specific component treatment.

## Quality Bar

- Body text and muted text must remain readable on all surfaces.
- Buttons must have clear hover and active states through existing token usage.
- The mobile tab bar must remain legible in both light and dark appearances.
- Chart controls, chart legends, chat bubbles, forms, and chips must not collapse into low-contrast combinations.
- The current `cosmic` theme is the default and should remain visually close to the existing production look unless explicitly changed.

## Verification

Run:

```bash
bun run check
uv run python scripts/verify_ui_smoke.py
uv run python scripts/verify_ui_browser.py
uv run pre-commit run --all-files
```

The browser smoke test must pass across desktop and mobile for every slug in `THEMES`.

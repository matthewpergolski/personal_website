# UX Verification

Use this checklist for visual or interaction-heavy PRs. Keep it lightweight: the goal is to catch layout regressions before Vercel preview review.

## Local Checks

1. Run the app locally:

   ```bash
   uv run uvicorn src.main:app --host 127.0.0.1 --port 8000
   ```

2. Capture desktop and mobile screenshots for:

   - `/`
   - `/about`
   - `/resume`
   - `/projects`
   - `/contact`
   - `/chat`

3. Use at least these viewports:

   - Desktop: `1280 x 900`
   - Mobile: `390 x 844`

4. Check the screenshots for:

   - No overlapping text, buttons, nav, chat widget, or mobile tab bar.
   - Primary calls to action fit on one line or wrap cleanly.
   - Cards do not contain nested card-like visual frames.
   - Section headings match their content density.
   - Mobile nav opens and closes without covering the bottom tab bar.
   - Resume and About content still reflects `data/experience.json`.
   - Chat page and floating chat remain reachable, share browser-session history, and show source/provider context.
   - Tech Stack controls explain the selected view/metric and small mobile slices have a readable key.

## Required Commands

```bash
uv run pytest -q
uv run python scripts/verify_ui_smoke.py
uv run playwright install chromium
uv run python scripts/verify_ui_browser.py
uv run pre-commit run --all-files
```

`verify_ui_browser.py` launches the FastHTML app with patched external services and checks desktop/mobile routes with Chromium. It is not a pixel-perfect screenshot test; it catches broken routes, console errors, horizontal overflow, missing critical UI, and mobile chat/tab-bar overlap.

## Vercel Preview

Before merge, verify GitHub checks, the Vercel preview deployment, and any protected-preview limitations. If Vercel preview requires login, local browser verification plus green Vercel deployment status is acceptable, but say so in the PR notes.

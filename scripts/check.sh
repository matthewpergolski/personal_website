#!/usr/bin/env bash
# Run the repository test and lint suite, stopping on the first failure.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

uv run pytest -q
uv run python scripts/verify_ui_smoke.py
uv run python scripts/verify_ui_browser.py
bun run check
uv run pre-commit run --all-files

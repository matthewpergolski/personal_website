"""The test/lint suite has one entrypoint, and CI installs a pinned Bun."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECK_COMMANDS = (
    "uv run pytest -q",
    "uv run python scripts/verify_ui_smoke.py",
    "uv run python scripts/verify_ui_browser.py",
    "bun run check",
    "uv run pre-commit run --all-files",
)


def test_check_script_runs_the_suite_in_order():
    script = ROOT / "scripts" / "check.sh"
    text = script.read_text()
    positions = [text.index(command) for command in CHECK_COMMANDS]
    assert positions == sorted(positions)
    assert "set -euo pipefail" in text
    assert script.stat().st_mode & 0o111


def test_ci_and_agents_invoke_the_check_script():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    agents = (ROOT / "AGENTS.md").read_text()
    workflows = (ROOT / ".github" / "workflows").glob("*.yml")

    assert "scripts/check.sh" in ci
    assert "scripts/check.sh" in agents
    assert "bun-version-file: .bun-version" in ci
    assert "bun-version: latest" not in ci
    for command in CHECK_COMMANDS:
        assert command not in agents

    for path in workflows:
        text = path.read_text()
        for command in CHECK_COMMANDS:
            assert command not in text, path.name


def test_bun_version_file_is_a_concrete_pin():
    pinned = (ROOT / ".bun-version").read_text().strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", pinned)
    assert pinned != "latest"

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from starlette.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import main as main_mod  # noqa: E402
from src.assets.styles import GLOBAL_STYLES  # noqa: E402


@dataclass(frozen=True)
class SmokeCheck:
    name: str
    run: Callable[[], None]


def _profile() -> dict:
    return {
        "name": "Matthew L. Pergolski",
        "bio": "AI/ML engineer and data scientist",
        "avatar_url": "https://example.com/avatar.png",
        "html_url": "https://github.com/matthewpergolski",
        "public_repos": 17,
        "followers": 1,
    }


def _projects() -> list[dict]:
    return [
        {
            "name": "portfolio_app",
            "language": "Python",
            "description": "Portfolio application",
            "topics": ["fasthtml"],
            "url": "https://github.com/matthewpergolski/portfolio_app",
            "stars": 3,
            "updated": "2026-05-01",
        }
    ]


def _patch_external_services() -> None:
    async def fake_profile() -> dict:
        return _profile()

    async def fake_projects() -> list[dict]:
        return _projects()

    async def fake_language_bytes() -> dict[str, int]:
        return {"Python": 1200, "HTML": 600, "R": 400}

    main_mod.fetch_github_profile = fake_profile
    main_mod.fetch_github_projects = fake_projects
    main_mod.fetch_language_bytes_aggregate = fake_language_bytes
    main_mod.generate_captcha = lambda: ("data:image/png;base64,AA==", "ABCDE")


def _response_text(client: TestClient, path: str) -> str:
    response = client.get(path)
    if response.status_code != 200:
        raise AssertionError(f"{path} returned {response.status_code}")
    return response.text


def _assert_contains(text: str, path: str, expected: list[str]) -> None:
    missing = [item for item in expected if item not in text]
    if missing:
        raise AssertionError(f"{path} missing expected content: {missing}")


def _check_public_routes(client: TestClient) -> None:
    expectations = {
        "/": ["Matthew L. Pergolski", "Tech Stack Snapshot", "mobile-tabbar"],
        "/about": ["About Me", "Professional Background", "Highlights"],
        "/projects": ["Featured Projects", "portfolio_app"],
        "/resume": ["Professional Resume", "Download Resume"],
        "/contact": ["Get In Touch", "Send a Message", "captcha"],
        "/chat": ["Experience Chat", "chat-page-section", "chat-page-container"],
    }
    for path, expected in expectations.items():
        _assert_contains(_response_text(client, path), path, expected)


def _check_mobile_navigation(client: TestClient) -> None:
    html = _response_text(client, "/")
    expected = [
        'id="mobile-tabbar"',
        'id="tab-home"',
        'id="tab-about"',
        'id="tab-projects"',
        'id="tab-resume"',
        'id="tab-contact"',
        'id="tab-chat"',
        'aria-controls="nav-links"',
        'id="nav-toggle"',
    ]
    _assert_contains(html, "/", expected)
    if html.index(">About<") > html.index(">Projects<"):
        raise AssertionError("Navigation order should put About before Projects")


def _check_chat_ui_contract(client: TestClient) -> None:
    html = _response_text(client, "/chat")
    expected = [
        "Ask about Matthew&#x27;s experience, projects, and role fit.",
        "Free-tier chat. Limited answers.",
        "Advanced models available.",
        "What AI/ML work have you done?",
        "How have you used Python in your AI/ML work?",
        "Summarize your Lockheed Martin experience.",
        "What kind of roles are you targeting?",
        "Start a new chat",
        "Copy conversation",
        "chat-page-title",
        "chat-page-container",
        "chat-page-section",
    ]
    _assert_contains(html, "/chat", expected)


def _check_mobile_css_contracts() -> None:
    css = GLOBAL_STYLES
    expected = [
        "@media (max-width: 768px)",
        ".mobile-tabbar { display:flex; }",
        "body { padding-bottom: 74px; }",
        ".experience-chat:not(.experience-chat-page) { display: none; }",
        "body.nav-open .mobile-tabbar",
        "body.nav-open .experience-chat { display: none; }",
    ]
    _assert_contains(css, "GLOBAL_STYLES", expected)

    chat_html = _response_text(TestClient(main_mod.app), "/chat")
    chat_expected = [
        ".experience-chat-page .chat-form",
        "position: fixed",
        "bottom: calc(74px + env(safe-area-inset-bottom))",
        ".chat-page-section ~ .footer",
        "margin-bottom: 104px",
        "chat-page-container { padding-bottom: 1rem; }",
    ]
    _assert_contains(chat_html, "/chat inline chat styles", chat_expected)


def _check_chat_api(client: TestClient) -> None:
    response = client.post(
        "/api/rag/chat",
        json={"message": "How have you used Python in your AI/ML work?"},
    )
    if response.status_code != 200:
        raise AssertionError(f"chat API returned {response.status_code}")
    payload = response.json()
    if payload.get("provider") != "local":
        raise AssertionError(f"expected local provider, got {payload.get('provider')}")
    if not payload.get("sources"):
        raise AssertionError("expected chat API sources")
    if "Python" not in payload.get("response", ""):
        raise AssertionError("expected Python context in chat API response")


def run_smoke_checks() -> None:
    _patch_external_services()
    client = TestClient(main_mod.app)
    checks = [
        SmokeCheck("public routes", lambda: _check_public_routes(client)),
        SmokeCheck("mobile navigation", lambda: _check_mobile_navigation(client)),
        SmokeCheck("chat UI contract", lambda: _check_chat_ui_contract(client)),
        SmokeCheck("mobile CSS contracts", _check_mobile_css_contracts),
        SmokeCheck("chat API", lambda: _check_chat_api(client)),
    ]

    failures: list[str] = []
    for check in checks:
        try:
            check.run()
            print(f"PASS {check.name}")
        except Exception as exc:
            failures.append(f"FAIL {check.name}: {exc}")

    if failures:
        for failure in failures:
            print(failure)
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run deterministic UI smoke checks for route, mobile, and chat regressions."
    )
    parser.parse_args()
    asyncio.run(asyncio.to_thread(run_smoke_checks))


if __name__ == "__main__":
    main()

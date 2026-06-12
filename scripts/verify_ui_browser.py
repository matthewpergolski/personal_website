from __future__ import annotations

import argparse
import socket
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import uvicorn
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import main as main_mod  # noqa: E402
from scripts.verify_ui_smoke import _patch_external_services  # noqa: E402


@dataclass(frozen=True)
class Viewport:
    name: str
    width: int
    height: int
    is_mobile: bool = False


ROUTES = {
    "/": [".hero-title", "#mobile-tabbar", "text=Tech Stack Snapshot"],
    "/about": ["text=About Me", "text=Professional Background"],
    "/projects": ["text=Featured Projects"],
    "/resume": ["text=Professional Resume", "text=Download Resume"],
    "/contact": ["text=Get In Touch", "text=Send a Message"],
    "/chat": [".chat-page-title", "#chat-form", "#chat-suggestions"],
}

THEMES = ("cosmic", "graphite", "evergreen", "atelier", "sunrise", "spectrum")
APPEARANCES = ("light", "dark")


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _start_server(port: int) -> uvicorn.Server:
    config = uvicorn.Config(
        main_mod.app,
        host="127.0.0.1",
        port=port,
        lifespan="off",
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return server


def _wait_for_server(base_url: str) -> None:
    deadline = time.monotonic() + 10
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = httpx.get(f"{base_url}/chat", timeout=1)
            if response.status_code == 200:
                return
        except Exception as exc:  # noqa: BLE001 - surfaced if readiness times out.
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"server did not become ready: {last_error}")


def _assert_no_horizontal_overflow(page: Page, label: str) -> None:
    has_no_overflow = page.evaluate(
        "() => document.documentElement.scrollWidth <= window.innerWidth + 1"
    )
    if not has_no_overflow:
        metrics = page.evaluate(
            "() => ({scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth})"
        )
        raise AssertionError(f"{label} has horizontal overflow: {metrics}")


def _assert_visible(page: Page, selector: str, label: str) -> None:
    page.locator(selector).first.wait_for(state="visible", timeout=5000)
    count = page.locator(selector).count()
    if count < 1:
        raise AssertionError(f"{label} missing selector {selector}")


def _check_route(page: Page, base_url: str, route: str, viewport: Viewport) -> None:
    label = f"{viewport.name} {route}"
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))
    page.on(
        "console",
        lambda msg: (
            errors.append(f"console error: {msg.text}") if msg.type == "error" else None
        ),
    )

    response = page.goto(f"{base_url}{route}", wait_until="domcontentloaded")
    if response is None or response.status >= 400:
        status = response.status if response else "no response"
        raise AssertionError(f"{label} returned {status}")

    for selector in ROUTES[route]:
        if selector == "#mobile-tabbar" and not viewport.is_mobile:
            continue
        _assert_visible(page, selector, label)

    _assert_no_horizontal_overflow(page, label)
    if errors:
        raise AssertionError(f"{label} browser errors: {errors}")


def _check_chat_mobile_interaction(
    page: Page, base_url: str, viewport: Viewport
) -> None:
    page.goto(f"{base_url}/chat", wait_until="domcontentloaded")
    page.locator("#chat-reset").click()
    _assert_visible(page, "#chat-suggestions", f"{viewport.name} chat")

    page.locator(".chat-suggestion").first.click()
    page.wait_for_function(
        "() => [...document.querySelectorAll('.chat-message.assistant')].length >= 2",
        timeout=7000,
    )
    _assert_visible(page, "#chat-suggestions", f"{viewport.name} chat follow-up")
    _assert_no_horizontal_overflow(page, f"{viewport.name} chat follow-up")

    layout = page.evaluate(
        """() => {
            const form = document.querySelector('#chat-form').getBoundingClientRect();
            const tab = document.querySelector('#mobile-tabbar').getBoundingClientRect();
            const title = document.querySelector('.chat-page-title').getBoundingClientRect();
            return {
                formBottom: form.bottom,
                tabTop: tab.top,
                titleTop: title.top,
                titleHeight: title.height,
                innerHeight: window.innerHeight
            };
        }"""
    )
    if layout["formBottom"] > layout["tabTop"] + 1:
        raise AssertionError(f"mobile chat form overlaps tab bar: {layout}")
    if layout["titleTop"] < 20 or layout["titleHeight"] < 30:
        raise AssertionError(f"mobile chat title is cramped: {layout}")


def _check_theme_controls(page: Page, base_url: str, viewport: Viewport) -> None:
    page.goto(f"{base_url}/", wait_until="domcontentloaded")
    if viewport.is_mobile:
        _assert_visible(page, "#theme-toggle-mobile", f"{viewport.name} theme toggle")
        page.locator("#nav-toggle").click()
        _assert_visible(
            page,
            '.nav-theme-panel [data-theme-select="mobile-menu"]',
            f"{viewport.name} theme select",
        )
        _assert_visible(
            page,
            '.nav-theme-panel [data-appearance-choice="system"]',
            f"{viewport.name} mode controls",
        )
    else:
        duplicate_toggles = page.locator("#theme-toggle").count()
        if duplicate_toggles:
            raise AssertionError(
                "desktop theme controls should not include #theme-toggle"
            )
        _assert_visible(page, ".theme-summary", f"{viewport.name} theme menu")
        page.locator(".theme-summary").click()
        _assert_visible(
            page,
            '.theme-popover [data-theme-select="desktop-menu"]',
            f"{viewport.name} theme select",
        )
        _assert_visible(
            page,
            '.theme-popover [data-appearance-choice="system"]',
            f"{viewport.name} mode controls",
        )
    _assert_no_horizontal_overflow(page, f"{viewport.name} theme controls")


def _check_theme_matrix(page: Page, base_url: str, viewport: Viewport) -> None:
    for theme in THEMES:
        for appearance in APPEARANCES:
            page.goto(f"{base_url}/", wait_until="domcontentloaded")
            page.evaluate(
                """([theme, appearance]) => {
                    localStorage.setItem('site_theme_v1', theme);
                    localStorage.setItem('site_appearance_v1', appearance);
                }""",
                [theme, appearance],
            )
            page.reload(wait_until="domcontentloaded")
            attrs = page.evaluate(
                """() => ({
                    theme: document.documentElement.getAttribute('data-theme'),
                    appearance: document.documentElement.getAttribute('data-appearance'),
                    bg: getComputedStyle(document.body).backgroundColor,
                    color: getComputedStyle(document.body).color
                })"""
            )
            if attrs["theme"] != theme or attrs["appearance"] != appearance:
                raise AssertionError(
                    f"{viewport.name} theme attrs mismatch for {theme}/{appearance}: {attrs}"
                )
            _assert_visible(
                page, ".hero-title", f"{viewport.name} {theme}/{appearance}"
            )
            _assert_no_horizontal_overflow(
                page, f"{viewport.name} {theme}/{appearance}"
            )


def run_browser_checks(headed: bool = False) -> None:
    _patch_external_services()
    port = _available_port()
    base_url = f"http://127.0.0.1:{port}"
    server = _start_server(port)
    try:
        _wait_for_server(base_url)
        viewports = [
            Viewport("desktop", 1280, 900),
            Viewport("mobile", 390, 844, is_mobile=True),
        ]
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not headed)
            try:
                for viewport in viewports:
                    page = browser.new_page(
                        viewport={"width": viewport.width, "height": viewport.height},
                        is_mobile=viewport.is_mobile,
                    )
                    try:
                        for route in ROUTES:
                            _check_route(page, base_url, route, viewport)
                        _check_theme_controls(page, base_url, viewport)
                        _check_theme_matrix(page, base_url, viewport)
                        if viewport.is_mobile:
                            _check_chat_mobile_interaction(page, base_url, viewport)
                        print(f"PASS {viewport.name} browser smoke")
                    finally:
                        page.close()
            finally:
                browser.close()
    finally:
        server.should_exit = True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Playwright desktop/mobile smoke checks against the FastHTML app."
    )
    parser.add_argument(
        "--headed", action="store_true", help="Run with a visible browser."
    )
    args = parser.parse_args()
    run_browser_checks(headed=args.headed)


if __name__ == "__main__":
    main()

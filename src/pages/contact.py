from __future__ import annotations

import time

import fasthtml.common as ft

from src.components.ui import ensure_url
from src.config import SiteConfig


def build_contact_page(
    query_params,
    config: SiteConfig,
    captcha_image: str,
):
    alert = _contact_alert(query_params)

    return ft.Section(
        ft.H2("Get In Touch", cls="section-title"),
        ft.Div(
            ft.Div(
                alert if alert else ft.Div(),
                ft.H3("Let's Connect"),
                ft.P(
                    "I'm always interested in discussing new opportunities, "
                    "interesting projects, or just having a chat about data science "
                    "and AI."
                ),
                ft.H4("Contact Information"),
                ft.P(f"📧 Email: {config.public_email or ''}"),
                ft.Div(
                    ft.A(
                        "💼 LinkedIn",
                        href=ensure_url(config.linkedin_url),
                        cls="icon-link",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                    ft.A(
                        "🐙 GitHub",
                        href=ensure_url(f"https://github.com/{config.github_username}")
                        if config.github_username
                        else "https://github.com/",
                        cls="icon-link",
                        target="_blank",
                        rel="noopener noreferrer",
                    ),
                    style=(
                        "display:flex; gap:.75rem; flex-wrap:wrap; "
                        "margin: .5rem 0 1rem;"
                    ),
                ),
                ft.H4("Response Time"),
                ft.P("I typically respond to emails within 24 hours."),
                cls="card",
            ),
            ft.Div(
                ft.H3("Send a Message"),
                ft.Form(
                    ft.Div(
                        ft.Label("Name", fr="name"),
                        ft.Input(
                            type="text",
                            id="name",
                            name="name",
                            required=True,
                            cls="form-input",
                        ),
                        cls="form-group",
                    ),
                    ft.Div(
                        ft.Label("Email", fr="email"),
                        ft.Input(
                            type="email",
                            id="email",
                            name="email",
                            required=True,
                            cls="form-input",
                        ),
                        cls="form-group",
                    ),
                    ft.Div(
                        ft.Label("Company", fr="company"),
                        ft.Input(
                            type="text",
                            id="company",
                            name="company",
                            cls="form-input",
                        ),
                        cls="hp-wrap",
                    ),
                    ft.Div(
                        ft.Label("Message", fr="message"),
                        ft.Textarea(
                            id="message",
                            name="message",
                            required=True,
                            rows=5,
                            cls="form-input",
                        ),
                        cls="form-group",
                    ),
                    ft.Input(type="hidden", name="t0", value=str(int(time.time()))),
                    ft.Div(
                        ft.Label("Verification", fr="captcha"),
                        ft.Img(
                            src=captcha_image,
                            alt="CAPTCHA",
                            style=(
                                "border:1px solid var(--border-color); "
                                "border-radius:4px; margin-bottom:0.5rem; "
                                "display:block;"
                            ),
                        ),
                        ft.Input(
                            type="text",
                            id="captcha",
                            name="captcha",
                            required=True,
                            placeholder="Enter the code above",
                            cls="form-input",
                        ),
                        cls="form-group",
                    ),
                    ft.Button("Send Message", type="submit", cls="btn"),
                    method="post",
                    action="/contact",
                    cls="contact-form",
                ),
                cls="card",
            ),
            cls="card-grid",
        ),
        cls="container section",
    )


def _contact_alert(query_params):
    if "sent" in query_params:
        return ft.Div(
            ft.P("Thanks! Your message was sent."),
            cls="card",
            style="border-left:4px solid var(--success-color);",
        )
    if "saved" in query_params:
        return ft.Div(
            ft.P("Message saved locally (email not configured)."),
            cls="card",
            style="border-left:4px solid var(--accent-color);",
        )
    if "err" in query_params:
        errmap = {
            "invalid": "Please check the fields and try again.",
            "ratelimit": "Too many messages recently — please try again later.",
            "verify": "Please complete the verification challenge.",
            "server": "We couldn't send your message right now. Please email me directly.",
        }
        msg = errmap.get(
            query_params.get("err"), "We couldn't send your message right now."
        )
        return ft.Div(
            ft.P(msg), cls="card", style="border-left:4px solid var(--error-color);"
        )
    return None

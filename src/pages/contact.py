from __future__ import annotations

import time

import fasthtml.common as ft

from src.components.patterns import Card, IconLink, InlineActions
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
            Card(
                alert if alert else ft.Div(),
                ft.H3("Let's Connect"),
                ft.P(config.contact_intro),
                ft.H4("Contact Information"),
                ft.P(f"📧 Email: {config.public_email or ''}"),
                InlineActions(
                    IconLink(
                        "💼 LinkedIn",
                        href=ensure_url(config.linkedin_url),
                    ),
                    IconLink(
                        "🐙 GitHub",
                        href=ensure_url(f"https://github.com/{config.github_username}")
                        if config.github_username
                        else "https://github.com/",
                    ),
                    cls="contact-links",
                ),
                ft.H4("Response Time"),
                ft.P(config.contact_response_time),
            ),
            Card(
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
                            cls="captcha-img",
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
            ),
            cls="card-grid",
        ),
        cls="container section",
    )


def _contact_alert(query_params):
    if "sent" in query_params:
        return Card(
            ft.P("Thanks! Your message was sent."),
            cls="alert-success",
        )
    if "saved" in query_params:
        return Card(
            ft.P("Message saved locally (email not configured)."),
            cls="alert-info",
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
        return Card(ft.P(msg), cls="alert-error")
    return None

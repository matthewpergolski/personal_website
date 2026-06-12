from __future__ import annotations

import time

import fasthtml.common as ft

from src.components.forms import CaptchaField, TextInput, TextareaField
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
        ft.H2(config.text("contact", "title", "Get In Touch"), cls="section-title"),
        ft.Div(
            Card(
                alert if alert else ft.Div(),
                ft.H3(config.text("contact", "intro_title", "Let's Connect")),
                ft.P(config.contact_intro),
                ft.H4(config.text("contact", "info_title", "Contact Information")),
                ft.P(
                    f"{config.text('contact', 'email_label', '📧 Email')}: "
                    f"{config.public_email or ''}"
                ),
                InlineActions(
                    IconLink(
                        config.text("contact", "linkedin_label", "💼 LinkedIn"),
                        href=ensure_url(config.linkedin_url),
                    ),
                    IconLink(
                        config.text("contact", "github_label", "🐙 GitHub"),
                        href=ensure_url(f"https://github.com/{config.github_username}")
                        if config.github_username
                        else "https://github.com/",
                    ),
                    cls="contact-links",
                ),
                ft.H4(config.text("contact", "response_title", "Response Time")),
                ft.P(config.contact_response_time),
            ),
            Card(
                ft.H3(config.text("contact", "form_title", "Send a Message")),
                ft.Form(
                    TextInput(
                        config.text("contact", "name_label", "Name"),
                        "name",
                        required=True,
                    ),
                    TextInput(
                        config.text("contact", "form_email_label", "Email"),
                        "email",
                        input_type="email",
                        required=True,
                    ),
                    TextInput(
                        config.text("contact", "company_label", "Company"),
                        "company",
                        cls="hp-wrap",
                    ),
                    TextareaField(
                        config.text("contact", "message_label", "Message"),
                        "message",
                        required=True,
                    ),
                    ft.Input(type="hidden", name="t0", value=str(int(time.time()))),
                    CaptchaField(captcha_image),
                    ft.Button(
                        config.text("contact", "submit_label", "Send Message"),
                        type="submit",
                        cls="btn",
                    ),
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

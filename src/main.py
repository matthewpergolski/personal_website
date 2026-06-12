#!/usr/bin/env python3
"""
FastHTML Portfolio Website - Main Application
A professional portfolio website built exclusively with FastHTML
to showcase GitHub projects and serve as a resume for technical roles.
"""

from dotenv import load_dotenv
import base64
import os
import asyncio
import hashlib
import hmac
import random
from pathlib import Path
import secrets
import string
from urllib.parse import urlparse
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from captcha.image import ImageCaptcha
from src.app_shell import create_app, mount_static
from src.services.github import fetch_github_profile, fetch_github_projects
from src.utils.render import render_page
from src.services.github import fetch_language_bytes_aggregate
from src.services.content import load_experience
from src.services.contact_form import (
    add_captcha_answer,
    consume_matching_captcha,
    contact_error_code,
    get_contact_thresholds,
    parse_contact_submission,
    save_local_message,
    validate_contact_fields,
)
from src.services.email import send_email
from src.config import get_config, BASE_DATA_DIR, ROOT_DIR
from src.pages.chat import build_chat_page
from src.pages.contact import build_contact_page
from src.pages.home import build_home_page
from src.pages.profile import build_about_page, build_resume_page
from src.pages.projects import build_projects_error, build_projects_page
from src.utils.rate_limit import CHAT_RATE_LIMIT, is_rate_limited
from src.services.rag.simple_chat import handle_chat_payload, sanitized_chat_history


load_dotenv("envs.sh")


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").lower() in ("1", "true", "yes", "on")


def assert_debug_disabled_on_vercel() -> None:
    if os.getenv("VERCEL") and _env_truthy("DEBUG"):
        raise RuntimeError("DEBUG must be disabled on Vercel deployments.")


assert_debug_disabled_on_vercel()


# =============================================================================
# Security & Reliability Utilities (added during security fixes)
# =============================================================================


def get_client_ip(request):
    """Best-effort real client IP, trusting proxy headers only behind a proxy."""
    if os.getenv("VERCEL") or _env_truthy("TRUST_PROXY_HEADERS"):
        for header in ("x-forwarded-for", "x-real-ip"):
            val = request.headers.get(header)
            if val:
                return val.split(",")[0].strip()
    return getattr(request.client, "host", "unknown") if request.client else "unknown"


def validate_startup_config() -> None:
    """Fail fast with clear messages if critical configuration is missing."""
    warnings = []
    errors = []

    if not os.getenv("GITHUB_USERNAME"):
        warnings.append("GITHUB_USERNAME not set — GitHub features disabled.")

    if not os.getenv("GITHUB_TOKEN"):
        errors.append("GITHUB_TOKEN is required for GitHub integration.")

    contact_dest = os.getenv("SMTP_TO") or os.getenv("CONTACT_EMAIL") or ""
    if not contact_dest:
        warnings.append(
            "No contact destination configured (contact form will save locally)."
        )

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")

    if errors:
        if _env_truthy("DEBUG"):
            print("DEBUG mode — continuing despite errors.")
        else:
            raise RuntimeError("Missing required environment variables.")


_captcha = ImageCaptcha(width=180, height=60)
SESSION_KEY_FNAME = "/tmp/.sesskey" if os.getenv("VERCEL") else ".sesskey"
SESSION_SECRET = os.getenv("SESSION_SECRET") or os.getenv("SECRET_KEY")
_RUNTIME_CAPTCHA_SECRET = secrets.token_bytes(32)


def _captcha_secret() -> bytes:
    """Return a server-side key for CAPTCHA answer hashing."""
    configured = (
        os.getenv("CAPTCHA_SECRET")
        or os.getenv("CONTACT_CAPTCHA_SECRET")
        or SESSION_SECRET
    )
    if configured:
        return configured.encode("utf-8")
    try:
        key_path = Path(SESSION_KEY_FNAME)
        if key_path.exists():
            return key_path.read_bytes()
    except Exception:
        pass
    return _RUNTIME_CAPTCHA_SECRET


def captcha_answer_hash(answer: str) -> str:
    """Hash a CAPTCHA answer without exposing it in the client session cookie."""
    normalized = answer.strip().upper().encode("utf-8")
    return hmac.new(_captcha_secret(), normalized, hashlib.sha256).hexdigest()


def generate_captcha() -> tuple[str, str]:
    """Generate a CAPTCHA image and return (data_url, answer)."""
    answer = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    data = _captcha.generate(answer)
    img_bytes = data.getvalue()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}", answer


# FastHTML app configuration lives in src/app_shell.py; src.main remains the
# stable Vercel entrypoint.
app = create_app(SESSION_KEY_FNAME, SESSION_SECRET)
mount_static(app)


# Routes
@app.get("/")
async def home():
    """Home page"""
    config = get_config()
    profile, lang_bytes, repos = await asyncio.gather(
        fetch_github_profile(),
        fetch_language_bytes_aggregate(),
        fetch_github_projects(),
    )
    experience_data = load_experience(ROOT_DIR) or {}

    return render_page(
        f"{config.owner_name} - {config.site_description}",
        *build_home_page(
            profile,
            lang_bytes,
            repos,
            experience_data,
            config.github_username,
        ),
    )


@app.get("/projects")
async def projects():
    """Projects page with GitHub integration"""
    config = get_config()
    try:
        projects_data, profile = await asyncio.gather(
            fetch_github_projects(), fetch_github_profile()
        )
        projects_content = build_projects_page(
            projects_data, profile, config.github_username
        )
    except Exception as e:
        projects_content = build_projects_error(e)

    return render_page(
        f"Projects - {config.owner_name}",
        projects_content,
    )


@app.get("/about")
async def about():
    """About page with hero, highlights, mini timeline, and snapshot panel."""
    config = get_config()
    data = load_experience(ROOT_DIR) or {}
    profile = await fetch_github_profile()

    return render_page(
        f"About - {config.owner_name}",
        build_about_page(data, profile, config),
    )


@app.get("/resume")
def resume():
    """Resume page"""
    config = get_config()
    data = load_experience(ROOT_DIR) or {}

    return render_page(
        f"Resume - {config.owner_name}",
        build_resume_page(data, config),
    )


@app.get("/contact")
def contact(req: Request):
    """Contact page"""
    config = get_config()
    # Generate self-hosted CAPTCHA and store with timestamp (supports multiple tabs)
    captcha_image, captcha_answer = generate_captcha()
    add_captcha_answer(req.session, captcha_answer_hash(captcha_answer))

    return render_page(
        f"Contact - {config.owner_name}",
        build_contact_page(req.query_params, config, captcha_image),
    )


@app.get("/chat")
def chat_page():
    """Dedicated chat page with the same session-scoped conversation as the widget."""
    config = get_config()
    return render_page(
        f"Chat - {config.owner_name}",
        build_chat_page(),
        include_chat=False,
    )


@app.post("/api/rag/chat")
async def rag_chat(req: Request):
    """Answer portfolio questions with local retrieval and optional free HF generation."""
    ip = get_client_ip(req)
    if is_rate_limited(ip, CHAT_RATE_LIMIT):
        return JSONResponse(
            {
                "success": False,
                "error": "Too many chat requests. Please try again later.",
            },
            status_code=429,
        )

    try:
        payload = await req.json()
    except Exception:
        return JSONResponse(
            {"success": False, "error": "Invalid JSON."}, status_code=400
        )

    history = sanitized_chat_history(req.session.get("chat_history"))
    result = await handle_chat_payload(payload, history=history)
    if result.get("success"):
        message = str(payload.get("message") or "").strip()
        history.extend(
            [
                {"role": "user", "content": message[:240]},
                {
                    "role": "assistant",
                    "content": str(result.get("response") or "")[:240],
                },
            ]
        )
        req.session["chat_history"] = sanitized_chat_history(history)
    status = 200 if result.get("success") else 400
    return JSONResponse(result, status_code=status)


@app.post("/api/rag/chat/reset")
async def rag_chat_reset(req: Request):
    """Clear server-side chat history for this browser session."""
    req.session["chat_history"] = []
    return JSONResponse({"success": True})


@app.post("/contact")
async def contact_submit(req: Request):
    """Handle contact form submission: try SMTP, else save locally."""
    try:
        form = await req.form()
        submission = parse_contact_submission(form)

        if submission.company:
            # Silently accept to mislead bots
            return RedirectResponse("/contact", status_code=303)

        errs = validate_contact_fields(submission, get_contact_thresholds())
        if not consume_matching_captcha(
            req.session, submission.captcha, captcha_answer_hash
        ):
            errs.append("Please enter the correct verification code.")

        # Consolidated rate limiting (per-IP + global)
        ip = get_client_ip(req)
        if not errs and is_rate_limited(ip):
            errs.append("Too many messages recently — please try again later.")

        if not errs:
            subject = f"Portfolio Contact from {submission.name}"
            body = (
                f"From: {submission.name} <{submission.email}>\n\n{submission.message}"
            )
            ok, info = await send_email(subject, body, reply_to=submission.email)
            if ok:
                return RedirectResponse("/contact?sent=1", status_code=303)
            else:
                if os.getenv("VERCEL"):
                    print(
                        f"Email send failed; local fallback disabled on Vercel: {info}"
                    )
                    return RedirectResponse("/contact?err=server", status_code=303)
                # Fallback: persist to data/messages
                try:
                    save_local_message(BASE_DATA_DIR, submission)
                    return RedirectResponse("/contact?saved=1", status_code=303)
                except Exception:
                    return RedirectResponse("/contact?err=server", status_code=303)
        else:
            # Prefer simple redirect with error code to avoid re-post on refresh
            return RedirectResponse(
                f"/contact?err={contact_error_code(errs)}", status_code=303
            )

    except Exception:
        return RedirectResponse("/contact", status_code=303)


@app.get("/resume/download")
def resume_download():
    """Redirect to the configured resume URL or local static fallback."""
    url = _safe_resume_download_url(get_config().resume_url)
    return RedirectResponse(url, status_code=307)


def _safe_resume_download_url(url: str | None) -> str:
    fallback = "/static/resume.pdf"
    candidate = (url or "").strip()
    if not candidate:
        return fallback
    if candidate.startswith("/static/") and not candidate.startswith("//"):
        return candidate

    parsed = urlparse(candidate)
    if parsed.scheme != "https" or not parsed.netloc:
        return fallback

    allowed_hosts = [
        host.strip().lower()
        for host in os.getenv("RESUME_URL_ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ]
    if (
        allowed_hosts
        and parsed.hostname
        and parsed.hostname.lower() not in allowed_hosts
    ):
        return fallback
    return candidate


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

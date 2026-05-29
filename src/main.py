#!/usr/bin/env python3
"""
FastHTML Portfolio Website - Main Application
A professional portfolio website built exclusively with FastHTML
to showcase GitHub projects and serve as a resume for technical roles.
"""

from fasthtml import FastHTML
import fasthtml.common as ft
from fasthtml.common import (
    A,
    Button,
    Div,
    H2,
    H3,
    Img,
    Link,
    P,
    Script,
    Section,
    Span,
    Style,
)
from dotenv import load_dotenv
import base64
import os
import json
import asyncio
import hashlib
import hmac
import random
from pathlib import Path
import secrets
import string
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
import time
from captcha.image import ImageCaptcha
from src.services.github import fetch_github_profile, fetch_github_projects
from src.components.ui import HeroSection, display_role_title, ensure_url
from src.utils.render import render_page
from src.services.github import fetch_language_bytes_aggregate
from src.services.content import load_experience
from src.services.email import send_email
from src.config import get_config, BASE_DATA_DIR
from src.utils.rate_limit import is_rate_limited
from src.components.chat.widget import ChatWidget
from src.services.rag.simple_chat import handle_chat_payload


load_dotenv("envs.sh")


# =============================================================================
# Security & Reliability Utilities (added during security fixes)
# =============================================================================


def get_client_ip(request):
    """Best-effort real client IP, respecting common proxy headers."""
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
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
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


CFG = get_config()

# FastHTML App Configuration
app = FastHTML(
    # On Vercel's serverless runtime, the filesystem is read-only except for /tmp.
    # Ensure FastHTML does not try to write the default .sesskey in CWD.
    key_fname=SESSION_KEY_FNAME,
    secret_key=SESSION_SECRET,
    sess_https_only=bool(os.getenv("VERCEL")),
    title=os.getenv("SITE_TITLE", "Professional Portfolio"),
    hdrs=(
        Link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        ),
        # Theme Styles
        Link(rel="icon", type="image/svg+xml", href="/static/favicon.svg"),
        Style("""
            :root {
                --primary-color: #2563eb;
                --secondary-color: #64748b;
                --accent-color: #f59e0b;
                --dark-color: #1e293b;
                --light-color: #f8fafc;
                --text-color: #334155;
                --border-color: #e2e8f0;
                --surface-1: #ffffff;
                --surface-2: #f8fafc;
                --muted-text: #64748b;
                --chip-bg: #eff6ff;
                --chip-border: #dbeafe;
                --chip-fg: #1e40af;
                --success-color: #10b981;
                --error-color: #ef4444;
                --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            /* Dark theme overrides */
            html[data-theme='dark'] {
                --primary-color: #60a5fa;
                --secondary-color: #94a3b8;
                --accent-color: #fbbf24;
                --dark-color: #0b1220;       /* base canvas color */
                --light-color: #0b1220;      /* page background */
                --text-color: #e2e8f0;       /* primary text */
                --muted-text: #94a3b8;       /* secondary text */
                --border-color: #1f2937;     /* outlines */
                --surface-1: #0f172a;        /* cards, nav, panels */
                --surface-2: #111827;        /* subtle elevated */
                --chip-bg: #111827;
                --chip-border: #334155;
                --chip-fg: #93c5fd;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: var(--font-family);
                line-height: 1.6;
                color: var(--text-color);
                background: var(--light-color);
                position: relative;
            }

            /* Subtle interactive glow following the cursor */
            body::before {
                content: "";
                position: fixed;
                inset: 0;
                background: radial-gradient(800px 400px at var(--glow-x, 50%) var(--glow-y, -20%), rgba(255,255,255,.06), transparent 70%);
                pointer-events: none;
                z-index: 0;
            }

            /* Asteroid belt canvas layer */
            #asteroid-belt { position: fixed; left:0; top:0; width:100vw; height:100vh; z-index: 0; pointer-events: none; opacity: var(--starfield-opacity, .18); }
            @media (prefers-reduced-motion: reduce) { body::before { display: none; } }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1rem;
            }

            @media (min-width: 768px) {
                .container {
                    padding: 0 2rem;
                }
            }

            .hero-section {
                background:
                    radial-gradient(900px 420px at 18% 10%, rgba(96,165,250,.22), transparent 65%),
                    radial-gradient(740px 360px at 88% 16%, rgba(251,191,36,.10), transparent 60%),
                    linear-gradient(180deg, rgba(15,23,42,.02), transparent);
                color: var(--text-color);
                padding: 4.5rem 0 4rem;
                text-align: left;
                position: relative;
                overflow: hidden;
                border-bottom: 1px solid var(--border-color);
            }

            .hero-layout {
                display: grid;
                grid-template-columns: minmax(0, 1.35fr) minmax(260px, .65fr);
                gap: 2rem;
                align-items: center;
            }

            .hero-copy { max-width: 780px; }

            .hero-kicker {
                color: var(--primary-color);
                font-weight: 700;
                margin-bottom: .75rem;
                text-transform: uppercase;
                font-size: .85rem;
            }

            .hero-actions {
                display: flex;
                gap: .75rem;
                flex-wrap: wrap;
                margin-top: 1.5rem;
            }

            .hero-aside {
                display: grid;
                justify-items: center;
                gap: 1rem;
            }

            .hero-current {
                width: min(100%, 360px);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1rem;
                background: color-mix(in srgb, var(--surface-1) 82%, transparent);
            }

            .hero-meta-label,
            .hero-meta-sub {
                display: block;
                color: var(--muted-text);
                font-size: .9rem;
            }

            .hero-meta-main {
                display: block;
                color: var(--text-color);
                font-weight: 800;
                line-height: 1.2;
                margin: .25rem 0;
            }

            .hero-title {
                font-size: 3rem;
                font-weight: 700;
                line-height: 1.05;
                margin-bottom: .85rem;
            }

            .hero-subtitle {
                color: var(--primary-color);
                font-size: 1.15rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }

            .hero-description {
                color: var(--text-color);
                font-size: 1.05rem;
                max-width: 760px;
                line-height: 1.55;
            }

            @media (max-width: 800px) {
                .hero-section { padding: 3rem 0; }
                .hero-layout { grid-template-columns: 1fr; text-align: center; }
                .hero-actions { justify-content: center; }
                .hero-title { font-size: 2.25rem; }
                .hero-description {
                    display: -webkit-box;
                    -webkit-line-clamp: 5;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }
                .hero-aside .avatar-lg { display: none; }
            }

            .avatar {
                width: 160px;
                height: 160px;
                border-radius: 50%;
                box-shadow: 0 0 0 2px rgba(37,99,235,.28), 0 10px 30px rgba(0,0,0,0.25);
                border: 3px solid rgba(255,255,255,0.75);
                margin-bottom: 1rem;
                transition: box-shadow .2s ease, transform .2s ease;
            }
            .avatar:hover { box-shadow: 0 0 0 3px rgba(37,99,235,.45), 0 14px 36px rgba(0,0,0,.35); transform: translateY(-1px) scale(1.01); }
            .avatar:active { transform: scale(.995); }
            .avatar-lg { width: 160px; height: 160px; }
            @media (max-width: 640px){ .avatar-lg { width: 112px; height: 112px; } }

            .nav {
                background: var(--surface-1);
                padding: 1rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                position: sticky;
                top: 0;
                z-index: 1000; /* keep above hero visuals */
            }
            .nav-toggle { display: none; }
            .menu-hint { display: none; }
            .nav-close { display: none; }
            .nav-toggle { cursor: pointer; }

            .nav-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .nav-brand { display: inline-flex; align-items: center; gap: .6rem; text-decoration: none; }
            .brand-initials { font-size: 1.1rem; font-weight: 700; color: var(--text-color); }
            .brand-sub { font-size: .95rem; color: var(--muted-text); font-weight: 600; }
            .brand-logo { width: 28px; height: 28px; border-radius: 999px; border: 1px solid var(--border-color); }

            .nav-links {
                display: flex;
                gap: 2rem;
            }

            .nav-link {
                color: var(--text-color);
                text-decoration: none;
                font-weight: 500;
                transition: color 0.2s;
            }

            .nav-link:hover {
                color: var(--primary-color);
            }

            @media (max-width: 768px) {
                .nav-container { gap: .5rem; }
                .nav-toggle { display: inline-flex; align-items:center; justify-content:center; padding:.5rem .75rem; border:1px solid var(--border-color); border-radius:8px; background:var(--surface-1); color:var(--text-color); position: relative; z-index: 1002; }
                .brand-sub { display: none; }
                /* Off‑canvas menu */
                .nav-links {
                    display: flex; flex-direction: column; gap: .5rem;
                    position: fixed; top: 0; right: 0; height: 100svh; width: min(82vw, 340px);
                    background: var(--surface-1); border-left: 1px solid var(--border-color);
                    padding: 4.5rem 1rem 1rem; box-shadow: -16px 0 40px rgba(0,0,0,.35);
                    transform: translateX(100%); transition: transform .2s ease;
                    z-index: 1001; overflow-y: auto;
                }
                .nav.open .nav-links { transform: translateX(0); }
                body.nav-open::after { content:""; position: fixed; inset: 0; background: rgba(0,0,0,.45); backdrop-filter: blur(1px); z-index: 999; }
                body.nav-open { overflow: hidden; }
                .nav.open .nav-actions { display: none !important; }
                .nav-link { padding:.5rem 0; font-size: 1.05rem; }
                .nav-actions { display: none; }
                /* Tone down background effects on mobile */
                body { --starfield-opacity: .10; }
                /* In-panel close button */
                .nav-close { display:inline-flex; position: absolute; top: .9rem; right: .9rem; height: 36px; width: 36px; align-items:center; justify-content:center; border-radius:10px; border:1px solid var(--border-color); background: var(--surface-1); color: var(--text-color); font-size: 1.25rem; }
                .nav-close:active { transform: scale(.98); }
                /* Wiggle animation for first-time users */
                @keyframes wiggle { 0%{ transform: rotate(0) translateY(0); } 30%{ transform: rotate(7deg) translateY(-1px);} 60%{ transform: rotate(-7deg) translateY(-1px);} 100%{ transform: rotate(0) translateY(0);} }
                .nav-toggle.nudge { animation: wiggle .7s ease-in-out 0s 2; }
            }

            .nav-actions {
                display: flex;
                gap: .75rem;
                align-items: center;
            }

            @media (max-width: 768px) {
                .nav-actions { display: none !important; }
                .nav-container { justify-content: space-between; }
                .nav-toggle { margin-left: auto; }
            }

            .icon-link {
                display: inline-flex;
                align-items: center;
                gap: .5rem;
                padding: .5rem .75rem;
                border: 1px solid var(--border-color);
                border-radius: 999px;
                text-decoration: none;
                color: var(--text-color);
                background: var(--surface-1);
                transition: transform .15s ease, box-shadow .15s ease;
                box-shadow: 0 1px 2px rgba(0,0,0,.05);
            }
            .icon-link:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }

            .theme-toggle { cursor: pointer; }

            .section {
                padding: 4rem 0;
            }

            /* Mobile bottom tab bar */
            .mobile-tabbar { display:none; }
            .mobile-tabbar { position: fixed; left:0; right:0; bottom:0; height: 64px; display:none; background: rgba(15,23,42,.86); border-top: 1px solid var(--border-color); backdrop-filter: blur(10px); z-index: 999; align-items:center; justify-content: space-around; padding: 0 max(8px, env(safe-area-inset-left)) calc(max(6px, env(safe-area-inset-bottom))); }
            .mobile-tabbar .tab { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:2px; color: var(--muted-text); text-decoration:none; font-weight:600; font-size:.8rem; padding:.35rem .4rem; border-radius:8px; }
            .mobile-tabbar .tab-ico { font-size: 1.15rem; line-height:1; }
            .mobile-tabbar .tab.active { color:#fff; background: rgba(37,99,235,.22); }
            @media (max-width: 768px) {
                .mobile-tabbar { display:flex; }
                body { padding-bottom: 74px; }
                /* Hide when menu is open */
                .nav.open ~ .mobile-tabbar { transform: translateY(110%); transition: transform .2s ease; }
            }

            .section-title {
                font-size: 2.5rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 3rem;
                color: var(--text-color);
            }

            .highlight-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 1rem;
            }

            .highlight-card {
                min-height: 190px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1.25rem;
                background: var(--surface-1);
                box-shadow: 0 10px 30px rgba(0,0,0,.12);
            }

            .highlight-index {
                display: block;
                color: var(--primary-color);
                font-size: .85rem;
                font-weight: 800;
                margin-bottom: .8rem;
            }

            .highlight-copy {
                color: var(--text-color);
                font-weight: 650;
                line-height: 1.5;
            }

            @media (max-width: 900px) {
                .highlight-grid { grid-template-columns: 1fr; }
                .highlight-card { min-height: auto; }
            }

            .resume-callout {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                margin: -1.5rem auto 2rem;
                padding: 1rem 1.25rem;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                background: var(--surface-1);
            }

            .resume-callout p { color: var(--muted-text); margin: .15rem 0 0; }
            .resume-callout .btn { flex: 0 0 auto; white-space: nowrap; }

            @media (max-width: 700px) {
                .resume-callout { align-items: stretch; flex-direction: column; }
                .resume-callout .btn { text-align: center; }
            }

            /* About hero */
            .about-hero {
                background: radial-gradient(900px 400px at 10% -10%, rgba(255,255,255,0.06), transparent),
                            linear-gradient(180deg, rgba(255,255,255,0.02), transparent);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 2rem;
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 1.25rem;
                align-items: center;
            }
            @media (max-width: 640px){ .about-hero { grid-template-columns: 1fr; text-align:center; } }

            .hero-cta { display:flex; gap:.75rem; flex-wrap:wrap; }
            @media (max-width: 640px){
                .hero-cta { justify-content:center; }
                .hero-cta .btn { width: 100%; max-width: 320px; }
            }

            /* Stats */
            .stats-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: .75rem; }
            .stat-card { background: var(--surface-1); border:1px solid var(--border-color); border-radius:12px; padding: .9rem; text-align:center; }
            .stat-num { font-weight:700; font-size:1.25rem; color: var(--text-color); }
            .stat-label { color: var(--muted-text); font-size:.9rem; }

            /* Timeline */
            .timeline { position: relative; margin-left: .75rem; }
            .timeline::before { content:""; position:absolute; left:-.75rem; top:0; bottom:0; width:2px; background: var(--border-color); }
            .timeline-item { position: relative; margin: 0 0 1rem 0; padding-left: .75rem; }
            .timeline-item::before { content:""; position:absolute; left:-.95rem; top:.45rem; width:8px; height:8px; border-radius:50%; background: var(--primary-color); box-shadow:0 0 0 2px var(--surface-1); }

            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-top: 2rem;
            }

            /* Two-column emphasis grid (wide:narrow) */
            .grid-2-1 {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
                align-items: start;
            }
            @media (max-width: 980px) { .grid-2-1 { grid-template-columns: 1fr; } }

            .card {
                background: var(--surface-1);
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                border: 1px solid var(--border-color);
            }

            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }

            .card-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: var(--text-color);
                line-height: 1.2;
                overflow-wrap: anywhere; /* allow breaking long identifiers */
                word-break: break-word;
                max-width: 100%;
            }

            .card-subtitle {
                color: var(--secondary-color);
                margin-bottom: 1rem;
            }

            .card-description {
                color: var(--text-color);
                margin-bottom: 1.5rem;
            }

            .chips { display: flex; gap: .5rem; flex-wrap: wrap; }
            .chip { padding: .25rem .6rem; border-radius: 999px; font-size: .8rem; background: var(--chip-bg); color: var(--chip-fg); border: 1px solid var(--chip-border); }

            .btn {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: var(--primary-color);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 500;
                transition: background 0.2s;
                border: none;
                cursor: pointer;
            }

            .btn:hover {
                background: #1d4ed8;
            }

            .btn-secondary {
                background: var(--secondary-color);
            }

            .btn-secondary:hover {
                background: #475569;
            }

            .footer {
                background: var(--surface-2);
                color: white;
                padding: 3rem 0 1rem;
                text-align: center;
            }

            .loading {
                text-align: center;
                padding: 2rem;
                color: var(--secondary-color);
            }

            .error {
                color: var(--error-color);
                padding: 1rem;
                background: #fef2f2;
                border-radius: 8px;
                border: 1px solid #fecaca;
            }

            /* Forms */
            input, textarea, select, .form-input {
                background: var(--surface-1);
                color: var(--text-color);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: .6rem .75rem;
                outline: none;
            }
            input::placeholder, textarea::placeholder { color: var(--muted-text); }
            input:focus, textarea:focus, select:focus { border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(37,99,235,.25); }

            /* Typography rhythm */
            p { margin: 0 0 1rem; }
            h3 { margin: 1rem 0 .5rem; }
            h4 { margin: .75rem 0 .25rem; }
            ul { margin: .5rem 0 1rem 1.25rem; }
            li { margin: .25rem 0; }
            .chart-controls .icon-link.active { background: var(--primary-color); color: #fff; border-color: transparent; }
            .contact-form { display:grid; gap:1rem; max-width: 720px; }
            .contact-form .form-group { display:block; width:100%; }
            .contact-form label { display:block; font-weight:600; margin-bottom:.35rem; color: var(--muted-text); }
            .contact-form input, .contact-form textarea { width:100%; }
            .contact-form textarea { min-height:160px; resize:vertical; }
            .hp-wrap { position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden; }
        """),
        # Plotly for interactive charts
        Script(src="https://cdn.plot.ly/plotly-2.35.2.min.js"),
        # Dark mode toggle persistence
        Script("""
            (function(){
              try {
                const saved = localStorage.getItem('theme_v2');
                const theme = saved || 'dark';
                document.documentElement.setAttribute('data-theme', theme);
                document.addEventListener('DOMContentLoaded', function(){
                  const btn = document.getElementById('theme-toggle');
                  if (!btn) return;
                  btn.addEventListener('click', function(){
                    const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                    document.documentElement.setAttribute('data-theme', cur);
                    localStorage.setItem('theme_v2', cur);
                  });
                });
              } catch(e){}
            })();
        """),
        # Mouse-follow glow effect
        Script(r"""
          (function(){
            document.addEventListener('mousemove', function(e){
              try{
                document.documentElement.style.setProperty('--glow-x', e.clientX+'px');
                document.documentElement.style.setProperty('--glow-y', e.clientY+'px');
              }catch(_){}
            });
            // Mobile nav toggle + close on link/escape/outside; first-time wiggle
            document.addEventListener('DOMContentLoaded', function(){
              try{
                var seen = localStorage.getItem('menu_hint_seen') === '1';
                var btn = document.getElementById('nav-toggle');
                if (btn && !seen && window.innerWidth <= 768) {
                  btn.classList.add('nudge');
                  setTimeout(function(){ try{ btn.classList.remove('nudge'); localStorage.setItem('menu_hint_seen','1'); }catch(_){} }, 1600);
                }
              }catch(_){ }
            });

            document.addEventListener('click', function(e){
              var t = e.target;
              var nav = document.querySelector('.nav');
              var links = document.getElementById('nav-links');
              if (t && (t.id === 'nav-close')) {
                if (nav) {
                  nav.classList.remove('open');
                  document.body.classList.remove('nav-open');
                  try{ var b = document.getElementById('nav-toggle'); if(b) b.setAttribute('aria-expanded','false'); }catch(_){}
                }
                return;
              }
              if (t && t.id === 'nav-toggle') {
                if (nav) {
                  var open = nav.classList.toggle('open');
                  document.body.classList.toggle('nav-open', open);
                  try{ var btn = document.getElementById('nav-toggle'); if(btn) btn.setAttribute('aria-expanded', open?'true':'false'); }catch(_){}
                }
                return;
              }
              if (nav && nav.classList.contains('open')) {
                var withinLinks = links && (links.contains(t) || (t.closest && t.closest('#nav-links')));
                var isToggle = (t.id === 'nav-toggle');
                if (!withinLinks && !isToggle) {
                  nav.classList.remove('open');
                  document.body.classList.remove('nav-open');
                  try{ var btn = document.getElementById('nav-toggle'); if(btn) btn.setAttribute('aria-expanded','false'); }catch(_){}
                }
              }
            });
            document.addEventListener('keydown', function(e){
              if (e.key === 'Escape') {
                var nav = document.querySelector('.nav');
                if (nav && nav.classList.contains('open')) {
                  nav.classList.remove('open');
                  document.body.classList.remove('nav-open');
                }
              }
            });
            // Highlight active tab in the bottom tab bar
            document.addEventListener('DOMContentLoaded', function(){
              try{
                var p = location.pathname || '/';
                var id = p.startsWith('/projects') ? 'tab-projects'
                      : p.startsWith('/about') ? 'tab-about'
                      : p.startsWith('/resume') ? 'tab-resume'
                      : p.startsWith('/chat') ? 'tab-chat'
                      : p.startsWith('/contact') ? 'tab-contact'
                      : 'tab-home';
                var el = document.getElementById(id);
                if (el) el.classList.add('active');
              }catch(_){ }
            });

            // Basic edge-swipe gestures (open from right edge, close by swiping right on panel)
            (function(){
              var startX=0, startY=0, trackingOpen=false, trackingClose=false;
              document.addEventListener('touchstart', function(e){
                try{
                  var t=e.touches&&e.touches[0]; if(!t) return;
                  startX=t.clientX; startY=t.clientY;
                  var nav=document.querySelector('.nav'); var links=document.getElementById('nav-links');
                  var edge=24;
                  if(nav && !nav.classList.contains('open') && startX > (window.innerWidth-edge)) trackingOpen=true;
                  else if(nav && nav.classList.contains('open') && links && links.contains(e.target)) trackingClose=true;
                }catch(_){}
              }, {passive:true});
              document.addEventListener('touchmove', function(e){
                try{
                  var t=e.touches&&e.touches[0]; if(!t) return; var dx=t.clientX-startX; var dy=t.clientY-startY;
                  if(Math.abs(dy) > 40) { trackingOpen=false; trackingClose=false; return; }
                  var nav=document.querySelector('.nav');
                  if(trackingOpen && dx < -50) { if(nav){ nav.classList.add('open'); document.body.classList.add('nav-open'); try{var b=document.getElementById('nav-toggle'); if(b) b.setAttribute('aria-expanded','true');}catch(_){} } trackingOpen=false; }
                  if(trackingClose && dx > 50) { if(nav){ nav.classList.remove('open'); document.body.classList.remove('nav-open'); try{var b=document.getElementById('nav-toggle'); if(b) b.setAttribute('aria-expanded','false');}catch(_){} } trackingClose=false; }
                }catch(_){}
              }, {passive:true});
              document.addEventListener('touchend', function(){ trackingOpen=false; trackingClose=false; }, {passive:true});
            })();

            // Basic edge-swipe gestures (open from right edge, close by swiping right on panel)
            (function(){
              var startX=0, startY=0, trackingOpen=false, trackingClose=false;
              document.addEventListener('touchstart', function(e){
                try{
                  var t=e.touches&&e.touches[0]; if(!t) return;
                  startX=t.clientX; startY=t.clientY;
                  var nav=document.querySelector('.nav'); var links=document.getElementById('nav-links');
                  var edge=24;
                  if(nav && !nav.classList.contains('open') && startX > (window.innerWidth-edge)) trackingOpen=true;
                  else if(nav && nav.classList.contains('open') && links && links.contains(e.target)) trackingClose=true;
                }catch(_){}
              }, {passive:true});
              document.addEventListener('touchmove', function(e){
                try{
                  var t=e.touches&&e.touches[0]; if(!t) return; var dx=t.clientX-startX; var dy=t.clientY-startY;
                  if(Math.abs(dy) > 40) { trackingOpen=false; trackingClose=false; return; }
                  var nav=document.querySelector('.nav');
                  if(trackingOpen && dx < -50) { if(nav){ nav.classList.add('open'); document.body.classList.add('nav-open'); try{var b=document.getElementById('nav-toggle'); if(b) b.setAttribute('aria-expanded','true');}catch(_){} } trackingOpen=false; }
                  if(trackingClose && dx > 50) { if(nav){ nav.classList.remove('open'); document.body.classList.remove('nav-open'); try{var b=document.getElementById('nav-toggle'); if(b) b.setAttribute('aria-expanded','false');}catch(_){} } trackingClose=false; }
                }catch(_){}
              }, {passive:true});
              document.addEventListener('touchend', function(){ trackingOpen=false; trackingClose=false; }, {passive:true});
            })();
            // Starfield: layered parallax stars drifting across the viewport
            function initBelt(){
              if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
              var c = document.getElementById('asteroid-belt');
              if (!c) return;
              var ctx = c.getContext('2d');
              var dpr = Math.min(window.devicePixelRatio || 1, 2);
              function resize(){
                // Ensure canvas covers full viewport regardless of parent layout
                c.style.width = '100vw';
                c.style.height = '100vh';
                c.width = Math.floor((window.innerWidth || document.documentElement.clientWidth) * dpr);
                c.height = Math.floor((window.innerHeight || document.documentElement.clientHeight) * dpr);
              }
              resize();
              window.addEventListener('resize', resize);
              var W=()=>c.width, H=()=>c.height; // in device pixels
              var textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim() || '#e2e8f0';
              var col = 'rgba(255,255,255,0.6)';
              try{ // derive color from CSS var (approx)
                var tmp = document.createElement('canvas');
                var tctx = tmp.getContext('2d');
                tctx.fillStyle = textColor; // may be rgb(...)
                col = tctx.fillStyle.replace('rgb','rgba').replace(')',' ,0.55)');
              }catch(_){ }
              function makeLayer(count, speed, sizeMin, sizeMax){
                var arr=[]; for (var i=0;i<count;i++){
                  arr.push({
                    x: Math.random()*W(),
                    y: Math.random()*H(),
                    s: (sizeMin + Math.random()*(sizeMax-sizeMin)) * dpr,
                    v: speed * (0.6 + Math.random()*0.8),
                    tw: Math.random()*Math.PI*2,
                    tws: 0.015 + Math.random()*0.03
                  });
                } return arr;
              }
              var baseCount = (Math.min(c.clientWidth, c.clientHeight) > 900) ? 140 : 90;
              var layer1 = makeLayer(Math.floor(baseCount*0.5), 0.02, 0.5, 1.2);
              var layer2 = makeLayer(Math.floor(baseCount*0.35), 0.04, 0.8, 1.8);
              var layer3 = makeLayer(Math.floor(baseCount*0.15), 0.07, 1.2, 2.4);
              var layers = [layer1, layer2, layer3];
              var lastT=0, paused=false;
              document.addEventListener('visibilitychange', ()=>{ paused = document.hidden; });
              function tick(t){
                if(paused){ requestAnimationFrame(tick); return; }
                var dt = Math.min(32, (t-lastT)||16); lastT=t;
                ctx.clearRect(0,0,W(),H());
                for (var li=0; li<layers.length; li++){
                  var arr = layers[li];
                  for (var i=0;i<arr.length;i++){
                    var p=arr[i];
                    p.x += p.v*dt; // drift to the right
                    if (p.x > W()+10) p.x = -10;
                    // gentle vertical drift
                    p.y += Math.sin((p.tw + t*0.0003)) * 0.02 * dt;
                    if (p.y < -10) p.y = H()+10; else if (p.y > H()+10) p.y = -10;
                    p.tw += p.tws*dt/16;
                    var alpha = 0.18 + 0.22*Math.abs(Math.sin(p.tw));
                    ctx.fillStyle = col.replace(/\d?\.\d+\)/,' '+alpha.toFixed(2)+')');
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.s, 0, Math.PI*2);
                    ctx.fill();
                  }
                }
                requestAnimationFrame(tick);
              }
              requestAnimationFrame(tick);
            }
            document.addEventListener('DOMContentLoaded', initBelt);
          })();
        """),
    ),
)

# Mount static files at /static using project-relative data/static
ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(os.getenv("STATIC_DIR", ROOT_DIR / "data" / "static"))
try:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception:
    # Safe no-op if mounting fails in some environments
    pass

# GitHub API calls moved to src/services/github.py

"""UI components moved to src/components/ui.py"""

"""render_page helper moved to src/utils/render.py"""


# Routes
@app.get("/")
async def home():
    """Home page"""
    profile, lang_bytes, repos = await asyncio.gather(
        fetch_github_profile(),
        fetch_language_bytes_aggregate(),
        fetch_github_projects(),
    )
    # Build top languages from aggregated byte counts
    items = sorted(
        [(name, value) for name, value in (lang_bytes or {}).items() if value > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    top = items[:8]
    if len(items) > 8:
        others_total = sum(v for _, v in items[8:])
        top.append(("Others", others_total))
    labels_bytes = [k for k, _ in top]
    values_bytes = [v for _, v in top]
    # Repo counts by primary language (for metric toggle)
    lang_counts = {}
    for r in repos or []:
        lang = r.get("language") or "Other"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    repo_items = sorted(
        [(name, value) for name, value in lang_counts.items() if value > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    repo_top = repo_items[:8]
    if len(repo_items) > 8:
        repo_top.append(("Others", sum(v for _, v in repo_items[8:])))
    labels_repos = [k for k, _ in repo_top]
    values_repos = [v for _, v in repo_top]

    # Load highlights content
    highlights = []
    experience_data = {}
    try:
        from pathlib import Path

        experience_data = load_experience(Path(__file__).resolve().parent.parent) or {}
        if isinstance(experience_data.get("highlights"), list):
            highlights = [str(x) for x in experience_data["highlights"]][:6]
    except Exception:
        pass

    highlights_section = (
        Section(
            H2("Highlights", cls="section-title"),
            Div(
                *[
                    Div(
                        Span(f"{idx:02d}", cls="highlight-index"),
                        P(h, cls="highlight-copy"),
                        cls="highlight-card",
                    )
                    for idx, h in enumerate(highlights[:3], start=1)
                ],
                cls="container highlight-grid",
            ),
            cls="section",
        )
        if highlights
        else Div()
    )

    chart_section = (
        Section(
            H2("Tech Stack Snapshot", cls="section-title"),
            Div(
                Div(
                    Div(
                        Div(
                            Span("View:"),
                            Button("Donut", id="chart-donut", cls="icon-link"),
                            Button("Bar", id="chart-bar", cls="icon-link"),
                            Button("Treemap", id="chart-tree", cls="icon-link"),
                            Span("Metric:"),
                            Button("Repos", id="metric-repos", cls="icon-link"),
                            Button("Bytes", id="metric-bytes", cls="icon-link"),
                            Button("Export PNG", id="chart-export", cls="icon-link"),
                            style="display:flex; gap:.5rem; flex-wrap:wrap; align-items:center;",
                            cls="chart-controls",
                        ),
                        style="display:flex; justify-content:flex-end; margin-bottom:.5rem;",
                    ),
                    Div(id="lang-chart", style="height:480px;"),
                    style="max-width:1000px;margin:0 auto;background:var(--surface-1);border:1px solid var(--border-color);border-radius:16px;padding:1rem;box-shadow: 0 10px 40px rgba(0,0,0,.25);backdrop-filter: blur(4px);",
                ),
            ),
            Script(f"""
                (function(){{
                  if(!window.Plotly) return;
                  const labelsBytes = {json.dumps(labels_bytes)};
                  const valuesBytes = {json.dumps(values_bytes)};
                  const labelsRepos = {json.dumps(labels_repos)};
                  const valuesRepos = {json.dumps(values_repos)};
                  const ghUser = {json.dumps(os.getenv("GITHUB_USERNAME") or "")};
                  if(!labelsBytes.length && !labelsRepos.length) return;
                  function fmtBytes(n) {{
                    const units=['B','KB','MB','GB']; let i=0, x=n; while(x>1024 && i<units.length-1){{x/=1024; i++;}} return (Math.round(x*10)/10)+' '+units[i];
                  }}
                  function colors(n) {{
                    const palette=['#60a5fa','#fbbf24','#34d399','#f472b6','#a78bfa','#fca5a5','#93c5fd','#fcd34d','#4ade80','#f9a8d4'];
                    const arr=[]; for(let i=0;i<n;i++) arr.push(palette[i%palette.length]); return arr;
                  }}
                  let metric='repos';
                  function getLabels(){{ return metric==='bytes' ? labelsBytes : labelsRepos; }}
                  function getVals(){{ return metric==='bytes' ? valuesBytes : valuesRepos; }}
                  function render(kind) {{
                    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim() || '#e2e8f0';
                    const bg = 'rgba(0,0,0,0)';
                    let data, layout;
                    const labels = getLabels();
                    const v = getVals();
                    if(kind==='bar') {{
                      data=[{{ type:'bar', orientation:'h', x:v, y:labels, marker:{{color:colors(v.length)}}, hovertemplate: metric==='bytes' ? '%{{y}}: %{{x:,}} bytes<extra></extra>' : '%{{y}}: %{{x}} repos<extra></extra>' }}];
                      const xtitle = metric==='bytes' ? 'Bytes' : 'Repositories';
                      layout={{ paper_bgcolor:bg, plot_bgcolor:bg, margin:{{t:10,b:30,l:140,r:10}}, xaxis:{{tickfont:{{color:textColor}}, gridcolor:'rgba(255,255,255,0.05)', title:xtitle, rangemode:'tozero'}}, yaxis:{{tickfont:{{color:textColor}}}}, font:{{color:textColor}}, showlegend:false, uniformtext:{{mode:'hide', minsize:10}} }};
                    }} else if (kind==='tree') {{
                      data=[{{ type:'treemap', labels:labels, parents:labels.map(_=>''), values:v, marker:{{colors:colors(v.length)}}, hovertemplate: metric==='bytes' ? '%{{label}}<br>%{{value:,}} bytes<extra></extra>' : '%{{label}}<br>%{{value}} repos<extra></extra>' }}];
                      layout={{ paper_bgcolor:bg, plot_bgcolor:bg, margin:{{t:10,b:10,l:10,r:10}}, font:{{color:textColor}} }};
                    }} else {{
                      data=[{{ type:'pie', hole:.5, labels, values:v, marker:{{colors:colors(v.length)}}, textinfo:'label+percent', textposition:'outside', automargin:true, hovertemplate: metric==='bytes' ? '%{{label}}: %{{value:,}} bytes (%{{percent}})<extra></extra>' : '%{{label}}: %{{value}} repos (%{{percent}})<extra></extra>' }}];
                      layout={{ paper_bgcolor:bg, plot_bgcolor:bg, showlegend:true, legend:{{ font:{{color:textColor}}, orientation:'h', y:-.12 }}, margin:{{t:24,b:80,l:72,r:72}}, font:{{color:textColor}}, uniformtext:{{mode:'show', minsize:11}} }};
                    }}
                    Plotly.newPlot('lang-chart', data, layout, {{displayModeBar:false, responsive:true}}).then(function(g) {{
                      g.on('plotly_click', function(ev) {{
                        if(!ev || !ev.points || !ev.points.length) return;
                        const lang = (ev.points[0].label || ev.points[0].y || '').toString();
                        if(!lang) return;
                        const url = ghUser ? `https://github.com/${{ghUser}}?tab=repositories&language=${{encodeURIComponent(lang)}}` : `https://github.com/search?q=language:${{encodeURIComponent(lang)}}&type=repositories`;
                        window.open(url, '_blank');
                      }});
                      document.getElementById('chart-export')?.addEventListener('click', async ()=>{{ try{{ const img=await Plotly.toImage(g, {{format:'png', height:700, width:1000, scale:2}}); const a=document.createElement('a'); a.href=img; a.download='tech-stack.png'; a.click(); }}catch(e){{}} }});
                    }});
                  }}
                  let current='donut';
                  function setActive(){{
                    const map = {{
                      'chart-bar': current==='bar',
                      'chart-donut': current==='donut',
                      'chart-tree': current==='tree',
                      'metric-repos': metric==='repos',
                      'metric-bytes': metric==='bytes'
                    }};
                    Object.keys(map).forEach(id=>{{
                      const el=document.getElementById(id); if(!el) return;
                      if(map[id]) el.classList.add('active'); else el.classList.remove('active');
                    }});
                  }}
                  render(current); setActive();
                  document.getElementById('chart-bar')?.addEventListener('click', ()=>{{current='bar'; render(current); setActive();}});
                  document.getElementById('chart-donut')?.addEventListener('click', ()=>{{current='donut'; render(current); setActive();}});
                  document.getElementById('chart-tree')?.addEventListener('click', ()=>{{current='tree'; render(current); setActive();}});
                  document.getElementById('metric-bytes')?.addEventListener('click', ()=>{{metric='bytes'; render(current); setActive();}});
                  document.getElementById('metric-repos')?.addEventListener('click', ()=>{{metric='repos'; render(current); setActive();}});
                }})();
            """),
            cls="section",
        )
        if labels_bytes and values_bytes
        else Div()
    )

    return render_page(
        "Matthew L. Pergolski - Data Scientist & AI/ML Engineer",
        HeroSection(profile, experience_data),
        highlights_section,
        chart_section,
    )


@app.get("/projects")
async def projects():
    """Projects page with GitHub integration"""
    try:
        projects_data, profile = await asyncio.gather(
            fetch_github_projects(), fetch_github_profile()
        )

        if not projects_data:
            projects_content = Div(
                H2("Projects", cls="section-title"),
                Div(
                    P(
                        "Unable to load projects at this time. Please check back later.",
                        cls="error",
                    ),
                    cls="container",
                ),
            )
        else:
            total = len(projects_data)
            gh_url = (profile or {}).get("html_url") or (
                f"https://github.com/{os.getenv('GITHUB_USERNAME')}"
                if os.getenv("GITHUB_USERNAME")
                else None
            )
            project_cards = [
                Div(
                    H3(project["name"].replace("_", "_\u200b"), cls="card-title"),
                    P(f"Language: {project['language']}", cls="card-subtitle"),
                    P(project["description"], cls="card-description"),
                    (
                        Div(
                            *[
                                Span(t, cls="chip")
                                for t in (project.get("topics") or [])
                            ],
                            cls="chips",
                        )
                        if project.get("topics")
                        else Div()
                    ),
                    Div(
                        A(
                            "View Project",
                            href=project["url"],
                            cls="btn",
                            target="_blank",
                        ),
                        P(
                            f"⭐ {project['stars']} • Updated {project['updated']}",
                            style="margin-top: 1rem; font-size: 0.9rem; color: var(--secondary-color);",
                        ),
                        style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;",
                    ),
                    cls="card",
                )
                for project in projects_data
            ]

            projects_content = Section(
                H2("Featured Projects", cls="section-title"),
                Div(
                    P(
                        f"Showing {total} repositories",
                        (" • " if gh_url else ""),
                        (
                            A(
                                "View GitHub Profile →",
                                href=gh_url,
                                target="_blank",
                                rel="noopener noreferrer",
                            )
                            if gh_url
                            else ""
                        ),
                        style="text-align:center;color:var(--secondary-color);margin-top:-1.5rem;",
                    ),
                    cls="container",
                ),
                Div(Div(*project_cards, cls="card-grid"), cls="container"),
                cls="section",
            )

    except Exception as e:
        projects_content = Div(
            H2("Projects", cls="section-title"),
            Div(P(f"Error loading projects: {str(e)}", cls="error"), cls="container"),
        )

    return render_page(
        "Projects - Matthew L. Pergolski",
        projects_content,
    )


@app.get("/about")
async def about():
    """About page with hero, highlights, mini timeline, and snapshot panel."""
    base = Path(__file__).resolve().parent.parent
    data = load_experience(base) or {}
    profile = await fetch_github_profile()

    # Hero
    summary = (
        data.get("summary")
        or os.getenv("SITE_DESCRIPTION")
        or "AI/ML engineer turning data into product value."
    )
    avatar = (profile or {}).get("avatar_url") or (
        f"https://github.com/{os.getenv('GITHUB_USERNAME')}.png"
        if os.getenv("GITHUB_USERNAME")
        else None
    )

    # Highlights and timeline
    highlights = data.get("highlights") or []
    exp = data.get("experience", [])[:3]

    # Snapshot
    snapshot = data.get("snapshot") or {}
    years = snapshot.get("years") or None
    pub_repos = (profile or {}).get("public_repos") or 0
    followers = (profile or {}).get("followers") or 0

    # Skills
    skills = data.get("skills") or {}
    skill_cards = [
        ft.Div(
            ft.H4(cat),
            ft.Div(*[ft.Span(s, cls="chip") for s in items], cls="chips"),
            cls="card",
        )
        for cat, items in skills.items()
    ]

    hero = ft.Div(
        *([Img(src=avatar, alt="Avatar", cls="avatar")] if avatar else []),
        ft.Div(
            ft.H3("Professional Background"),
            ft.P(summary),
            ft.Div(
                A("View Projects", href="/projects", cls="btn"),
                A("Download Resume", href="/resume/download", cls="btn btn-secondary"),
                cls="hero-cta",
            ),
        ),
        cls="about-hero",
    )

    left_col = ft.Div(
        ft.H3("Highlights"),
        ft.Ul(
            *[ft.Li(h) for h in highlights],
            style="margin-left:1.25rem; margin-bottom:1.25rem;",
        ),
        ft.H3("Recent Roles"),
        ft.Div(
            *[
                ft.Div(
                    ft.H4(display_role_title(r.get("title"))),
                    ft.P(
                        f"{r.get('company', 'Company')} • {r.get('period', '')}",
                        style="color: var(--secondary-color);",
                    ),
                    ft.Ul(
                        *[ft.Li(b) for b in (r.get("bullets") or [])[:3]],
                        style="margin-left:1.25rem; margin-bottom:.75rem;",
                    ),
                    cls="timeline-item",
                )
                for r in exp
            ],
            cls="timeline",
        ),
        cls="card",
    )

    right_col = ft.Div(
        ft.H3("Snapshot"),
        ft.Div(
            *(
                [
                    ft.Div(
                        ft.Div(str(years), cls="stat-num"),
                        ft.Div("Years", cls="stat-label"),
                        cls="stat-card",
                    )
                ]
                if years
                else []
            ),
            ft.Div(
                ft.Div(str(pub_repos), cls="stat-num"),
                ft.Div("Public Repos", cls="stat-label"),
                cls="stat-card",
            ),
            *(
                [
                    ft.Div(
                        ft.Div(str(followers), cls="stat-num"),
                        ft.Div("Followers", cls="stat-label"),
                        cls="stat-card",
                    )
                ]
                if followers > 0
                else []
            ),
            cls="stats-grid",
            style="margin-bottom:1rem;",
        ),
        ft.H3("Links"),
        ft.Div(
            A(
                "💼 LinkedIn",
                href=ensure_url(os.getenv("LINKEDIN_URL")),
                cls="icon-link",
                target="_blank",
                rel="noopener noreferrer",
            ),
            A(
                "🐙 GitHub",
                href=ensure_url(f"https://github.com/{os.getenv('GITHUB_USERNAME')}")
                if os.getenv("GITHUB_USERNAME")
                else "https://github.com/",
                cls="icon-link",
                target="_blank",
                rel="noopener noreferrer",
            ),
            A(
                "⬇️ Resume",
                href="/resume/download",
                cls="icon-link",
                target="_blank",
                rel="noopener noreferrer",
            ),
            style="display:flex; gap:.5rem; flex-wrap:wrap;",
        ),
        cls="card",
    )

    return render_page(
        "About - Matthew L. Pergolski",
        ft.Section(
            ft.H2("About Me", cls="section-title"),
            hero,
            ft.Div(left_col, right_col, cls="grid-2-1", style="margin-top:1.5rem;"),
            ft.Div(*skill_cards, cls="card-grid", style="margin-top:1.5rem;"),
            cls="container section",
        ),
    )


@app.get("/resume")
def resume():
    """Resume page"""
    data = load_experience(Path(__file__).resolve().parent.parent) or {}
    exp = data.get("experience", [])
    edu = data.get("education", [])
    skills = data.get("skills", {})

    exp_blocks = []
    if exp:
        exp_blocks.append(ft.H3("Experience"))
        for r in exp:
            bullets = r.get("bullets") or []
            exp_blocks.append(
                ft.Div(
                    ft.H4(display_role_title(r.get("title"))),
                    ft.P(
                        f"{r.get('company', 'Company')} • {r.get('period', '')}",
                        style="color: var(--secondary-color);",
                    ),
                    ft.Ul(
                        *[ft.Li(b) for b in bullets],
                        style="margin-left: 1.5rem; margin-bottom: 1.25rem;",
                    ),
                )
            )
    if edu:
        exp_blocks.append(ft.H3("Education"))
        for e in edu:
            exp_blocks.append(
                ft.Div(
                    ft.H4(e.get("degree", "Degree")),
                    ft.P(
                        f"{e.get('institution', 'University')} • {e.get('period', '')}",
                        style="color: var(--secondary-color);",
                    ),
                )
            )
    left_col = ft.Div(*exp_blocks, cls="card")

    skills_blocks = []
    if skills:
        skills_blocks.append(ft.H3("Skills"))
        for cat, items in skills.items():
            skills_blocks.append(ft.H4(cat))
            skills_blocks.append(
                ft.Div(
                    *[ft.Span(s, cls="chip") for s in items],
                    cls="chips",
                    style="margin-bottom: .75rem;",
                )
            )
    right_col = ft.Div(
        *skills_blocks,
        cls="card",
    )

    return render_page(
        "Resume - Matthew L. Pergolski",
        ft.Section(
            ft.H2("Professional Resume", cls="section-title"),
            ft.Div(
                ft.Div(
                    ft.H3("Want the PDF version?"),
                    ft.P(
                        "Download the formatted resume, or browse the expanded experience details below."
                    ),
                ),
                ft.A("Download Resume", href="/resume/download", cls="btn"),
                cls="resume-callout",
            ),
            ft.Div(left_col, right_col, cls="grid-2-1"),
            cls="container section",
        ),
    )


@app.get("/contact")
def contact(req: Request):
    """Contact page"""
    # Query-based alert messages (after POST redirect)
    qp = req.query_params
    alert = None
    if "sent" in qp:
        alert = ft.Div(
            ft.P("Thanks! Your message was sent."),
            cls="card",
            style="border-left:4px solid var(--success-color);",
        )
    elif "saved" in qp:
        alert = ft.Div(
            ft.P("Message saved locally (email not configured)."),
            cls="card",
            style="border-left:4px solid var(--accent-color);",
        )
    elif "err" in qp:
        errmap = {
            "invalid": "Please check the fields and try again.",
            "ratelimit": "Too many messages recently — please try again later.",
            "verify": "Please complete the verification challenge.",
            "server": "We couldn't send your message right now. Please email me directly.",
        }
        msg = errmap.get(qp.get("err"), "We couldn't send your message right now.")
        alert = ft.Div(
            ft.P(msg), cls="card", style="border-left:4px solid var(--error-color);"
        )

    # Generate self-hosted CAPTCHA and store with timestamp (supports multiple tabs)
    captcha_image, captcha_answer = generate_captcha()
    now = time.time()
    answers = req.session.get("captcha_answers", [])
    # Keep only recent ones (last 10 minutes or max 5)
    answers = [
        a for a in answers if a.get("answer_hash") and now - a.get("ts", 0) < 600
    ][-4:]
    answers.append({"answer_hash": captcha_answer_hash(captcha_answer), "ts": now})
    req.session["captcha_answers"] = answers

    return render_page(
        "Contact - Matthew L. Pergolski",
        ft.Section(
            ft.H2("Get In Touch", cls="section-title"),
            ft.Div(
                ft.Div(
                    alert if alert else ft.Div(),
                    ft.H3("Let's Connect"),
                    ft.P(
                        "I'm always interested in discussing new opportunities, interesting projects, or just having a chat about data science and AI."
                    ),
                    ft.H4("Contact Information"),
                    ft.P(f"📧 Email: {CFG.public_email or ''}"),
                    ft.Div(
                        ft.A(
                            "💼 LinkedIn",
                            href=ensure_url(os.getenv("LINKEDIN_URL")),
                            cls="icon-link",
                            target="_blank",
                            rel="noopener noreferrer",
                        ),
                        ft.A(
                            "🐙 GitHub",
                            href=ensure_url(
                                f"https://github.com/{os.getenv('GITHUB_USERNAME')}"
                            )
                            if os.getenv("GITHUB_USERNAME")
                            else "https://github.com/",
                            cls="icon-link",
                            target="_blank",
                            rel="noopener noreferrer",
                        ),
                        style="display:flex; gap:.75rem; flex-wrap:wrap; margin: .5rem 0 1rem;",
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
                        # Self-hosted image CAPTCHA (no external services, no env vars required)
                        ft.Div(
                            ft.Label("Verification", fr="captcha"),
                            ft.Img(
                                src=captcha_image,
                                alt="CAPTCHA",
                                style="border:1px solid var(--border-color); border-radius:4px; margin-bottom:0.5rem; display:block;",
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
        ),
    )


@app.get("/chat")
def chat_page():
    """Dedicated chat page with the same session-scoped conversation as the widget."""
    return render_page(
        "Chat - Matthew L. Pergolski",
        ft.Section(
            ft.H2("Experience Chat", cls="section-title"),
            ft.Div(
                *ChatWidget.full_page(),
                cls="container section",
            ),
        ),
        include_chat=False,
    )


@app.post("/api/rag/chat")
async def rag_chat(req: Request):
    """Answer portfolio questions with local retrieval and optional free HF generation."""
    try:
        payload = await req.json()
    except Exception:
        return JSONResponse(
            {"success": False, "error": "Invalid JSON."}, status_code=400
        )

    result = await handle_chat_payload(payload)
    status = 200 if result.get("success") else 400
    return JSONResponse(result, status_code=status)


@app.post("/contact")
async def contact_submit(req: Request):
    """Handle contact form submission: try SMTP, else save locally."""
    try:
        form = await req.form()
        name = (form.get("name") or "").strip()
        email_addr = (form.get("email") or "").strip()
        message_txt = (form.get("message") or "").strip()

        # Configurable validation/anti-spam thresholds
        dbg = os.getenv("DEBUG", "").lower() in ("1", "true", "yes", "on")
        try:
            min_msg_len = int(os.getenv("CONTACT_MIN_MSG_LEN", "10"))
        except Exception:
            min_msg_len = 10
        try:
            min_submit_secs = float(os.getenv("CONTACT_MIN_SECONDS", "2.5"))
        except Exception:
            min_submit_secs = 2.5
        # In DEBUG, relax constraints for easier local testing
        if dbg:
            min_msg_len = min(min_msg_len, 3)
            min_submit_secs = 0.0

        errs = []
        # Honeypot / timing
        if (form.get("company") or "").strip():
            # Silently accept to mislead bots
            return RedirectResponse("/contact", status_code=303)
        t0 = 0
        try:
            t0 = int(form.get("t0") or 0)
        except Exception:
            t0 = 0
        if t0 and min_submit_secs > 0:
            if time.time() - t0 < min_submit_secs:
                errs.append("Submission was too fast; please try again.")
        if len(name) < 2:
            errs.append("Please enter your name.")
        if "@" not in email_addr:
            errs.append("Please enter a valid email address.")
        if len(message_txt) < min_msg_len:
            errs.append("Please write a slightly longer message.")

        # Self-hosted CAPTCHA validation supporting multiple recent codes (better multi-tab UX)
        submitted = (form.get("captcha") or "").strip().upper()
        submitted_hash = captcha_answer_hash(submitted)
        now = time.time()
        answers = req.session.get("captcha_answers", [])
        # Clean old entries and look for a match
        valid_answers = []
        matched = False
        for item in answers:
            if now - item.get("ts", 0) > 600:
                continue  # too old
            answer_hash = item.get("answer_hash")
            if not answer_hash:
                continue
            if not matched and answer_hash == submitted_hash:
                matched = True  # consume this one
                continue
            valid_answers.append(item)
        req.session["captcha_answers"] = valid_answers

        if not matched:
            errs.append("Please enter the correct verification code.")

        # Consolidated rate limiting (per-IP + global)
        ip = get_client_ip(req)
        if not errs and is_rate_limited(ip):
            errs.append("Too many messages recently — please try again later.")

        if not errs:
            subject = f"Portfolio Contact from {name}"
            body = f"From: {name} <{email_addr}>\n\n{message_txt}"
            ok, info = await send_email(subject, body, reply_to=email_addr)
            if ok:
                return RedirectResponse("/contact?sent=1", status_code=303)
            else:
                if os.getenv("VERCEL"):
                    print(
                        f"Email send failed; local fallback disabled on Vercel: {info}"
                    )
                    return RedirectResponse("/contact?err=server", status_code=303)
                # Fallback: persist to data/messages
                msg_dir = BASE_DATA_DIR / "messages"
                try:
                    msg_dir.mkdir(parents=True, exist_ok=True)
                    (msg_dir / f"{int(time.time())}.json").write_text(
                        json.dumps(
                            {"name": name, "email": email_addr, "message": message_txt}
                        )
                    )
                    return RedirectResponse("/contact?saved=1", status_code=303)
                except Exception:
                    return RedirectResponse("/contact?err=server", status_code=303)
        else:
            # Prefer simple redirect with error code to avoid re-post on refresh
            code = "invalid"
            if any("verification" in e.lower() for e in errs):
                code = "verify"
            if any("many" in e.lower() for e in errs):
                code = "ratelimit"
            return RedirectResponse(f"/contact?err={code}", status_code=303)

    except Exception:
        return RedirectResponse("/contact", status_code=303)


@app.get("/resume/download")
def resume_download():
    """Redirect to the configured resume URL or local static fallback."""
    url = os.getenv("RESUME_URL") or "/static/resume.pdf"
    return RedirectResponse(url, status_code=307)


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

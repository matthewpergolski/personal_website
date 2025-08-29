#!/usr/bin/env python3
"""
FastHTML Portfolio Website - Main Application
A professional portfolio website built exclusively with FastHTML
to showcase GitHub projects and serve as a resume for technical roles.
"""

from fasthtml import FastHTML
from fasthtml.common import *
import fasthtml.common as ft
from dotenv import load_dotenv
import os
import json
import asyncio
from pathlib import Path
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.requests import Request
import time, json
from src.services.github import fetch_github_profile, fetch_github_projects
from src.components.ui import Navigation, HeroSection, SiteFooter, ensure_url
from src.utils.render import render_page
from src.services.github import fetch_language_bytes_aggregate
from src.services.content import load_experience
from src.services.email import send_email
import httpx

async def verify_human(req: Request) -> tuple[bool, str]:
    """Verify Cloudflare Turnstile or hCaptcha token if configured.
    Returns (ok, reason). If not configured, returns (True, 'disabled').
    """
    form = await req.form()
    # Prefer Turnstile if present
    ts_secret = os.getenv('TURNSTILE_SECRET_KEY')
    ts_site = os.getenv('TURNSTILE_SITE_KEY')
    if ts_secret and ts_site:
        token = form.get('cf-turnstile-response') or ''
        if not token:
            return False, 'missing turnstile token'
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
                    data={'secret': ts_secret, 'response': token, 'remoteip': getattr(req.client, 'host', '')}
                )
                j = r.json()
                return (j.get('success') is True, 'turnstile')
        except Exception as e:
            return False, str(e)
    # hCaptcha fallback
    hc_secret = os.getenv('HCAPTCHA_SECRET')
    hc_site = os.getenv('HCAPTCHA_SITE_KEY')
    if hc_secret and hc_site:
        token = form.get('h-captcha-response') or ''
        if not token:
            return False, 'missing hcaptcha token'
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post('https://hcaptcha.com/siteverify', data={'secret': hc_secret, 'response': token})
                j = r.json()
                return (bool(j.get('success')), 'hcaptcha')
        except Exception as e:
            return False, str(e)
    return True, 'disabled'

# Load environment variables
load_dotenv('envs.sh')

# FastHTML App Configuration
app = FastHTML(
    # On Vercel's serverless runtime, the filesystem is read-only except for /tmp.
    # Ensure FastHTML does not try to write the default .sesskey in CWD.
    key_fname=("/tmp/.sesskey" if os.getenv("VERCEL") else ".sesskey"),
    title=os.getenv('SITE_TITLE', 'Professional Portfolio'),
    hdrs=(
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
        # Theme Styles
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
                background: radial-gradient(1200px 600px at 10% -10%, rgba(255,255,255,0.15), transparent),
                            linear-gradient(135deg, var(--primary-color) 0%, #1d4ed8 100%);
                color: white;
                padding: 4rem 0;
                text-align: center;
                position: relative;
                overflow: hidden;
            }

            .hero-title {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }

            @media (max-width: 768px) {
                .hero-title {
                    font-size: 2rem;
                }
            }

            .hero-subtitle {
                font-size: 1.25rem;
                opacity: 0.9;
                margin-bottom: 2rem;
            }

            .hero-description {
                font-size: 1.1rem;
                opacity: 0.8;
                max-width: 600px;
                margin: 0 auto;
            }

            .avatar {
                width: 112px;
                height: 112px;
                border-radius: 50%;
                box-shadow: 0 10px 30px rgba(0,0,0,0.25);
                border: 3px solid rgba(255,255,255,0.7);
                margin-bottom: 1rem;
            }
            .avatar-lg { width: 144px; height: 144px; }
            @media (max-width: 640px){ .avatar-lg { width: 96px; height: 96px; } }

            .nav {
                background: var(--surface-1);
                padding: 1rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                position: sticky;
                top: 0;
                z-index: 100;
            }

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
                .nav-toggle { display: inline-flex; align-items:center; justify-content:center; padding:.5rem .75rem; border:1px solid var(--border-color); border-radius:8px; background:var(--surface-1); color:var(--text-color); }
                .nav-links { display: none; }
                .nav.open .nav-links { display: flex; flex-direction: column; gap: 1rem; padding-top: .5rem; }
                .nav-actions { display: none; }
            }

            .nav-actions {
                display: flex;
                gap: .75rem;
                align-items: center;
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

            .section-title {
                font-size: 2.5rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 3rem;
                color: var(--text-color);
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
            @media (max-width: 640px){ .hero-cta { justify-content:center; } }

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
        """)
        ,
        # Plotly for interactive charts
        Script(src="https://cdn.plot.ly/plotly-2.35.2.min.js")
        ,
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
        """)
        ,
        # Mouse-follow glow effect
        Script(r"""
          (function(){
            document.addEventListener('mousemove', function(e){
              try{
                document.documentElement.style.setProperty('--glow-x', e.clientX+'px');
                document.documentElement.style.setProperty('--glow-y', e.clientY+'px');
              }catch(_){}
            });
            // Mobile nav toggle
            document.addEventListener('click', function(e){
              var t = e.target;
              if (t && t.id === 'nav-toggle') {
                var nav = document.querySelector('.nav');
                if (nav) nav.classList.toggle('open');
              }
            });
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
        """)
)
)

# Mount static files at /static using project-relative data/static
ROOT_DIR = Path(__file__).resolve().parent.parent
# On Vercel (serverless), writes must go to /tmp. Use that for ephemeral data.
BASE_DATA_DIR = Path("/tmp") if os.getenv("VERCEL") else (ROOT_DIR / "data")
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
        fetch_github_profile(), fetch_language_bytes_aggregate(), fetch_github_projects()
    )
    # Build top languages from aggregated byte counts
    items = sorted((lang_bytes or {}).items(), key=lambda x: x[1], reverse=True)
    top = items[:8]
    if len(items) > 8:
        others_total = sum(v for _, v in items[8:])
        top.append(("Others", others_total))
    labels = [k for k, _ in top]
    values = [v for _, v in top]
    # Repo counts by primary language (for metric toggle)
    lang_counts = {}
    for r in (repos or []):
        lang = r.get('language') or 'Other'
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    values_cnt = [lang_counts.get(k, 0) for k in labels]

    # Load highlights content
    highlights = []
    try:
        from pathlib import Path
        data = load_experience(Path(__file__).resolve().parent.parent)
        if data and isinstance(data.get('highlights'), list):
            highlights = [str(x) for x in data['highlights']][:6]
    except Exception:
        pass

    highlights_section = (
        Section(
            H2("Highlights", cls="section-title"),
            Div(
                Div(
                    *[P(f"• {h}") for h in highlights],
                    cls="card"
                ),
                cls="container"
            ),
            cls="section"
        ) if highlights else Div()
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
                            cls="chart-controls"
                        ),
                        style="display:flex; justify-content:flex-end; margin-bottom:.5rem;"
                    ),
                    Div(id="lang-chart", style="height:480px;"),
                    style="max-width:1000px;margin:0 auto;background:var(--surface-1);border:1px solid var(--border-color);border-radius:16px;padding:1rem;box-shadow: 0 10px 40px rgba(0,0,0,.25);backdrop-filter: blur(4px);"
                ),
            ),
            Script(f"""
                (function(){{
                  if(!window.Plotly) return;
                  const labels = {json.dumps(labels)};
                  const valuesBytes = {json.dumps(values)};
                  const valuesCnt = {json.dumps(values_cnt)};
                  const ghUser = {json.dumps(os.getenv('GITHUB_USERNAME') or '')};
                  if(!labels.length) return;
                  function fmtBytes(n) {{
                    const units=['B','KB','MB','GB']; let i=0, x=n; while(x>1024 && i<units.length-1){{x/=1024; i++;}} return (Math.round(x*10)/10)+' '+units[i];
                  }}
                  function colors(n) {{
                    const palette=['#60a5fa','#fbbf24','#34d399','#f472b6','#a78bfa','#fca5a5','#93c5fd','#fcd34d','#4ade80','#f9a8d4'];
                    const arr=[]; for(let i=0;i<n;i++) arr.push(palette[i%palette.length]); return arr;
                  }}
                  let metric='repos';
                  function getVals(){{ return metric==='bytes' ? valuesBytes : valuesCnt; }}
                  function render(kind) {{
                    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim() || '#e2e8f0';
                    const bg = 'rgba(0,0,0,0)';
                    let data, layout;
                    const v = getVals();
                    if(kind==='bar') {{
                      data=[{{ type:'bar', orientation:'h', x:v, y:labels, marker:{{color:colors(v.length)}}, hovertemplate: metric==='bytes' ? '%{{y}}: %{{x:,}} bytes<extra></extra>' : '%{{y}}: %{{x}} repos<extra></extra>' }}];
                      const xtitle = metric==='bytes' ? 'Bytes' : 'Repositories';
                      layout={{ paper_bgcolor:bg, plot_bgcolor:bg, margin:{{t:10,b:30,l:140,r:10}}, xaxis:{{tickfont:{{color:textColor}}, gridcolor:'rgba(255,255,255,0.05)', title:xtitle, rangemode:'tozero'}}, yaxis:{{tickfont:{{color:textColor}}}}, font:{{color:textColor}}, showlegend:false, uniformtext:{{mode:'hide', minsize:10}} }};
                    }} else if (kind==='tree') {{
                      data=[{{ type:'treemap', labels:labels, parents:labels.map(_=>''), values:v, marker:{{colors:colors(v.length)}}, hovertemplate: metric==='bytes' ? '%{{label}}<br>%{{value:,}} bytes<extra></extra>' : '%{{label}}<br>%{{value}} repos<extra></extra>' }}];
                      layout={{ paper_bgcolor:bg, plot_bgcolor:bg, margin:{{t:10,b:10,l:10,r:10}}, font:{{color:textColor}} }};
                    }} else {{
                      data=[{{ type:'pie', hole:.5, labels, values:v, marker:{{colors:colors(v.length)}}, textinfo:'label+percent', textposition:'inside', hovertemplate: metric==='bytes' ? '%{{label}}: %{{value:,}} bytes (%{{percent}})<extra></extra>' : '%{{label}}: %{{value}} repos (%{{percent}})<extra></extra>' }}];
                      layout={{ paper_bgcolor:bg, plot_bgcolor:bg, showlegend:true, legend:{{ font:{{color:textColor}} }}, margin:{{t:10,b:10,l:10,r:10}}, font:{{color:textColor}}, uniformtext:{{mode:'hide', minsize:12}} }};
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
            cls="section"
        ) if labels and values else Div()
    )

    return render_page(
        "Matthew L. Pergolski - Data Scientist & AI/ML Engineer",
        HeroSection(profile),
        highlights_section,
        chart_section,
    )

@app.get("/projects")
async def projects():
    """Projects page with GitHub integration"""
    try:
        projects_data, profile = await asyncio.gather(fetch_github_projects(), fetch_github_profile())

        if not projects_data:
            projects_content = Div(
                H2("Projects", cls="section-title"),
                Div(
                    P("Unable to load projects at this time. Please check back later.", cls="error"),
                    cls="container"
                )
            )
        else:
            total = len(projects_data)
            gh_url = (profile or {}).get('html_url') or (f"https://github.com/{os.getenv('GITHUB_USERNAME')}" if os.getenv('GITHUB_USERNAME') else None)
            project_cards = [
                Div(
                    H3(project['name'].replace('_', '_\u200b'), cls="card-title"),
                    P(f"Language: {project['language']}", cls="card-subtitle"),
                    P(project['description'], cls="card-description"),
                    (Div(*[Span(t, cls="chip") for t in (project.get('topics') or [])], cls="chips") if project.get('topics') else Div()),
                    Div(
                        A("View Project", href=project['url'], cls="btn", target="_blank"),
                        P(f"⭐ {project['stars']} • Updated {project['updated']}", style="margin-top: 1rem; font-size: 0.9rem; color: var(--secondary-color);"),
                        style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;"
                    ),
                    cls="card"
                )
                for project in projects_data
            ]

            projects_content = Section(
                H2("Featured Projects", cls="section-title"),
                Div(
                    P(
                        f"Showing {total} repositories",
                        (" • " if gh_url else ""),
                        (A("View GitHub Profile →", href=gh_url, target="_blank", rel="noopener noreferrer") if gh_url else ""),
                        style="text-align:center;color:var(--secondary-color);margin-top:-1.5rem;"
                    ),
                    cls="container"
                ),
                Div(
                    Div(*project_cards, cls="card-grid"),
                    cls="container"
                ),
                cls="section"
            )

    except Exception as e:
        projects_content = Div(
            H2("Projects", cls="section-title"),
            Div(
                P(f"Error loading projects: {str(e)}", cls="error"),
                cls="container"
            )
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
    summary = data.get('summary') or os.getenv('SITE_DESCRIPTION') or "AI/ML engineer turning data into product value."
    avatar = (profile or {}).get('avatar_url') or (f"https://github.com/{os.getenv('GITHUB_USERNAME')}.png" if os.getenv('GITHUB_USERNAME') else None)

    # Highlights and timeline
    highlights = data.get('highlights') or []
    exp = data.get('experience', [])[:3]

    # Snapshot
    snapshot = data.get('snapshot') or {}
    years = snapshot.get('years') or None
    pub_repos = (profile or {}).get('public_repos') or 0
    followers = (profile or {}).get('followers') or 0

    # Skills
    skills = data.get('skills') or {}
    skill_cards = [
        ft.Div(
            ft.H4(cat),
            ft.Div(*[ft.Span(s, cls="chip") for s in items], cls="chips"),
            cls="card"
        ) for cat, items in skills.items()
    ]

    hero = ft.Div(
        *( [Img(src=avatar, alt="Avatar", cls="avatar")] if avatar else [] ),
        ft.Div(
            ft.H3("Professional Background"),
            ft.P(summary),
            ft.Div(
                A("View Projects", href="/projects", cls="btn"),
                A("Download Resume", href="/resume/download", cls="btn btn-secondary"),
                cls="hero-cta"
            ),
        ),
        cls="about-hero"
    )

    left_col = ft.Div(
        ft.H3("Highlights"),
        ft.Ul(*[ft.Li(h) for h in highlights], style="margin-left:1.25rem; margin-bottom:1.25rem;"),
        ft.H3("Recent Roles"),
        ft.Div(
            *[
                ft.Div(
                    ft.H4(r.get('title','Role')),
                    ft.P(f"{r.get('company','Company')} • {r.get('period','')}", style="color: var(--secondary-color);"),
                    ft.Ul(*[ft.Li(b) for b in (r.get('bullets') or [])[:3]], style="margin-left:1.25rem; margin-bottom:.75rem;")
                    ,cls="timeline-item"
                ) for r in exp
            ],
            cls="timeline"
        ),
        cls="card"
    )

    right_col = ft.Div(
        ft.H3("Snapshot"),
        ft.Div(
            *( [ft.Div(ft.Div(str(years), cls="stat-num"), ft.Div("Years", cls="stat-label"), cls="stat-card")] if years else [] ),
            ft.Div(ft.Div(str(pub_repos), cls="stat-num"), ft.Div("Public Repos", cls="stat-label"), cls="stat-card"),
            *( [ft.Div(ft.Div(str(followers), cls="stat-num"), ft.Div("Followers", cls="stat-label"), cls="stat-card")] if followers > 0 else [] ),
            cls="stats-grid",
            style="margin-bottom:1rem;"
        ),
        ft.H3("Links"),
        ft.Div(
            A("💼 LinkedIn", href=ensure_url(os.getenv('LINKEDIN_URL')), cls="icon-link", target="_blank", rel="noopener noreferrer"),
            A("🐙 GitHub", href=ensure_url(f"https://github.com/{os.getenv('GITHUB_USERNAME')}") if os.getenv('GITHUB_USERNAME') else "https://github.com/", cls="icon-link", target="_blank", rel="noopener noreferrer"),
            A("⬇️ Resume", href="/resume/download", cls="icon-link", target="_blank", rel="noopener noreferrer"),
            style="display:flex; gap:.5rem; flex-wrap:wrap;"
        ),
        cls="card"
    )

    return render_page(
        "About - Matthew L. Pergolski",
        ft.Section(
            ft.H2("About Me", cls="section-title"),
            hero,
            ft.Div(
                left_col,
                right_col,
                cls="grid-2-1",
                style="margin-top:1.5rem;"
            ),
            ft.Div(
                *skill_cards,
                cls="card-grid",
                style="margin-top:1.5rem;"
            ),
            cls="container section"
        ),
    )

@app.get("/resume")
def resume():
    """Resume page"""
    data = load_experience(Path(__file__).resolve().parent.parent) or {}
    exp = data.get('experience', [])
    edu = data.get('education', [])
    skills = data.get('skills', {})

    exp_blocks = []
    if exp:
        exp_blocks.append(ft.H3("Experience"))
        for r in exp:
            bullets = r.get('bullets') or []
            exp_blocks.append(
                ft.Div(
                    ft.H4(r.get('title', 'Role')),
                    ft.P(f"{r.get('company','Company')} • {r.get('period','')}", style="color: var(--secondary-color);"),
                    ft.Ul(*[ft.Li(b) for b in bullets], style="margin-left: 1.5rem; margin-bottom: 1.25rem;"),
                )
            )
    if edu:
        exp_blocks.append(ft.H3("Education"))
        for e in edu:
            exp_blocks.append(
                ft.Div(
                    ft.H4(e.get('degree','Degree')),
                    ft.P(f"{e.get('institution','University')} • {e.get('period','')}", style="color: var(--secondary-color);"),
                )
            )
    left_col = ft.Div(*exp_blocks, cls="card")

    skills_blocks = []
    if skills:
        skills_blocks.append(ft.H3("Skills"))
        for cat, items in skills.items():
            skills_blocks.append(ft.H4(cat))
            skills_blocks.append(ft.Div(*[ft.Span(s, cls="chip") for s in items], cls="chips", style="margin-bottom: .75rem;"))
    right_col = ft.Div(
        ft.H3("Download Resume"),
        ft.P("Get a complete PDF version of my professional resume."),
        ft.A("Download PDF", href="/resume/download", cls="btn"),
        *skills_blocks,
        cls="card"
    )

    return render_page(
        "Resume - Matthew L. Pergolski",
        ft.Section(
            ft.H2("Professional Resume", cls="section-title"),
            ft.Div(
                left_col,
                right_col,
                cls="grid-2-1"
            ),
            cls="container section"
        ),
    )

@app.get("/contact")
def contact(req: Request):
    """Contact page"""
    # Query-based alert messages (after POST redirect)
    qp = req.query_params
    alert = None
    if 'sent' in qp:
        alert = ft.Div(ft.P("Thanks! Your message was sent."), cls="card", style="border-left:4px solid var(--success-color);")
    elif 'saved' in qp:
        alert = ft.Div(ft.P("Message saved locally (email not configured)."), cls="card", style="border-left:4px solid var(--accent-color);")
    elif 'err' in qp:
        errmap = {
            'invalid': "Please check the fields and try again.",
            'ratelimit': "Too many messages recently — please try again later.",
            'verify': "Please complete the verification challenge.",
            'server': "We couldn't send your message right now. Please email me directly.",
        }
        msg = errmap.get(qp.get('err'), "We couldn't send your message right now.")
        alert = ft.Div(ft.P(msg), cls="card", style="border-left:4px solid var(--error-color);")

    return render_page(
        "Contact - Matthew L. Pergolski",
        ft.Section(
            ft.H2("Get In Touch", cls="section-title"),
            ft.Div(
                ft.Div(
                    alert if alert else ft.Div(),
                    ft.H3("Let's Connect"),
                    ft.P("I'm always interested in discussing new opportunities, interesting projects, or just having a chat about data science and AI."),
                    ft.H4("Contact Information"),
                    ft.P("📧 Email: matthew@example.com"),
                    ft.Div(
                        ft.A("💼 LinkedIn", href=ensure_url(os.getenv('LINKEDIN_URL')), cls="icon-link", target="_blank", rel="noopener noreferrer"),
                        ft.A("🐙 GitHub", href=ensure_url(f"https://github.com/{os.getenv('GITHUB_USERNAME')}") if os.getenv('GITHUB_USERNAME') else "https://github.com/", cls="icon-link", target="_blank", rel="noopener noreferrer"),
                        style="display:flex; gap:.75rem; flex-wrap:wrap; margin: .5rem 0 1rem;"
                    ),
                    ft.H4("Response Time"),
                    ft.P("I typically respond to emails within 24 hours."),
                    cls="card"
                ),
                ft.Div(
                    ft.H3("Send a Message"),
                    ft.Form(
                        ft.Div(
                            ft.Label("Name", fr="name"),
                            ft.Input(type="text", id="name", name="name", required=True, cls="form-input"),
                            cls="form-group"
                        ),
                        ft.Div(
                            ft.Label("Email", fr="email"),
                            ft.Input(type="email", id="email", name="email", required=True, cls="form-input"),
                            cls="form-group"
                        ),
                        ft.Div(
                            ft.Label("Company", fr="company"),
                            ft.Input(type="text", id="company", name="company", cls="form-input"),
                            cls="hp-wrap"
                        ),
                        ft.Div(
                            ft.Label("Message", fr="message"),
                            ft.Textarea(id="message", name="message", required=True, rows=5, cls="form-input"),
                            cls="form-group"
                        ),
                        ft.Input(type="hidden", name="t0", value=str(int(time.time()))),
                        # Bot protection widgets
                        *( [
                            ft.Div(cls="cf-turnstile", **{"data-sitekey": os.getenv('TURNSTILE_SITE_KEY')}),
                            ft.Script(src="https://challenges.cloudflare.com/turnstile/v0/api.js", defer=True)
                           ] if os.getenv('TURNSTILE_SITE_KEY') else [] ),
                        *( [
                            ft.Div(cls="h-captcha", **{"data-sitekey": os.getenv('HCAPTCHA_SITE_KEY')}),
                            ft.Script(src="https://js.hcaptcha.com/1/api.js", async_=True, defer=True)
                           ] if os.getenv('HCAPTCHA_SITE_KEY') else [] ),
                        ft.Button("Send Message", type="submit", cls="btn"),
                        method="post",
                        action="/contact",
                        cls="contact-form"
                    ),
                    cls="card"
                ),
                cls="card-grid"
            ),
            cls="container section"
        ),
    )

@app.post("/contact")
async def contact_submit(req: Request):
    """Handle contact form submission: try SMTP, else save locally."""
    try:
        form = await req.form()
        name = (form.get('name') or '').strip()
        email_addr = (form.get('email') or '').strip()
        message_txt = (form.get('message') or '').strip()

        # Configurable validation/anti-spam thresholds
        dbg = (os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes', 'on'))
        try:
            min_msg_len = int(os.getenv('CONTACT_MIN_MSG_LEN', '10'))
        except Exception:
            min_msg_len = 10
        try:
            min_submit_secs = float(os.getenv('CONTACT_MIN_SECONDS', '2.5'))
        except Exception:
            min_submit_secs = 2.5
        # In DEBUG, relax constraints for easier local testing
        if dbg:
            min_msg_len = min(min_msg_len, 3)
            min_submit_secs = 0.0

        errs = []
        # Honeypot / timing
        if (form.get('company') or '').strip():
            # Silently accept to mislead bots
            return RedirectResponse('/contact', status_code=303)
        t0 = 0
        try:
            t0 = int(form.get('t0') or 0)
        except Exception:
            t0 = 0
        if t0 and min_submit_secs > 0:
            if time.time() - t0 < min_submit_secs:
                errs.append("Submission was too fast; please try again.")
        if len(name) < 2:
            errs.append("Please enter your name.")
        if '@' not in email_addr:
            errs.append("Please enter a valid email address.")
        if len(message_txt) < min_msg_len:
            errs.append("Please write a slightly longer message.")

        alert = None
        # Verify CAPTCHA if configured
        ok_human, reason = await verify_human(req)
        if not ok_human:
            errs.append("Please complete the verification challenge.")

        # Basic file-backed rate limit (per IP per hour, and global per day)
        def rate_limited(ip: str) -> bool:
            try:
                limit_ip = int(os.getenv('RATE_IP_PER_HOUR', '3'))
                limit_global = int(os.getenv('RATE_GLOBAL_PER_DAY', '50'))
            except Exception:
                limit_ip, limit_global = 3, 50
            now = int(time.time())
            rl_dir = BASE_DATA_DIR / 'ratelimit'
            try: rl_dir.mkdir(parents=True, exist_ok=True)
            except Exception: pass
            ipf = rl_dir / f"{ip}.json"
            try:
                lst = json.loads(ipf.read_text())
            except Exception:
                lst = []
            lst = [t for t in lst if now - int(t) < 3600]
            if len(lst) >= limit_ip:
                try: ipf.write_text(json.dumps(lst))
                except Exception: pass
                return True
            lst.append(now)
            try: ipf.write_text(json.dumps(lst))
            except Exception: pass
            gf = rl_dir / 'global.json'
            try:
                gl = json.loads(gf.read_text())
            except Exception:
                gl = []
            gl = [t for t in gl if now - int(t) < 86400]
            if len(gl) >= limit_global:
                try: gf.write_text(json.dumps(gl))
                except Exception: pass
                return True
            gl.append(now)
            try: gf.write_text(json.dumps(gl))
            except Exception: pass
            return False

        ip = getattr(req.client, 'host', 'unknown')
        if not errs and rate_limited(ip):
            errs.append("Too many messages recently — please try again later.")

        if not errs:
            subject = f"Portfolio Contact from {name}"
            body = f"From: {name} <{email_addr}>\n\n{message_txt}"
            ok, info = await send_email(subject, body, reply_to=email_addr)
            if ok:
                return RedirectResponse('/contact?sent=1', status_code=303)
            else:
                # Fallback: persist to data/messages
                msg_dir = BASE_DATA_DIR / 'messages'
                try:
                    msg_dir.mkdir(parents=True, exist_ok=True)
                    (msg_dir / f"{int(time.time())}.json").write_text(json.dumps({"name":name, "email":email_addr, "message":message_txt}))
                    return RedirectResponse('/contact?saved=1', status_code=303)
                except Exception:
                    return RedirectResponse('/contact?err=server', status_code=303)
        else:
            # Prefer simple redirect with error code to avoid re-post on refresh
            code = 'invalid'
            if any('verification' in e.lower() for e in errs):
                code = 'verify'
            if any('many' in e.lower() for e in errs):
                code = 'ratelimit'
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

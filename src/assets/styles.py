GLOBAL_STYLES = r"""
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
                .hero-aside { gap: .75rem; }
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

            .muted { color: var(--muted-text); }
            .inline-actions { display:flex; gap:.5rem; flex-wrap:wrap; }
            .stack-gap { margin-top: 1.5rem; }
            .section-kicker { text-align:center; color:var(--secondary-color); margin-top:-1.5rem; }
            .bullet-list { margin-left: 1.25rem; }
            .bullet-list-tight { margin-bottom: .75rem; }
            .bullet-list-loose { margin-bottom: 1.25rem; }

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
            .about-hero .avatar { justify-self: center; margin: 0 auto 1rem; object-fit: cover; object-position: center; }

            .hero-cta { display:flex; gap:.75rem; flex-wrap:wrap; }
            @media (max-width: 640px){
                .hero-cta { justify-content:center; }
                .hero-cta .btn { width: 100%; max-width: 320px; }
            }

            /* Stats */
            .stats-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: .75rem; }
            .stats-grid-spaced { margin-bottom:1rem; }
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
            .chips-spaced { margin-bottom: .75rem; }
            .chip { padding: .25rem .6rem; border-radius: 999px; font-size: .8rem; background: var(--chip-bg); color: var(--chip-fg); border: 1px solid var(--chip-border); }

            .project-card-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 1rem;
            }
            .project-card-meta { margin-top: 1rem; font-size: 0.9rem; }

            .chart-shell {
                max-width:1000px;
                margin:0 auto;
                background:var(--surface-1);
                border:1px solid var(--border-color);
                border-radius:16px;
                padding:1rem;
                box-shadow: 0 10px 40px rgba(0,0,0,.25);
                backdrop-filter: blur(4px);
            }
            .chart-toolbar { display:flex; justify-content:flex-end; margin-bottom:.5rem; }
            .chart-controls { display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; }
            .chart-canvas { height:480px; }

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
            .alert-success { border-left:4px solid var(--success-color); }
            .alert-info { border-left:4px solid var(--accent-color); }
            .alert-error { border-left:4px solid var(--error-color); }

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
            .contact-links { margin: .5rem 0 1rem; }
            .captcha-img { border:1px solid var(--border-color); border-radius:4px; margin-bottom:0.5rem; display:block; }
            .hp-wrap { position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden; }
"""

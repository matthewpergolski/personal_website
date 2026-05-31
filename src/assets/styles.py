GLOBAL_STYLES = r"""
            :root {
                --primary-color: #2563eb;
                --secondary-color: #64748b;
                --accent-color: #f59e0b;
                --primary-strong: #1d4ed8;
                --dark-color: #1e293b;
                --light-color: #f8fafc;
                --text-color: #334155;
                --border-color: #e2e8f0;
                --surface-1: #ffffff;
                --surface-2: #f8fafc;
                --surface-3: #eef2f7;
                --muted-text: #64748b;
                --chip-bg: #eff6ff;
                --chip-border: #dbeafe;
                --chip-fg: #1e40af;
                --success-color: #10b981;
                --error-color: #ef4444;
                --radius-sm: 8px;
                --radius-md: 12px;
                --radius-lg: 16px;
                --shadow-sm: 0 1px 2px rgba(15,23,42,.08);
                --shadow-md: 0 12px 32px rgba(15,23,42,.14);
                --shadow-lg: 0 24px 70px rgba(15,23,42,.20);
                --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            /* Dark theme overrides */
            html[data-theme='dark'] {
                --primary-color: #60a5fa;
                --primary-strong: #3b82f6;
                --secondary-color: #94a3b8;
                --accent-color: #fbbf24;
                --dark-color: #0b1220;       /* base canvas color */
                --light-color: #0b1220;      /* page background */
                --text-color: #e2e8f0;       /* primary text */
                --muted-text: #94a3b8;       /* secondary text */
                --border-color: #1f2937;     /* outlines */
                --surface-1: #0f172a;        /* cards, nav, panels */
                --surface-2: #111827;        /* subtle elevated */
                --surface-3: #172033;
                --chip-bg: #111827;
                --chip-border: #334155;
                --chip-fg: #93c5fd;
                --shadow-sm: 0 1px 2px rgba(0,0,0,.22);
                --shadow-md: 0 18px 42px rgba(0,0,0,.28);
                --shadow-lg: 0 30px 80px rgba(0,0,0,.36);
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            html {
                overflow-x: hidden;
            }

            body {
                font-family: var(--font-family);
                line-height: 1.6;
                color: var(--text-color);
                background:
                    radial-gradient(900px 520px at 8% -10%, color-mix(in srgb, var(--primary-color) 12%, transparent), transparent 65%),
                    radial-gradient(700px 420px at 100% 0%, color-mix(in srgb, var(--accent-color) 8%, transparent), transparent 60%),
                    var(--light-color);
                position: relative;
                -webkit-font-smoothing: antialiased;
                text-rendering: optimizeLegibility;
                overflow-x: hidden;
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
                max-width: 1180px;
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
                    linear-gradient(180deg, color-mix(in srgb, var(--surface-2) 72%, transparent), transparent 72%),
                    radial-gradient(900px 420px at 18% 10%, color-mix(in srgb, var(--primary-color) 24%, transparent), transparent 65%),
                    radial-gradient(740px 360px at 88% 16%, color-mix(in srgb, var(--accent-color) 12%, transparent), transparent 60%);
                color: var(--text-color);
                padding: 5rem 0 4.25rem;
                text-align: left;
                position: relative;
                overflow: hidden;
                border-bottom: 1px solid var(--border-color);
            }

            .hero-layout {
                display: grid;
                grid-template-columns: minmax(0, 1.25fr) minmax(300px, .75fr);
                gap: clamp(2rem, 5vw, 4.5rem);
                align-items: center;
            }

            .hero-copy { max-width: 780px; }

            .hero-kicker {
                color: var(--primary-color);
                font-weight: 700;
                margin-bottom: .75rem;
                text-transform: uppercase;
                font-size: .85rem;
                letter-spacing: 0;
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
                gap: 1.1rem;
            }

            .hero-current {
                width: min(100%, 360px);
                border: 1px solid var(--border-color);
                border-radius: var(--radius-lg);
                padding: 1.1rem;
                background: color-mix(in srgb, var(--surface-1) 82%, transparent);
                box-shadow: var(--shadow-md);
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
                font-size: clamp(2.85rem, 7vw, 5rem);
                font-weight: 800;
                line-height: 1.05;
                margin-bottom: .85rem;
            }

            .hero-subtitle {
                color: var(--primary-color);
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 1rem;
            }

            .hero-description {
                color: var(--text-color);
                font-size: 1.08rem;
                max-width: 760px;
                line-height: 1.65;
            }

            @media (max-width: 800px) {
                .hero-section { padding: 3rem 0 2.25rem; }
                .hero-layout { grid-template-columns: 1fr; text-align: center; }
                .hero-actions { justify-content: center; }
                .hero-title { font-size: clamp(2.35rem, 12vw, 3.25rem); }
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
                box-shadow: 0 0 0 2px rgba(37,99,235,.28), var(--shadow-md);
                border: 3px solid rgba(255,255,255,0.75);
                margin-bottom: 1rem;
                transition: box-shadow .2s ease, transform .2s ease;
            }
            .avatar:hover { box-shadow: 0 0 0 3px rgba(37,99,235,.45), var(--shadow-lg); transform: translateY(-1px) scale(1.01); }
            .avatar:active { transform: scale(.995); }
            .avatar-lg { width: 176px; height: 176px; }
            @media (max-width: 640px){ .avatar-lg { width: 124px; height: 124px; } }

            .nav {
                background: color-mix(in srgb, var(--surface-1) 88%, transparent);
                padding: .8rem 0;
                box-shadow: var(--shadow-sm);
                position: sticky;
                top: 0;
                z-index: 1000; /* keep above hero visuals */
                border-bottom: 1px solid var(--border-color);
                backdrop-filter: blur(14px);
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

            .nav-brand { display: inline-flex; align-items: center; gap: .65rem; text-decoration: none; min-width: 0; }
            .brand-initials { font-size: 1.1rem; font-weight: 700; color: var(--text-color); }
            .brand-sub { font-size: .95rem; color: var(--muted-text); font-weight: 600; }
            .brand-logo { width: 34px; height: 34px; border-radius: 999px; border: 1px solid var(--border-color); object-fit: cover; object-position: center; }

            .nav-links {
                display: flex;
                gap: .5rem;
            }

            .nav-link {
                color: var(--text-color);
                text-decoration: none;
                font-weight: 650;
                padding: .45rem .7rem;
                border-radius: var(--radius-sm);
                transition: color 0.2s, background 0.2s;
            }

            .nav-link:hover {
                color: var(--primary-color);
                background: color-mix(in srgb, var(--primary-color) 10%, transparent);
            }

            @media (max-width: 768px) {
                .nav-container { gap: .5rem; }
                .nav-toggle { display: inline-flex; align-items:center; justify-content:center; width:44px; height:44px; padding:0; border:1px solid var(--border-color); border-radius:10px; background:var(--surface-1); color:var(--text-color); position: relative; z-index: 1002; box-shadow: var(--shadow-sm); }
                .brand-sub { display: none; }
                /* Off‑canvas menu */
                .nav-links {
                    display: none; flex-direction: column; gap: .35rem;
                    position: fixed; top: 0; right: 0; height: 100svh; width: min(82vw, 340px);
                    background: var(--surface-1); border-left: 1px solid var(--border-color);
                    padding: 4.5rem 1rem 1rem; box-shadow: -16px 0 40px rgba(0,0,0,.35);
                    transform: none;
                    z-index: 1001; overflow-y: auto;
                }
                .nav.open .nav-links { display: flex; }
                body.nav-open::after { content:""; position: fixed; inset: 0; background: rgba(0,0,0,.45); backdrop-filter: blur(1px); z-index: 999; }
                body.nav-open { overflow: hidden; }
                .nav.open .nav-actions { display: none !important; }
                .nav-link { padding:.75rem .85rem; font-size: 1.05rem; }
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
                justify-content: center;
                gap: .5rem;
                min-height: 40px;
                padding: .5rem .8rem;
                border: 1px solid var(--border-color);
                border-radius: 999px;
                text-decoration: none;
                color: var(--text-color);
                background: color-mix(in srgb, var(--surface-1) 86%, transparent);
                transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
                box-shadow: var(--shadow-sm);
            }
            .icon-link:hover { transform: translateY(-1px); border-color: color-mix(in srgb, var(--primary-color) 42%, var(--border-color)); box-shadow: var(--shadow-md); }

            .theme-toggle { cursor: pointer; }

            .section {
                padding: 4.5rem 0;
            }

            .muted { color: var(--muted-text); }
            .inline-actions { display:flex; gap:.5rem; flex-wrap:wrap; }
            .stack-gap { margin-top: 1.5rem; }
            .section-kicker { text-align:center; color:var(--secondary-color); margin:-2rem auto 2rem; max-width: 720px; }
            .bullet-list { margin-left: 1.25rem; }
            .bullet-list-tight { margin-bottom: .75rem; }
            .bullet-list-loose { margin-bottom: 1.25rem; }

            /* Mobile bottom tab bar */
            .mobile-tabbar { display:none; }
            .mobile-tabbar { position: fixed; left:0; right:0; bottom:0; min-height: 66px; display:none; background: rgba(15,23,42,.90); border-top: 1px solid color-mix(in srgb, var(--border-color) 70%, transparent); backdrop-filter: blur(14px); z-index: 999; align-items:center; justify-content: space-around; padding: .25rem max(8px, env(safe-area-inset-left)) calc(max(6px, env(safe-area-inset-bottom))); box-shadow: 0 -18px 48px rgba(0,0,0,.28); }
            .mobile-tabbar .tab { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:2px; color: var(--muted-text); text-decoration:none; font-weight:650; font-size:.75rem; padding:.4rem .42rem; border-radius:10px; min-width: 54px; }
            .mobile-tabbar .tab-ico { font-size: 1.15rem; line-height:1; }
            .mobile-tabbar .tab.active { color:#fff; background: rgba(37,99,235,.22); }
            @media (max-width: 768px) {
                .mobile-tabbar { display:flex; }
                body { padding-bottom: 74px; }
                .experience-chat:not(.experience-chat-page) { display: none; }
                /* Hide when menu is open */
                body.nav-open .mobile-tabbar,
                .nav.open ~ .mobile-tabbar { transform: translateY(110%); transition: transform .2s ease; }
                body.nav-open .experience-chat { display: none; }
            }

            .section-title {
                font-size: clamp(2rem, 5vw, 3.25rem);
                font-weight: 800;
                text-align: center;
                margin-bottom: 3rem;
                color: var(--text-color);
                line-height: 1.1;
            }

            .highlight-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 1rem;
            }

            .highlight-card {
                min-height: 176px;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-lg);
                padding: 1.25rem;
                background: linear-gradient(180deg, color-mix(in srgb, var(--surface-1) 96%, transparent), var(--surface-1));
                box-shadow: var(--shadow-md);
            }

            .highlight-index {
                display: block;
                color: var(--primary-color);
                font-size: .85rem;
                font-weight: 800;
                margin-bottom: .8rem;
                letter-spacing: 0;
            }

            .highlight-copy {
                color: var(--text-color);
                font-weight: 680;
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
                padding: 1.1rem 1.25rem;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-lg);
                background:
                    linear-gradient(135deg, color-mix(in srgb, var(--primary-color) 12%, var(--surface-1)), var(--surface-1));
                box-shadow: var(--shadow-md);
            }

            .resume-callout p { color: var(--muted-text); margin: .15rem 0 0; }
            .resume-callout .btn { flex: 0 0 auto; white-space: nowrap; }

            @media (max-width: 700px) {
                .resume-callout { align-items: stretch; flex-direction: column; }
                .resume-callout .btn { text-align: center; }
            }

            /* About hero */
            .about-hero {
                background:
                    radial-gradient(900px 400px at 10% -10%, color-mix(in srgb, var(--primary-color) 14%, transparent), transparent),
                    linear-gradient(180deg, color-mix(in srgb, var(--surface-1) 96%, transparent), var(--surface-1));
                border: 1px solid var(--border-color);
                border-radius: var(--radius-lg);
                padding: clamp(1.5rem, 4vw, 2.5rem);
                display: grid;
                grid-template-columns: auto 1fr;
                gap: clamp(1.25rem, 4vw, 2.25rem);
                align-items: center;
                box-shadow: var(--shadow-md);
            }
            @media (max-width: 640px){ .about-hero { grid-template-columns: 1fr; text-align:center; } }
            .about-hero .avatar { justify-self: center; margin: 0 auto 1rem; object-fit: cover; object-position: center; }
            .about-content-stack { display: grid; gap: 1.25rem; }

            .hero-cta { display:flex; gap:.75rem; flex-wrap:wrap; }
            @media (max-width: 640px){
                .hero-cta { justify-content:center; }
                .hero-cta .btn { width: 100%; max-width: 320px; }
            }

            /* Stats */
            .stats-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: .75rem; }
            .stats-grid-spaced { margin-bottom:1rem; }
            .stat-card { background: color-mix(in srgb, var(--surface-2) 78%, var(--surface-1)); border:1px solid var(--border-color); border-radius:var(--radius-md); padding: 1rem; text-align:center; }
            .stat-num { font-weight:800; font-size:1.35rem; color: var(--text-color); }
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
                background: linear-gradient(180deg, color-mix(in srgb, var(--surface-1) 96%, transparent), var(--surface-1));
                border-radius: var(--radius-lg);
                padding: 2rem;
                box-shadow: var(--shadow-md);
                transition: transform 0.2s, box-shadow 0.2s;
                border: 1px solid var(--border-color);
            }

            .card:hover {
                transform: translateY(-1px);
                box-shadow: var(--shadow-lg);
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
            .chip { padding: .3rem .65rem; border-radius: 999px; font-size: .82rem; font-weight: 650; background: var(--chip-bg); color: var(--chip-fg); border: 1px solid var(--chip-border); }

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
                background:linear-gradient(180deg, color-mix(in srgb, var(--surface-1) 96%, transparent), var(--surface-1));
                border:1px solid var(--border-color);
                border-radius:var(--radius-lg);
                padding:1rem;
                box-shadow: var(--shadow-lg);
                backdrop-filter: blur(4px);
            }
            .chart-toolbar { display:flex; justify-content:space-between; gap:1rem; margin-bottom:.75rem; align-items:end; flex-wrap:wrap; }
            .chart-control-group { display:grid; gap:.4rem; }
            .chart-control-label { color: var(--muted-text); font-size:.78rem; font-weight:800; }
            .chart-segment { display:flex; gap:.35rem; padding:.25rem; border:1px solid var(--border-color); border-radius:999px; background: color-mix(in srgb, var(--surface-2) 76%, transparent); }
            .chart-segment .icon-link { box-shadow:none; border-color:transparent; background:transparent; }
            .chart-option { position: relative; }
            .chart-hint {
                max-width: 680px;
                margin: -.15rem auto .75rem;
                color: var(--muted-text);
                font-size: .88rem;
                line-height: 1.45;
                text-align: center;
            }
            .chart-controls { display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; }
            .chart-canvas { height:480px; }
            .chart-key { display: none; }
            .chart-key-list {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: .45rem .7rem;
            }
            .chart-key-item {
                display: flex;
                align-items: center;
                gap: .4rem;
                min-width: 0;
                color: var(--muted-text);
                font-size: .78rem;
                line-height: 1.25;
            }
            .chart-key-swatch {
                width: .7rem;
                height: .7rem;
                border-radius: 3px;
                flex: 0 0 auto;
                box-shadow: inset 0 0 0 1px rgba(255,255,255,.22);
            }
            .chart-key-label {
                min-width: 0;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                color: var(--text-color);
                font-weight: 720;
            }
            .chart-key-value {
                white-space: nowrap;
                color: var(--muted-text);
            }

            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-height: 44px;
                padding: 0.75rem 1.35rem;
                background: var(--primary-color);
                color: white;
                text-decoration: none;
                border-radius: var(--radius-sm);
                font-weight: 720;
                line-height: 1.2;
                transition: background 0.2s, transform .15s ease, box-shadow .15s ease;
                border: none;
                cursor: pointer;
                box-shadow: 0 12px 24px color-mix(in srgb, var(--primary-color) 26%, transparent);
            }

            .btn:hover {
                background: var(--primary-strong);
                transform: translateY(-1px);
            }

            .btn-secondary {
                background: var(--secondary-color);
                box-shadow: none;
            }

            .btn-secondary:hover {
                background: #475569;
            }

            .footer {
                background: var(--surface-2);
                color: var(--text-color);
                padding: 2.5rem 0 1rem;
                text-align: center;
                border-top: 1px solid var(--border-color);
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
            .chart-segment .icon-link.active { background: var(--primary-color); color: #fff; border-color: transparent; box-shadow: 0 8px 20px color-mix(in srgb, var(--primary-color) 22%, transparent); }
            .chart-export { margin-left:auto; align-self:end; border-style:dashed; background: color-mix(in srgb, var(--surface-1) 72%, transparent); }
            @media (hover: hover) and (pointer: fine) {
                .chart-option::after {
                    content: attr(data-chart-tip);
                    position: absolute;
                    left: 50%;
                    bottom: calc(100% + .6rem);
                    width: max-content;
                    max-width: 260px;
                    padding: .55rem .7rem;
                    border: 1px solid var(--border-color);
                    border-radius: var(--radius-sm);
                    background: color-mix(in srgb, var(--surface-2) 96%, #000);
                    color: var(--text-color);
                    box-shadow: var(--shadow-md);
                    font-size: .78rem;
                    font-weight: 650;
                    line-height: 1.35;
                    opacity: 0;
                    pointer-events: none;
                    transform: translate(-50%, .2rem);
                    transition: opacity .15s ease, transform .15s ease;
                    z-index: 5;
                }
                .chart-option:hover::after,
                .chart-option:focus-visible::after {
                    opacity: 1;
                    transform: translate(-50%, 0);
                }
            }
            .contact-form { display:grid; gap:1rem; max-width: 720px; }
            .contact-form .form-group { display:block; width:100%; }
            .contact-form label { display:block; font-weight:600; margin-bottom:.35rem; color: var(--muted-text); }
            .contact-form input, .contact-form textarea { width:100%; }
            .contact-form textarea { min-height:160px; resize:vertical; }
            .contact-links { margin: .5rem 0 1rem; }
            .captcha-img { border:1px solid var(--border-color); border-radius:4px; margin-bottom:0.5rem; display:block; }
            .hp-wrap { position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden; }

            @media (max-width: 700px) {
                .section { padding: 3rem 0; }
                .section-title { margin-bottom: 2rem; }
                .card { padding: 1.25rem; }
                .card-grid { grid-template-columns: 1fr; gap: 1rem; }
                .grid-2-1 { gap: 1rem; }
                .highlight-grid { gap: .85rem; }
                .chart-shell { padding: .75rem; display: flex; flex-direction: column; }
                .chart-canvas { height: 320px; order: 4; }
                .chart-toolbar { justify-content:center; align-items:center; gap:.75rem; }
                .chart-control-group { justify-items:center; }
                .chart-control-label { text-align:center; }
                .chart-export { width:100%; max-width: 180px; margin:0 auto; }
                .chart-hint {
                    order: 2;
                    margin: .25rem auto .5rem;
                    padding: 0 .25rem;
                    font-size: .8rem;
                }
                .chart-key {
                    order: 3;
                    display: block;
                    margin: .5rem 0 .25rem;
                    padding: .75rem 0;
                    border-top: 1px solid var(--border-color);
                    border-bottom: 1px solid var(--border-color);
                }
            }
"""

# FastHTML Architecture Audit

Date: 2026-05-31

## Purpose

This project should be a strong example of a FastHTML portfolio app: clear Python element builders, focused page modules, reusable components, and small service boundaries. The goal is not to avoid CSS or JavaScript entirely. The goal is to avoid raw markup sprawl and keep visual/behavioral assets organized so the FastHTML structure stays readable.

## Current Assessment

The app is using FastHTML in the important places:

- Public HTML structure is built with FastHTML element functions such as `Div`, `Section`, `H2`, `P`, `A`, `Form`, and `Button`.
- `src.main:app` is now a thin Vercel-stable route layer.
- `src/pages/` owns page body builders.
- `src/components/` owns reusable UI and pattern builders.
- `src/services/` owns GitHub, email, content, contact-form, and chat logic.

This is not a template-string app. The remaining cleanup is about presentation organization and reusable patterns.

## Findings

### 1. CSS and JavaScript Are First-Class Asset Files

Global CSS, global browser interactions, chat behavior, and chart behavior now live as real `.css` and `.js` files under `src/assets/`. FastHTML still injects the assets into the rendered page, but the source files are now readable by editor tooling and Biome.

Current direction:

- Keep page structure in FastHTML Python builders.
- Keep browser-native behavior in JavaScript files when JavaScript is the right tool.
- Keep CSS in CSS files instead of Python strings.
- Use small Python loader modules only to read those assets into FastHTML headers/components.

### 2. Page Builders Should Prefer Components Over Repeated Structures

Repeated cards, chips, stat boxes, timelines, bullet lists, and inline action rows now have small helpers in `src/components/patterns.py`.

Current direction:

- Keep page modules readable and domain-specific.
- Promote repeated UI structure into components only when repetition is real.
- Avoid over-abstracting every `Div`; FastHTML is clearest when simple markup stays local.

### 3. Inline Style Sprawl Should Stay Near Zero

The page modules no longer use `style=`. Presentation that was previously inline now lives behind CSS classes such as:

- `inline-actions`
- `bullet-list`
- `stack-gap`
- `section-kicker`
- `project-card-footer`
- `chart-shell`
- `captcha-img`
- `alert-success`, `alert-info`, `alert-error`

Small one-off inline styles are acceptable in prototypes, but tracked pages should default to named classes.

### 4. Dynamic JavaScript Has A Data Boundary

The home page chart renders server-side data into a JSON script tag and keeps reusable Plotly behavior in `src/assets/tech-stack-chart.js`.

This keeps the page builder responsible for data and the browser asset responsible for rendering/interactions.

### 5. Chat Widget Is Self-Contained With Extracted Assets

`src/components/chat/widget.py` still owns chat markup and state configuration, while `src/assets/chat.css` and `src/assets/chat.js` own presentation and browser interaction. This preserves the portable widget boundary without hiding CSS/JS in Python strings.

## Target Structure

```text
src/
├── app_shell.py          # FastHTML app construction, headers, static mount
├── main.py               # Thin route orchestration and stable app export
├── assets/               # CSS/JS asset files plus small Python loaders
├── components/           # Reusable FastHTML components and patterns
├── pages/                # Page body builders
├── services/             # External integrations and business workflows
└── utils/                # Cross-cutting helpers
```

## Done In This Pass

- Added this audit as a tracked reference.
- Added `src/components/patterns.py` for repeated FastHTML structures.
- Added `src/components/forms.py` for repeated contact form field structures.
- Made desktop navigation and mobile tab navigation share one typed source of truth.
- Added asset helper functions so FastHTML headers/components load CSS/JS through a consistent boundary.
- Added a typed theme registry plus shared desktop/mobile FastHTML controls for theme and appearance mode.
- Removed inline `style=` usage from page/component builders.
- Extracted large CSS/JS strings into first-class asset files and added Biome checks.
- Kept route behavior and visual design intentionally stable.

## Recommended Follow-Up PRs

1. UX redesign pass: improve visual hierarchy, homepage first impression, desktop/mobile layout, and CTA ergonomics.
2. Content source-of-truth pass: move more profile/about/project copy out of Python literals and into structured content.
3. Chat/RAG quality pass: review the chat widget boundary, answer rendering, source display, and free-tier fallback UX.
4. Theme expansion pass: add more branded theme packs only after the token contract remains stable through real use.

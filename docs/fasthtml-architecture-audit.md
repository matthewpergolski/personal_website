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

### 1. Global CSS and JavaScript Are Acceptable, But Large

`src/assets/styles.py` and `src/assets/scripts.py` keep the entrypoint clean, but they are still large Python strings. That is acceptable for a low-dependency FastHTML app, but it is not the final form of a world-class example.

Future options:

- Keep them as Python assets while the app is small.
- Move to static `/static/app.css` and `/static/app.js` if cacheability, editor tooling, or syntax highlighting become more important.
- Split CSS by ownership only if it reduces review friction; avoid fragmenting styles prematurely.

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

### 4. Dynamic JavaScript Needs A Clear Boundary

The home page chart still emits a dynamic Plotly script because it embeds server-side data into browser behavior. That is reasonable, but it should remain isolated.

Future options:

- Move reusable chart rendering code into `src/assets/scripts.py` and pass data through a JSON script tag or `data-*` attributes.
- Keep the dynamic script local to `src/pages/home.py` if chart behavior remains one-off.

### 5. Chat Widget Is Self-Contained But Should Be Reviewed Later

`src/components/chat/widget.py` owns its own CSS and JavaScript. That can be a useful component boundary, especially for a portable widget, but it should be revisited during the chat/RAG quality pass.

Future options:

- Keep chat style/script colocated with the widget.
- Extract chat CSS/JS into assets if it grows or needs independent tooling.

## Target Structure

```text
src/
├── app_shell.py          # FastHTML app construction, headers, static mount
├── main.py               # Thin route orchestration and stable app export
├── assets/               # Global CSS/JS assets
├── components/           # Reusable FastHTML components and patterns
├── pages/                # Page body builders
├── services/             # External integrations and business workflows
└── utils/                # Cross-cutting helpers
```

## Done In This Pass

- Added this audit as a tracked reference.
- Added `src/components/patterns.py` for repeated FastHTML structures.
- Removed inline `style=` usage from page/component builders.
- Kept route behavior and visual design intentionally stable.

## Recommended Follow-Up PRs

1. UX redesign pass: improve visual hierarchy, homepage first impression, desktop/mobile layout, and CTA ergonomics.
2. Content source-of-truth pass: move more profile/about/project copy out of Python literals and into structured content.
3. Chat/RAG quality pass: review the chat widget boundary, answer rendering, source display, and free-tier fallback UX.
4. Visual regression pass: add lightweight browser/mobile screenshot checks before larger design changes.

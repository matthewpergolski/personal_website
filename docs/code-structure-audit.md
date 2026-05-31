# Code Structure Audit

Date: 2026-05-30

## Summary

The app is healthy enough to keep shipping, but `src/main.py` has become the main maintenance risk. It currently owns app setup, global CSS, browser JavaScript, static mounting, page rendering, route handlers, chart behavior, contact form validation, CAPTCHA handling, and redirects.

The next refactor should be incremental. Avoid a broad rewrite; split stable seams first, keep route behavior unchanged, and add smoke tests around moved pages.

## Current Shape

| Area | Current file | Notes |
| --- | --- | --- |
| App entrypoint, routes, CSS, JavaScript, page composition | `src/main.py` | 1,738 lines; largest module by far |
| Shared UI primitives | `src/components/ui.py` | Navigation, hero, footer, mobile tabs |
| Chat UI | `src/components/chat/widget.py` | Self-contained CSS/JS widget |
| RAG logic | `src/services/rag/simple_chat.py` | Reasonably scoped service module |
| Resume sync parser | `scripts/sync_resume_content.py` | Large, but isolated CLI/parser responsibility |
| Contact email | `src/services/email.py` | Small service, route still owns most contact workflow |
| Rate limiting | `src/utils/rate_limit.py` | Isolated helper, file-backed best-effort limits |

Largest Python files:

- `src/main.py`: 1,738 lines
- `scripts/sync_resume_content.py`: 609 lines
- `src/services/rag/simple_chat.py`: 291 lines
- `src/components/ui.py`: 236 lines
- `src/components/chat/widget.py`: 235 lines

Largest route/page functions in `src/main.py`:

- `home`: 172 lines
- `contact`: 155 lines
- `about`: 154 lines
- `contact_submit`: 106 lines
- `projects`: 93 lines
- `resume`: 74 lines

## Findings

### 1. `src/main.py` Mixes Too Many Responsibilities

`src/main.py` should eventually become a thin composition layer: create the app, register routes, and delegate page/body construction. Today it mixes page layout, form handling, data loading, external service calls, and browser behavior.

Impact:

- UI edits are hard to review because unrelated page logic lives nearby.
- Small visual changes can accidentally touch routing, security, or startup code.
- Tests mostly cover contact/RAG/parser behavior, not page rendering regressions.

Recommended split:

- `src/app.py`: FastHTML app construction, startup validation, static mounting.
- `src/routes/pages.py`: page route registration or route handlers.
- `src/routes/api.py`: JSON endpoints such as `/api/rag/chat`.
- `src/routes/contact.py`: contact GET/POST routes.
- `src/pages/home.py`, `src/pages/about.py`, `src/pages/resume.py`, `src/pages/projects.py`, `src/pages/contact.py`, `src/pages/chat.py`: page composition.

### 2. Global CSS and Browser JavaScript Should Move Out of the Entrypoint

Global CSS and browser scripts are embedded in `src/main.py` inside the FastHTML app setup. The navigation edge-swipe JavaScript block is duplicated, which is a concrete sign the embedded script is becoming hard to maintain.

Impact:

- Large string literals obscure actual Python structure.
- JavaScript cannot be linted or tested independently.
- Duplicate handlers can cause subtle interaction bugs.

Recommended split:

- Move global CSS into `src/assets/styles.py` first as a Python string to minimize behavior change.
- Move global browser scripts into `src/assets/scripts.py` next.
- After that, consider static `/static/app.css` and `/static/app.js` if cache/versioning needs justify it.
- Remove the duplicate edge-swipe block as the first low-risk cleanup.

### 3. Page Composition Should Be Modularized Before Further UX Work

Home, About, Resume, Projects, Contact, and Chat are all composed directly in route functions. That makes the next UX pass more expensive than it needs to be.

Impact:

- Future layout work will keep inflating `src/main.py`.
- Reused patterns such as cards, chips, timeline rows, stat boxes, and CTAs are recreated inline.
- Inline `style=` attributes are scattered through page functions.

Recommended split:

- Move page body builders first, without changing URLs:
  - `build_home_page(...)`
  - `build_projects_page(...)`
  - `build_about_page(...)`
  - `build_resume_page(...)`
  - `build_contact_page(...)`
  - `build_chat_page()`
- Promote repeated UI pieces into small components only after the page modules exist.
- Add route smoke tests for `/`, `/projects`, `/about`, `/resume`, `/contact`, `/chat`, and `/resume/download`.

### 4. Contact Form Workflow Is Security-Sensitive and Should Be Isolated

The contact POST route handles validation, timing checks, CAPTCHA, rate limiting, email sending, Vercel fallback behavior, and local message persistence in one function.

Impact:

- It is harder to change UI copy or form layout without touching security logic.
- Security behavior is already tested, but the production route remains dense.

Recommended split:

- `src/services/contact_form.py` for validation and result objects.
- Keep `src/services/email.py` for delivery.
- Keep rate limiting in `src/utils/rate_limit.py`.
- Route should translate form data into a contact service call and redirect based on a structured result.

### 5. Configuration Access Is Inconsistent

The repo has `src/config.py`, but `src/main.py`, `src/components/ui.py`, `src/services/github.py`, and `src/services/email.py` still read many environment variables directly.

Impact:

- Defaults and fallback behavior are spread across modules.
- It is harder to reason about what Vercel env vars are actually used.

Recommended split:

- Keep secrets read close to services that need them.
- Use `get_config()` for public site identity values: title, description, LinkedIn URL, GitHub username, resume URL, public email.
- Do not force all config into one object if it makes secret handling less clear.

### 6. Logging Is Informal

Several services use `print(...)` for warnings/errors. That works on Vercel, but it makes filtering and testing harder.

Impact:

- Runtime logs are readable, but not structured by module/severity.
- Error handling sometimes silently swallows exceptions.

Recommended split:

- Introduce standard-library `logging` in service modules.
- Keep user-facing fallback behavior unchanged.
- Prefer logging exceptions at service boundaries, not inside low-level helper loops unless actionable.

## Recommended PR Plan

### PR 1: Extract App Shell Assets

Goal: reduce `src/main.py` size without changing routes or page output.

Scope:

- Move global CSS to `src/assets/styles.py`.
- Move global JavaScript to `src/assets/scripts.py`.
- Remove duplicate edge-swipe navigation script.
- Keep FastHTML header wiring in the app setup.
- Run current tests and do browser smoke checks on desktop/mobile nav.

Why first:

- Lowest behavioral risk.
- Makes future page refactors easier to review.

### PR 2: Add Route Smoke Tests

Goal: create guardrails before moving page modules.

Scope:

- Add tests for public GET routes.
- Assert expected status codes and key text/links.
- Include `/resume/download` redirect behavior.
- Avoid brittle full-HTML snapshots.

Why second:

- Gives confidence before splitting page builders.

### PR 3: Extract Page Builders

Goal: move page composition out of route handlers.

Scope:

- Add `src/pages/` modules.
- Route handlers should load data and return page builders.
- Keep visual output unchanged except for trivial whitespace.

Why third:

- Cuts the largest route functions down while preserving behavior.

### PR 4: Extract Contact Workflow

Goal: isolate security-sensitive contact validation from rendering.

Scope:

- Add `src/services/contact_form.py`.
- Return structured outcomes from validation/delivery.
- Keep existing contact tests passing and add targeted service tests.

Why fourth:

- Contact behavior is important enough to refactor after route/page smoke tests exist.

### PR 5: Config Cleanup

Goal: reduce scattered public config lookups.

Scope:

- Use `get_config()` consistently for public site values.
- Keep provider secrets local to provider services.
- Update docs only if env var behavior changes.

Why fifth:

- Easier after app/page boundaries are clearer.

## Not Recommended Yet

- Do not introduce a frontend framework just to solve organization.
- Do not move to static CSS/JS files until the Python-string extraction is stable.
- Do not rewrite the resume parser as part of page refactoring.
- Do not add a database or external content service for this audit; the current Vercel/free-first constraints still favor committed JSON plus GitHub Actions sync.


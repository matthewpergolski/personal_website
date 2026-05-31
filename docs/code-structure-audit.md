# Code Structure Audit

Date: 2026-05-30
Updated: 2026-05-31

## Summary

The app is healthy enough to keep shipping. The initial refactor pass has reduced `src/main.py` from a monolithic route/rendering module into a thinner route orchestration layer. App shell setup, global CSS/JavaScript, public page builders, and contact form validation now live in dedicated modules.

Future refactors should stay incremental. Keep route behavior unchanged, add or update smoke tests around moved pages, and avoid turning this FastHTML app into a frontend/backend framework migration unless the product need is clear.

## Current Shape

| Area | Current file | Notes |
| --- | --- | --- |
| App entrypoint and route orchestration | `src/main.py` | Thin Vercel-stable route layer around app/page/service modules |
| App shell, headers, static mount | `src/app_shell.py` | FastHTML app construction and shared assets |
| Global CSS and browser JavaScript | `src/assets/styles.py`, `src/assets/scripts.py` | Extracted from the entrypoint |
| Page composition | `src/pages/*.py` | Home, projects, about/resume, contact, and chat builders |
| Shared UI primitives | `src/components/ui.py` | Navigation, hero, footer, mobile tabs |
| Chat UI | `src/components/chat/widget.py` | Self-contained CSS/JS widget |
| RAG logic | `src/services/rag/simple_chat.py` | Reasonably scoped service module |
| Resume sync parser | `scripts/sync_resume_content.py` | Large, but isolated CLI/parser responsibility |
| Contact email | `src/services/email.py` | Small SMTP delivery service |
| Contact form rules | `src/services/contact_form.py` | Validation, CAPTCHA session helpers, local fallback persistence |
| Rate limiting | `src/utils/rate_limit.py` | Isolated helper, file-backed best-effort limits |

Largest Python files after the first refactor pass:

- `scripts/sync_resume_content.py`: 609 lines
- `src/main.py`: about 300 lines
- `src/services/rag/simple_chat.py`: 291 lines
- `src/components/ui.py`: 236 lines
- `src/components/chat/widget.py`: 235 lines

Largest remaining route/workflow functions in `src/main.py` are now small enough to review directly. The next size risk is `scripts/sync_resume_content.py`, which is acceptable while it remains an isolated CLI/parser responsibility.

## Findings

### 1. `src/main.py` No Longer Owns Most Rendering, But Routes Could Still Be Split Later

`src/main.py` now creates the stable app export, registers routes, loads request-specific data, and delegates rendering/workflow details. A later split into `src/routes/` is possible, but it is no longer urgent.

Impact:

- UI edits are hard to review because unrelated page logic lives nearby.
- Small visual changes can accidentally touch routing, security, or startup code.
- Tests mostly cover contact/RAG/parser behavior, not page rendering regressions.

Remaining optional split:

- `src/routes/pages.py`: public page routes.
- `src/routes/api.py`: JSON endpoints such as `/api/rag/chat`.
- `src/routes/contact.py`: contact GET/POST route handlers.

### 2. Global CSS and Browser JavaScript Are Extracted

Global CSS and browser scripts now live in `src/assets/styles.py` and `src/assets/scripts.py`. The duplicate edge-swipe handler was removed.

Impact:

- Large string literals obscure actual Python structure.
- JavaScript cannot be linted or tested independently.
- Duplicate handlers can cause subtle interaction bugs.

Remaining optional improvement:

- Consider static `/static/app.css` and `/static/app.js` if cache/versioning needs justify it.

### 3. Page Composition Is Ready For Further UX Work

Home, Projects, About, Resume, Contact, and Chat now have page builders under `src/pages/`. This is the right base for the next UX pass.

Impact:

- Future layout work will keep inflating `src/main.py`.
- Reused patterns such as cards, chips, timeline rows, stat boxes, and CTAs are recreated inline.
- Inline `style=` attributes are scattered through page functions.

Recommended next step:

- Promote repeated UI pieces into small components only after the page modules exist.
- Continue route smoke tests for `/`, `/projects`, `/about`, `/resume`, `/contact`, `/chat`, and `/resume/download`.

### 4. Contact Form Workflow Is Isolated Enough For Current Risk

The contact POST route still orchestrates the workflow, but validation, timing thresholds, CAPTCHA session helpers, error-code selection, and local fallback persistence now live in `src/services/contact_form.py`.

Impact:

- It is harder to change UI copy or form layout without touching security logic.
- Security behavior is already tested, but the production route remains dense.

Remaining optional improvement:

- Introduce a structured contact workflow result if the POST route grows again.

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

Status: complete in PR #10.

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

Status: complete in PR #10 expansion.

Scope:

- Add tests for public GET routes.
- Assert expected status codes and key text/links.
- Include `/resume/download` redirect behavior.
- Avoid brittle full-HTML snapshots.

Why second:

- Gives confidence before splitting page builders.

### PR 3: Extract Page Builders

Status: complete in PR #10 expansion.

Scope:

- Add `src/pages/` modules.
- Route handlers should load data and return page builders.
- Keep visual output unchanged except for trivial whitespace.

Why third:

- Cuts the largest route functions down while preserving behavior.

### PR 4: Extract Contact Workflow

Status: complete in PR #10 expansion.

Scope:

- Add `src/services/contact_form.py`.
- Return structured outcomes from validation/delivery.
- Keep existing contact tests passing and add targeted service tests.

Why fourth:

- Contact behavior is important enough to refactor after route/page smoke tests exist.

### PR 5: Config Cleanup

Status: partly complete in PR #10 expansion.

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

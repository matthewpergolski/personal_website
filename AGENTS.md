# Agent Instructions

This file is the single source of truth for coding-agent behavior in this repository. Claude, Codex, Cline, and other agents should read this first, then progressively open only the files needed for the task.

## Project Snapshot

- Product: FastHTML portfolio site for Matthew Pergolski, with GitHub-backed project pages, resume/about content, a contact form, and an experience chat assistant.
- Backend/API: Python 3.12 ASGI app using FastHTML/Starlette, served through `src.main:app`.
- UI: FastHTML components plus in-page CSS and small vanilla JavaScript snippets. There is no React/Vue frontend.
- Deployment: Vercel Git integration with `vercel.json` routing all requests to `api/index.py`; Vercel installs dependencies from `pyproject.toml` and `uv.lock`.
- Package manager: `uv` only.
- Tests/lint: `pytest`, `ruff`, and `pre-commit`.
- Chat: free-first local retrieval over committed portfolio data, with optional Hugging Face generation if `HUGGINGFACE_API_KEY` is configured.

## Progressive Disclosure

Start with these files, depending on the task:

- General orientation: `README.md`, then `DEPLOYING.md` if deployment is relevant.
- App routing/UI: `src/main.py`, `src/components/ui.py`, `src/utils/render.py`.
- Chat/RAG: `src/components/chat/widget.py`, `src/services/rag/simple_chat.py`, `tests/test_rag_chat.py`.
- Contact/security: `src/main.py`, `src/services/email.py`, `src/utils/rate_limit.py`, `tests/test_contact.py`.
- Content changes: `data/experience.json`, optionally `data/site.json.example`.
- Dependencies/tooling: `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`.

Do not bulk-read generated or lock files unless the task requires dependency or deploy debugging.

## Development Rules

- Use `uv` for dependency management and command execution.
- Add runtime dependencies with `uv add <package>`.
- Add development dependencies with `uv add --dev <package>`.
- Run app locally with `uv run uvicorn src.main:app --host 127.0.0.1 --port 8000`.
- Run tests with `uv run pytest -q`.
- Run lint/format with `uv run pre-commit run --all-files`.
- Keep files/modules under roughly 7,800 tokens; split large modules before they become hard to review.
- Prefer small, focused changes over broad rewrites.

## Security Rules

- Never commit `envs.sh`, real API keys, SMTP passwords, Vercel tokens, GitHub tokens, or provider secrets.
- Vercel secrets should be marked as sensitive environment variables.
- After the April 2026 Vercel security incident, rotate any Vercel env vars that were not already marked sensitive, especially tokens, SMTP credentials, signing secrets, and provider API keys.
- `SESSION_SECRET` should be configured in Vercel for stable signed sessions.
- The chat assistant stores history in browser `sessionStorage`; this is per visitor and per browser tab/session, not shared server-side.
- Contact form fallback writes messages locally only outside Vercel. On Vercel, failed SMTP returns an error instead of claiming durable storage.

## Chat/RAG Policy

- Keep the chat free-first. Local retrieval must work without external AI providers.
- Hugging Face is optional and should be treated as a best-effort answer-polishing layer.
- If Hugging Face is missing, rate-limited, or out of free credits, return the local retrieved answer and a clear note rather than failing.
- Do not add heavyweight vector databases, local embedding models, or model downloads unless explicitly requested; they are poor fits for Vercel serverless and free-tier cold starts.

## Memory Bank

If a `memory-bank/` directory exists, read it in this order only when the task needs broader project history:

1. `projectbrief.md`
2. `productContext.md`
3. `systemPatterns.md`
4. `techContext.md`
5. `activeContext.md`
6. `progress.md`

If the user explicitly says "update memory bank", review all memory-bank files and update current state, next steps, and notable decisions.

## Agent Skill Scaffolding

- Shared future skills live under `.codex/skills/`.
- `.claude` points to `.codex` so Claude-facing skills share the same files.
- `.cline/skills` points to `.codex/skills`.
- `.cline/rules/AGENTS.md` points back to this file.
- `CLAUDE.md` points back to this file.

Do not duplicate standards across agent-specific files; update `AGENTS.md` instead.

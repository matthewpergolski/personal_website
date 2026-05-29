# Deploying the FastHTML App

This guide covers deploying this repository with Vercel's Git integration and Python runtime, plus notes on environment variables, cold starts, and alternatives.

## Overview
- Primary deployment model: Vercel Git integration using `vercel.json` + `api/index.py` (routes everything to the FastHTML ASGI app).
- Dependencies are installed from the committed root `pyproject.toml` and `uv.lock`; there is no separate generated `api/requirements.txt`.
- Alternative: Docker (see Dockerfile). The container must listen on `$PORT`.
- Persistence: Vercel instances are ephemeral. Rate limits are best-effort in `/tmp`; contact messages should be delivered through SMTP or another durable service.
- Recent security improvements (contact form validation, rate limiting, CAPTCHA, email handling) are included on `main`.

## Prerequisites
- GitHub repository with this code pushed.
- Vercel account, GitHub integration enabled.
- Secrets NOT committed to the repo (don’t commit `envs.sh`).

## 1) Commit and Push
```bash
git add .
git commit -m "Initial commit: Dockerized FastHTML app"
git branch -M main
git remote add origin <your-remote-url>
git push -u origin main
```

## 2) Create Vercel Project
1. In Vercel, click “New Project” → “Import Git Repository”.
2. Select this repo.
3. Use the repository defaults. `vercel.json` routes requests to the Python ASGI adapter in `api/index.py`.

## 3) Environment Variables
Set these in the Vercel project Settings → Environment Variables. Do not upload `envs.sh`.

- Core
  - `GITHUB_USERNAME` (required)
  - `GITHUB_TOKEN` (required; fine‑grained PAT with read‑only public_repo)
  - `CONTACT_EMAIL`
  - `SESSION_SECRET` (recommended; long random string for stable signed session cookies)
  - `SITE_TITLE` (optional)
  - `SITE_DESCRIPTION` (optional)
  - `LINKEDIN_URL` (optional)
  - `RESUME_URL` (optional)

- SMTP (for contact form)
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
  - `SMTP_FROM` (defaults to `CONTACT_EMAIL`)
  - `SMTP_TO` (defaults to `CONTACT_EMAIL`)
  - `SMTP_TLS` ("true"/"false")

- Anti‑spam (optional tuning)
  - `RATE_IP_PER_HOUR` (default 3)
  - `RATE_GLOBAL_PER_DAY` (default 50)
  - `CONTACT_MIN_SECONDS` (default 2.5; ignored in DEBUG locally)
  - `CONTACT_MIN_MSG_LEN` (default 10; relaxed in DEBUG locally)
  - `CAPTCHA_SECRET` (optional; used to hash self-hosted CAPTCHA answers; defaults to `SESSION_SECRET`)

## 4) Deploy
- Click “Deploy”.
- Future pushes to feature branches create Preview deployments.
- Pushes or merges to the production branch, usually `main`, create Production deployments.

## 5) Verify
- Open the deployment URL.
- Test pages and the contact form. Configure SMTP before relying on Vercel contact submissions; local file fallback is disabled on Vercel because `/tmp` is ephemeral.

## Cold Starts & Availability
- Vercel Hobby plan scales to zero after inactivity; first request after idle can take a few seconds. Not “always on”.
- If you need an always‑on instance, consider Fly.io, Render, or Railway (often low‑cost) using the same Dockerfile.

## Logs & Troubleshooting
- View logs in the Vercel dashboard (Build Logs and Runtime Logs).
- Ensure all required env vars are set.
- If GitHub rate limits hit, check token scope and validity.
- SMTP issues: verify credentials, port, and TLS settings.

## Local Development Parity
- Devcontainer/VS Code: use `./app.sh` or `uv run uvicorn src.main:app --reload`.
- Docker locally:
  ```bash
  docker build -t fasthtml-app .
  docker run --rm -p 8000:8000 \
    -e GITHUB_USERNAME=... -e GITHUB_TOKEN=... \
    -e CONTACT_EMAIL=... -e SMTP_HOST=... -e SMTP_USER=... -e SMTP_PASSWORD=... \
    fasthtml-app
  ```

## Security Notes
- Do not commit secrets (tokens, app passwords). Use Vercel env vars.
- Rotate any credentials that were previously committed.
- `.dockerignore` and `.vercelignore` exclude sensitive/dev files from builds.

## Alternatives
- GHCR + other platforms: This repo also includes a `Dockerfile` suitable for Fly.io/Render/Railway/Cloud Run.

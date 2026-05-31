# FastHTML Professional Portfolio Website

A visually stunning and technically impressive portfolio website built exclusively with FastHTML, designed to showcase GitHub projects and serve as a professional resume for data science and AI/ML engineering roles.

## 🚀 Features

- **Professional Design**: Clean, modern interface perfect for technical hiring managers
- **GitHub Integration**: Real-time project showcase with GitHub API
- **Responsive Layout**: Works perfectly on all devices
- **FastHTML Only**: No external CSS frameworks - pure FastHTML styling
- **Professional Pages**:
  - Home with hero section
  - Projects gallery with GitHub integration
  - About page with professional background
  - Resume page with downloadable CV
  - Contact page with professional form

## 🛠️ Technology Stack

- **Backend/API**: Python 3.12 ASGI app built with FastHTML/Starlette. `src/main.py` keeps the public route entrypoints, `src/app_shell.py` builds the FastHTML app, and Vercel enters through `api/index.py`.
- **UI framework**: FastHTML server-rendered page builders in `src/pages/`, reusable components in `src/components/`, in-page CSS, and small vanilla JavaScript helpers. There is no React/Vue frontend.
- **Chat/RAG**: Free-first local retrieval over committed portfolio data, with optional Hugging Face Inference API response polishing.
- **Data sources**: `data/experience.json`, optional public `data/site.json`, an optional Google Docs/Drive resume source sync, and GitHub REST API calls through `httpx`.
- **Deployment/hosting**: Vercel Git integration using `vercel.json` and the Vercel Python runtime.
- **Dependencies**: Managed by `uv` through `pyproject.toml` and `uv.lock`.
- **Quality tooling**: Ruff formatting/linting, pytest, pre-commit, and GitHub Actions.

## 📋 Prerequisites

- Python 3.12+
- UV package manager (`pip install uv`)
- GitHub API credentials (for project integration)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd fasthtml-portfolio
```

### 2. Configure Environment
Copy and edit the environment file:
```bash
cp envs.sh.example envs.sh
# Edit envs.sh with your GitHub credentials and personal information
# Optional: set RESUME_URL, SMTP_*, and bot protection keys
```

### 3. Run the Application
Use the launcher script for the best experience:
```bash
./app.sh
```

Or run directly with UV:
```bash
uv run python src/main.py
```

### 4. Access the Website
Open your browser and navigate to:
- **Local**: http://localhost:8000
- **Network**: http://0.0.0.0:8000

## 📁 Project Structure

```
fasthtml-portfolio/
├── api/
│   └── index.py            # Vercel Python entrypoint
├── src/
│   ├── __init__.py          # Package initialization
│   ├── app_shell.py         # FastHTML app/header/static setup
│   ├── assets/              # Global CSS/JavaScript strings wired into FastHTML headers
│   ├── config.py            # Environment/public site configuration
│   ├── main.py              # Route orchestration and stable Vercel app export
│   ├── components/          # Reusable FastHTML UI components
│   ├── pages/               # Page body builders for public routes
│   ├── services/            # GitHub, email, content, and chat services
│   └── utils/               # Rendering and rate-limit helpers
├── data/
│   ├── experience.json      # Portfolio/resume/chat source content
│   └── site.json.example    # Optional public site config template
├── docs/
│   ├── code-structure-audit.md # Refactor audit and recommended PR sequence
│   └── fasthtml-architecture-audit.md # FastHTML usage and structure guidance
├── tests/                   # pytest coverage, including route smoke tests
├── scripts/
│   ├── push-vercel-envs     # Sync selected envs.sh values to Vercel
│   └── sync_resume_content.py # Parse resume source into data/experience.json
├── AGENTS.md                # Shared coding-agent instructions
├── app.sh                  # Application launcher script
├── envs.sh.example         # Environment template
├── pyproject.toml          # UV project configuration
├── uv.lock                 # Dependency lock file
├── vercel.json             # Vercel routing/build configuration
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables (envs.sh)
```bash
# GitHub Integration (required for GitHub dashboard)
export GITHUB_USERNAME="your-github-username"
export GITHUB_TOKEN="your-github-personal-access-token"

# Contact Information
export CONTACT_EMAIL="your-email@example.com"

# Social Media Links
export LINKEDIN_URL="your-linkedin-profile"

# Application Settings
export DEBUG="true"
export OWNER_NAME="Your Name"
export SITE_TITLE="Your Name - Professional Title"
export SITE_DESCRIPTION="Brief professional description"

# Resume (external link preferred)
# For Google Docs: https://docs.google.com/document/d/YOUR_FILE_ID/export?format=pdf
export RESUME_URL="https://docs.google.com/document/d/YOUR_FILE_ID/export?format=pdf"

# Optional resume source for the content sync workflow.
# Prefer a Google Docs edit/share URL so the sync can fetch plain text.
# RESUME_URL stays the public download link used by /download-resume.
# export RESUME_SOURCE_URL="https://docs.google.com/document/d/YOUR_FILE_ID/edit"

# SMTP (contact form)
# Gmail example (use App Password):
# export SMTP_HOST=smtp.gmail.com
# export SMTP_PORT=587
# export SMTP_TLS=true
# export SMTP_USER=your_gmail@gmail.com
# export SMTP_PASSWORD=your_16_char_app_password
# export SMTP_FROM=your_gmail@gmail.com
# export SMTP_TO=your_hide_my_email@icloud.com   # or your inbox

# Recommended on Vercel: stable session/cookie secret.
# export SESSION_SECRET="replace-with-a-long-random-string"

# Optional CAPTCHA hash secret. If omitted, the app uses SESSION_SECRET/session key.
# export CAPTCHA_SECRET="replace-with-a-long-random-string"

# Rate limits (server-side safeguards)
export RATE_IP_PER_HOUR=3
export RATE_GLOBAL_PER_DAY=50

# Optional experience chat generation.
# If omitted, chat still works with local retrieval only.
# If configured and Hugging Face is rate-limited, chat falls back to local retrieval.
# export HUGGINGFACE_API_KEY=hf_xxx
# export HUGGINGFACE_CHAT_MODEL=HuggingFaceTB/SmolLM2-1.7B-Instruct
# export RAG_MAX_RESPONSE_TOKENS=220
# export RAG_TEMPERATURE=0.2
```

### Public site config (non-secret)

For non-secret values that you want in source control, such as public display copy, a public email alias, default titles, or links, add `data/site.json` from `data/site.json.example`:

```json
{
  "owner_name": "Your Name",
  "brand_initials": "YN",
  "brand_subtitle": "Portfolio",
  "site_title": "Personal Portfolio",
  "site_description": "AI/ML Engineer & Data Scientist",
  "hero_kicker": "AI/ML Engineering Portfolio",
  "hero_primary_cta": "View Projects",
  "hero_chat_cta": "Experience Chat",
  "footer_tagline": "Data Science • Machine Learning • AI Engineering",
  "public_email": "contact@your-domain.com",
  "linkedin_url": "https://linkedin.com/in/your-profile",
  "github_username": "your-github-username",
  "resume_url": "https://docs.../export?format=pdf",
  "contact_intro": "I'm always interested in discussing new opportunities.",
  "contact_response_time": "I typically respond to emails within 24 hours.",
  "resume_pdf_prompt": "Want the PDF version?",
  "resume_pdf_description": "Download the formatted resume, or browse the expanded experience details below."
}
```

At runtime the app merges env vars with this JSON:
- Env vars override JSON for deployment-specific values, for example `OWNER_NAME`, `SITE_TITLE`, `SITE_DESCRIPTION`, `PUBLIC_EMAIL`, social links, and resume links.
- `PUBLIC_EMAIL` is preferred for the Contact page; `CONTACT_EMAIL` and `SMTP_TO` are fallbacks.
- `data/experience.json` remains the source of truth for resume-derived About, Resume, Highlights, Skills, and chat retrieval content.
- Keep secrets such as tokens and SMTP credentials in env vars only.

### GitHub Token Setup
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Add the token to your `envs.sh` file

## 🎨 Design Philosophy

- **Professional**: Clean, sophisticated design for technical audiences
- **Minimalist**: Focus on content with subtle visual enhancements
- **Responsive**: Perfect experience across all device sizes
- **FastHTML Native**: Leverages FastHTML's styling capabilities exclusively
- **Performance**: Optimized for fast loading and smooth interactions

## 🏗️ Architecture

### Component-Based Design
- Reusable UI components built with FastHTML
- Server-side rendering for optimal performance
- HTMX integration for interactive elements
- Modular page structure for maintainability

### GitHub Integration
- Real-time project data fetching
- Rate limiting and error handling
- Caching strategy for performance
- Graceful degradation on API failures

### Content (single source of truth)
- `data/experience.json` drives About + Resume (summary, highlights, experience, education, skills, snapshot stats).
- Home Highlights render from the same file; update once, reflected everywhere.
- The chat assistant also retrieves from this same file, including synced `resume_text` when present.

### Resume source sync
- `scripts/sync_resume_content.py` parses a Google Docs, Google Drive PDF/DOCX, PDF, DOCX, or text resume source into `data/experience.json`.
- Set `RESUME_SOURCE_URL` as a GitHub repository variable or secret, then run the `Sync resume content` workflow manually or let the monthly schedule check for changes.
- The workflow validates that only `data/experience.json` changed, runs formatting/lint/tests, then opens and merges a PR when generated content changes. Unchanged content preserves the previous sync timestamp to avoid noisy PRs.
- Synced raw `resume_text` redacts email addresses and phone numbers before it is written.
- Manual GitHub run: Actions -> `Sync resume content` -> `Run workflow` -> branch `main`.
- Manual CLI run:
  ```bash
  gh workflow run sync-resume.yml --repo matthewpergolski/personal_website --ref main
  ```
- Local dry run:
  ```bash
  uv run python scripts/sync_resume_content.py --input tests/fixtures/resume_sample.txt --dry-run
  ```
- Local sync from the configured source:
  ```bash
  RESUME_SOURCE_URL="https://docs.google.com/document/d/YOUR_FILE_ID/edit" uv run python scripts/sync_resume_content.py
  ```
- `RESUME_URL` is still the public resume download link. `RESUME_SOURCE_URL` is the editable source used to refresh site and chat content.

### Email + Contact
- POST `/contact` sends email via SMTP and on success redirects to `/contact?sent=1`.
- If SMTP is not configured or fails in local/non-serverless environments, messages are saved to `data/messages/` and the page redirects to `/contact?saved=1`.
- On Vercel, SMTP failures return an error instead of writing messages to ephemeral `/tmp` storage.
- Anti‑spam: honeypot + min submit time + self-hosted image CAPTCHA + per‑IP/hour and daily global rate‑limits.

### Experience Chat
- The assistant is available from every page through the desktop floating widget, mobile Chat tab, and full-page experience at `/chat`.
- Chat history is stored in browser `sessionStorage`, so it carries across pages for the same visitor and tab/session only. It is not stored server-side and is not visible to other visitors.
- Retrieval is local and free: the app ranks committed portfolio/experience data for each question, including recent user turns for follow-up context.
- Responses show the answer path and source labels so visitors can tell whether the answer came from local retrieval or optional AI polishing.
- `HUGGINGFACE_API_KEY` is optional. When configured, a small Hugging Face model can polish responses; if it is missing, rate-limited, or out of free usage, the local retrieved answer is still returned.

### Development Checks
- Install Git hooks with `uv run pre-commit install`.
- Hooks run Ruff formatting and Ruff lint fixes.
- GitHub Actions runs formatting, linting, and tests.
- Vercel installs Python dependencies from the committed `pyproject.toml` and `uv.lock`.
- Visual/UX-heavy PRs should also follow `docs/ux-verification.md` for desktop and mobile screenshot checks.

### Vercel Environment Variables
- Push selected values from `envs.sh` with `./scripts/push-vercel-envs production`.
- Use `preview` or `development` as the first argument for those Vercel environments.
- The script marks token/password/secret/key variables as sensitive and overwrites existing values.
- The repo must be linked first with `vercel link` so the CLI knows which Vercel project to update.

### Agent Instructions
- `AGENTS.md` is the single source of truth for coding-agent behavior.
- `CLAUDE.md`, `.claude`, `.cline/skills`, and `.cline/rules/AGENTS.md` point back to the same shared instructions and skill scaffold.
- Future reusable local skills should live under `.codex/skills/`.

## 📊 Performance Features

- **Server-Side Rendering**: Fast initial page loads
- **Component Caching**: Efficient re-rendering
- **Lazy Loading**: Optimized resource loading
- **Responsive Images**: Optimized for different screen sizes
- **Interactive chart**: Tech‑stack snapshot with Bytes/Repos and Donut/Bar/Treemap views; PNG export.
- **Starfield background**: Lightweight, respects reduced‑motion.

## 🔒 Security

- Environment variable protection for sensitive data
- Input validation and sanitization
- CSRF protection via FastHTML
- Secure headers implementation
- Contact-form abuse protections: honeypot, minimum submit time, CAPTCHA, and server-side rate limits.
- Vercel environment values containing tokens, passwords, secrets, or keys should be marked sensitive.
- After vendor security notices, rotate provider tokens and Vercel environment variables, then review the Vercel activity log and recent deployments.

## 🚀 Deployment

### Local Development
```bash
./app.sh
```

### Production Deployment
- Vercel is the primary hosting target for this repo.
- Vercel builds from the Git branch, installs dependencies from `pyproject.toml`/`uv.lock`, and routes requests through `api/index.py`.
- Classic container hosting is still possible with `uvicorn src.main:app --host 0.0.0.0 --port 8000` behind a process manager or reverse proxy.

### Dev Container
- Open in VS Code Dev Containers (or Codespaces) — `.devcontainer` is configured.
- Defaults:
  - Base: Python 3.12 (non‑root `vscode` user)
  - uv installed and `uv sync` runs post‑create
  - Forwards port 8000 for the FastHTML app
- Run the app inside the container:
  ```bash
  uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
  ```

## 🤝 Contributing

This is a professional portfolio project, but feel free to:
1. Fork the repository
2. Customize for your own use
3. Suggest improvements via issues
4. Share your own FastHTML portfolio implementations

## 📄 License

This project is open source. Feel free to use it as a template for your own professional portfolio.

## 🙏 Acknowledgments

- Built with [FastHTML](https://fasthtml.io/) by Jeremy Howard
- Professional design inspired by modern technical portfolios
- GitHub API integration for real-time project data
- UV package management for modern Python development

---

**Created with ❤️ using FastHTML - showcasing the power of Python web development**

## 🧩 Modularization (Updated)

- `src/components/ui.py`: Navigation, hero, and footer components
- `src/services/github.py`: Async GitHub API calls (profile, repos with pagination)
- `src/utils/render.py`: `render_page` helper to apply app-level headers/styles
- `src/services/email.py`: SMTP email sender (Reply‑To set to visitor)

## 📄 Resume Link (External)

- Set `RESUME_URL` in `envs.sh` to point to a hosted PDF.
- For Google Docs, prefer the PDF export link: `https://docs.google.com/document/d/YOUR_FILE_ID/export?format=pdf`.
- Note: Most browsers ignore the HTML `download` attribute for cross-origin links; you can’t force download from Drive. If you need guaranteed downloads, host on S3/CloudFront with `Content-Disposition: attachment`.

## 📦 Static Fallback

- The app serves `/static` from `data/static` by default. Override with `STATIC_DIR`.
- Place an optional fallback file at `data/static/resume.pdf` (kept out of Git).

## 🧪 Contact Form Testing
- Use any email as the sender (e.g., `jane@example.com`). The email arrives From your SMTP_FROM address with Reply‑To set to the sender.
- Success banner: `/contact?sent=1`; local persistence banner: `/contact?saved=1`.

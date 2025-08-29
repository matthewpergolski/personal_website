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

- **Framework**: FastHTML (Python web framework)
- **Language**: Python 3.12+
- **Styling**: CSS-in-Python with FastHTML's built-in styling system
- **Dependencies**: python-fasthtml, httpx, python-dotenv
  - Optional: SMTP (email), Turnstile/hCaptcha (bot protection)
- **Package Management**: UV (modern Python dependency management)

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
├── src/
│   ├── __init__.py          # Package initialization
│   └── main.py             # Main FastHTML application
├── components/             # Reusable UI components (future use)
├── pages/                  # Page-specific modules (future use)
├── data/                   # Static data and configuration (future use)
├── memory-bank/            # Project documentation
│   ├── projectbrief.md     # Project requirements
│   ├── productContext.md   # Why this project exists
│   ├── techContext.md      # Technology decisions
│   ├── systemPatterns.md   # Architecture patterns
│   ├── activeContext.md    # Current work focus
│   └── progress.md         # Project progress
├── app.sh                  # Application launcher script
├── envs.sh                 # Environment variables (configure this)
├── envs.sh.example         # Environment template
├── pyproject.toml          # UV project configuration
├── uv.lock                 # Dependency lock file
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
export SITE_TITLE="Your Name - Professional Title"
export SITE_DESCRIPTION="Brief professional description"

# Resume (external link preferred)
# For Google Docs: https://docs.google.com/document/d/YOUR_FILE_ID/export?format=pdf
export RESUME_URL="https://docs.google.com/document/d/YOUR_FILE_ID/export?format=pdf"

# SMTP (contact form)
# Gmail example (use App Password):
# export SMTP_HOST=smtp.gmail.com
# export SMTP_PORT=587
# export SMTP_TLS=true
# export SMTP_USER=your_gmail@gmail.com
# export SMTP_PASSWORD=your_16_char_app_password
# export SMTP_FROM=your_gmail@gmail.com
# export SMTP_TO=your_hide_my_email@icloud.com   # or your inbox

# Optional bot protection (Turnstile preferred)
# export TURNSTILE_SITE_KEY="1x00000000000000000000AA"   # test key
# export TURNSTILE_SECRET_KEY="1x0000000000000000000000000000000AA"  # test secret
# hCaptcha alternative:
# export HCAPTCHA_SITE_KEY="10000000-ffff-ffff-ffff-000000000001"
# export HCAPTCHA_SECRET="0x0000000000000000000000000000000000000000"

# Rate limits (server-side safeguards)
export RATE_IP_PER_HOUR=3
export RATE_GLOBAL_PER_DAY=50
```

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

### Email + Contact
- POST `/contact` sends email via SMTP and on success redirects to `/contact?sent=1`.
- If SMTP is not configured or fails, messages are saved to `data/messages/` and the page redirects to `/contact?saved=1`.
- Anti‑spam: honeypot + min submit time + per‑IP/hour and daily global rate‑limits; optional Turnstile/hCaptcha verification if keys are present.

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

## 🚀 Deployment

### Local Development
```bash
./app.sh
```

### Production Deployment
- Recommended (long‑running Python app): Fly.io, Railway, Render, or Cloud Run.
- Vercel note: Python on Vercel runs as serverless functions; to use Vercel, you’d adapt the app to their Python runtime (not covered here). Docker deploys on Vercel are ephemeral and must listen on `$PORT`.
- Classic container: run with `uvicorn src.main:app --host 0.0.0.0 --port 8000` behind a process manager or reverse proxy.

### Dev Container
- Open in VS Code Dev Containers (or Codespaces) — `.devcontainer` is configured.
- Defaults:
  - Base: Python 3.12 (non‑root `vscode` user)
  - uv installed and `uv sync` runs post‑create
  - Forwards ports 8000 (app) and 11434 (optional Ollama)
- Optional LLM (future chat): set build arg `OLLAMA=1` to install Ollama and pull `llama3.2:3b`. The start script will run the server if available.
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

# Personal Website - Matthew Pergolski

A professional portfolio website built with Flask, featuring GitHub repository integration, skills visualization, and a future RAG-powered chatbot.

## Local Development

### Setup

1. Ensure you have Python 3.12+ installed
2. Clone this repository
3. Set up your environment:

```bash
# Using uv (recommended)
uv init
uv add -r requirements.txt

# OR using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:

```
mlp_github_token=your_github_personal_access_token
```

### Running Locally

```bash
# Using the script (recommended)
chmod +x scripts/start_local.sh
./scripts/start_local.sh

# OR manually
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

Visit http://localhost:5002 in your browser.

## Deployment on Render

This application is configured for easy deployment on Render.

### Manual Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
4. Add the following environment variables:
   - `FLASK_ENV`: production
   - `mlp_github_token`: Your GitHub Personal Access Token

### Automatic Deployment with Blueprint

If you have forked this repository, you can use Render Blueprints for one-click deployment:

1. Push all changes to your GitHub repository
2. Go to the Render Dashboard → Blueprints
3. Click "New Blueprint Instance"
4. Connect your repository
5. Render will automatically deploy using the `render.yaml` configuration

## Project Structure

```
personal_website/
├── app/                     # Application package
│   ├── __init__.py          # App factory function
│   ├── routes.py            # Routes/views
│   ├── templates/           # HTML templates
│   ├── static/              # Static assets
│   ├── github_api.py        # GitHub API functions
│   └── resume_utils.py      # Resume processing utilities
├── scripts/                 # Utility scripts
├── app.py                   # Application entry point
├── wsgi.py                  # WSGI entry point for production
├── gunicorn_config.py       # Gunicorn configuration
├── requirements.txt         # Dependencies
├── render.yaml              # Render Blueprint configuration
└── Procfile                 # Process definition for Render
```

## License

Copyright (c) 2024 Matthew Pergolski. All rights reserved.
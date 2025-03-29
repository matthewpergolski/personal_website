# Personal Website with GitHub Highlights

A modern personal website that showcases your GitHub profile, repositories, and contributions with an interactive and responsive design. This project is built with Flask and uses the GitHub API to automatically display your profile information, repositories, and other GitHub activity.

## Features

- **Profile Section**: Displays your GitHub profile information, including bio, followers, and repositories.
- **GitHub Highlights**: Shows your repositories with details like stars, forks, and languages used.
- **Responsive Design**: Looks great on desktop, tablet, and mobile devices.
- **Interactive Elements**: Smooth animations and transitions for enhanced user experience.

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**:
  - HTML for structure
  - Tailwind CSS for styling
  - JavaScript for interactivity
  - AOS (Animate On Scroll) for animations
- **APIs**: GitHub API for fetching profile and repository data

## Getting Started

### Prerequisites

- Python 3.12 or higher
- uv (Python package manager)
- GitHub personal access token

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal-website.git
   cd personal-website
   ```

2. Set up the environment:
   ```bash
   uv init --python 3.12
   ```

3. Install dependencies:
   ```bash
   uv add flask pytest python-dotenv requests pytest-mock
   ```

4. Create a `.env` file in the project root and add your GitHub token:
   ```
   mlp_github_token=your_github_token_value_here
   ```

### Running the Application Locally

1. Start the development server:
   ```bash
   uv run python main.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. You should see your GitHub profile information and repositories displayed on the site.

### Running Tests

Run the test suite using pytest:
```bash
uv run pytest
```

## Deployment Options

### Heroku Deployment

1. Create a Heroku account at [heroku.com](https://www.heroku.com/)
2. Install the Heroku CLI: `brew install heroku/brew/heroku`
3. Login to Heroku: `heroku login`
4. Create a new Heroku app: `heroku create your-app-name`
5. Add a Procfile to the project root:
   ```
   web: gunicorn main:app
   ```
6. Add gunicorn to your dependencies: `uv add gunicorn`
7. Configure environment variables:
   ```bash
   heroku config:set mlp_github_token=your_github_token_value_here
   ```
8. Deploy to Heroku:
   ```bash
   git push heroku main
   ```
9. Open your app: `heroku open`

### Vercel Deployment

1. Create a Vercel account at [vercel.com](https://vercel.com/)
2. Install Vercel CLI: `npm install -g vercel`
3. Create a `vercel.json` file in the project root:
   ```json
   {
     "version": 2,
     "builds": [
       { "src": "main.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/(.*)", "dest": "main.py" }
     ]
   }
   ```
4. Set up environment variables in the Vercel dashboard
5. Deploy to Vercel: `vercel --prod`

## Project Structure

```
personal_website/
├── app/                   # Application package
│   ├── __init__.py        # Flask app initialization
│   ├── routes.py          # Route definitions
│   ├── github_api.py      # GitHub API integration
│   ├── static/            # Static files (CSS, JS, images)
│   └── templates/         # HTML templates
├── tests/                 # Test directory
│   ├── test_routes.py     # Tests for routes
│   └── test_github_api.py # Tests for GitHub API integration
├── pyproject.toml         # Project dependencies and metadata
├── main.py                # Application entry point
├── .env                   # Environment variables (GitHub token)
└── README.md              # Project documentation 
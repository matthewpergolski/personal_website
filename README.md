# Personal Website with GitHub Highlights

A modern personal website that showcases my GitHub profile, repositories, and contributions with an interactive and responsive design. This project is built with Flask and uses the GitHub API to automatically display my profile information, repositories, and other GitHub activity.

## Features

- **Profile Section**: Displays my GitHub profile information, including bio, followers, and repositories.
- **GitHub Highlights**: Shows my repositories with details like stars, forks, and languages used.
- **Interactive Resume**: YAML-driven interactive resume with skills visualization and timeline.
- **AI Chatbot**: An interactive chatbot that helps visitors navigate and learn about my portfolio.
  - Expandable chat interface with a Claude-like full-screen experience
  - Dark mode support for all elements including the chatbot
  - Quick-access suggestion buttons for common questions
- **Responsive Design**: Looks great on desktop, tablet, and mobile devices.
- **Interactive Elements**: Smooth animations and transitions for enhanced user experience.
- **Dark/Light Mode**: Toggle between dark and light themes with persistent preference.

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**:
  - HTML for structure
  - Tailwind CSS for styling
  - JavaScript for interactivity
  - AOS (Animate On Scroll) for animations
  - Chart.js for data visualization
- **Data Management**: 
  - YAML for structured content management
  - PDF parsing for resume data extraction
  - Response caching for API efficiency
- **APIs**: GitHub API for fetching profile and repository data

## Getting Started

### Prerequisites

- Python 3.12 or higher
- uv (Python package manager)
- GitHub personal access token

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/matthewpergolski/personal-website.git
   cd personal-website
   ```

2. Set up the environment:
   ```bash
   uv init --python 3.12
   ```

3. Install dependencies using uv sync:
   ```bash
   # Add dependencies to pyproject.toml
   uv add flask pytest python-dotenv requests pytest-mock pyyaml pypdf responses
   
   # Or sync from existing pyproject.toml
   uv sync
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

2. Open your browser and navigate to `http://localhost:5001`

3. You should see my GitHub profile information and repositories displayed on the site.

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
4. Create a new Heroku app: `heroku create my-app-name`
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
9. Open my app: `heroku open`

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
│   ├── resume_utils.py    # Resume data loading and processing
│   ├── cache/             # API response cache storage
│   │   └── resume_data.yaml # Resume content
│   ├── static/            # Static files (CSS, JS, images)
│   │   └── js/            # JavaScript files
│   │       ├── resume.js  # Resume interactive features
│   │       └── chatbot.js # Chatbot functionality
│   └── templates/         # HTML templates
├── tests/                 # Test directory
│   ├── test_routes.py     # Tests for routes
│   ├── test_github_api.py # Tests for GitHub API integration
│   └── test_resume_utils.py # Tests for resume utilities
├── test_github_api.py     # Additional API tests
├── pyproject.toml         # Project dependencies and metadata
├── uv.lock                # Lock file for dependencies
├── main.py                # Application entry point
├── setup.sh               # Setup script for environment
├── .env                   # Environment variables (GitHub token)
├── .env.example           # Example environment file
└── README.md              # Project documentation 
```

## Resume Data Management

The website uses a YAML-based approach for managing resume data:

1. Structure my resume information in `app/data/resume_data.yaml`
2. The data follows this general structure:
   ```yaml
   personal_info:
     name: "Matthew Pergolski"
     title: "Professional Title"
     # other personal details
   
   education:
     - institution: "University Name"
       degree: "Degree Title"
       # other education details
   
   experience:
     - company: "Company Name"
       position: "Position"
       # other job details
   
   skills:
     technical:
       - name: "Skill Name"
         level: 85  # Percentage of proficiency
   ```

3. To extract data from my PDF resume, use the `extract_pdf_text()` utility in `resume_utils.py`:
   ```python
   from app.resume_utils import extract_pdf_text
   
   text = extract_pdf_text('path/to/my/resume.pdf')
   # Then parse the text into the appropriate YAML structure
   ```

## Future Plans

### RAG Integration for Enhanced Chatbot

Future versions will include a Retrieval-Augmented Generation (RAG) capability to make the chatbot more intelligent:

1. **Document Indexing**:
   - Index all of my GitHub repositories, README files, and documentation
   - Create embeddings of resume content for semantic search
   - Store project descriptions and technical details in a vector database

2. **Query Processing**:
   - Implement semantic search to find relevant information based on user queries
   - Retrieve context from the vector database to answer specific questions
   - Combine retrieved information with LLM capabilities for coherent responses

3. **User Experience**:
   - Enable the chatbot to answer specific questions about projects, skills, and experience
   - Allow users to ask technical questions about repository code
   - Provide detailed information about project implementations and technologies used

### Resume Data Extraction Process

To streamline the resume data management, a future enhancement will include:

1. **Automated Data Extraction**:
   - Enhanced PDF parsing with section recognition using ML/NLP techniques
   - Automatic categorization of resume sections (education, experience, skills)
   - Extraction of key information like dates, titles, and descriptions

2. **YAML Generation**:
   - Conversion of extracted information into properly formatted YAML
   - Validation of structure against a schema
   - Diffing with existing YAML to show changes

3. **Two-way Synchronization**:
   - Generate PDF resume from YAML data (single source of truth)
   - Update YAML when PDF changes (for compatibility with traditional resume workflows)
   - Web interface for editing resume data directly

## Advanced Features

### GitHub API Caching

The website implements an efficient caching mechanism for GitHub API calls:

- **Cache Duration**: API responses are cached for 1 hour by default
- **Cache Storage**: JSON files stored in the `app/cache/` directory
- **Automatic Refresh**: Cache automatically refreshes when expired
- **Language Aggregation**: Language data is aggregated across repositories
- **Performance**: Reduces API calls and improves page load times
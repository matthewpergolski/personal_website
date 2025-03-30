from flask import Blueprint, render_template, send_from_directory, current_app
from app.github_api import get_user_profile, get_repositories, get_visualization_data
from app.resume_utils import get_resume_data
import os
import datetime
import logging  # Add logging import

# Create a blueprint without specific URL prefix since routes will be added at the app level
bp = Blueprint('main', __name__, url_prefix=None)

@bp.route('/')
def index():
    """Render the homepage with GitHub user profile and language statistics."""
    user_profile = get_user_profile()
    viz_data = get_visualization_data()
    now = datetime.datetime.now()
    return render_template('index.html', profile=user_profile, viz_data=viz_data, now=now)

@bp.route('/projects')
def projects():
    """Render the projects page with GitHub repositories."""
    # Get user profile to obtain GitHub username for "view all" link
    user_profile = get_user_profile()
    
    # Use os.environ to bypass any environment variable caching
    import requests
    import json
    from dotenv import load_dotenv
    
    # Reload environment variables - remove the force parameter
    load_dotenv(override=True)  # Use override instead of force
    
    # Direct API call to GitHub to get repositories
    github_token = os.environ.get("mlp_github_token")
    headers = {
        "Authorization": f"token {github_token}" if github_token else None,
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Direct API call without using the caching function
        current_app.logger.info("Making direct API call to GitHub")
        response = requests.get(
            "https://api.github.com/user/repos",
            headers=headers,
            params={
                "sort": "updated", 
                "per_page": 100,
                "visibility": "all",
                "affiliation": "owner,collaborator,organization_member"
            }
        )
        
        if response.status_code == 200:
            repos = response.json()
            current_app.logger.info(f"Retrieved {len(repos)} repositories directly from GitHub API")
            
            # Enhance repositories with language data
            for repo in repos:
                languages_url = repo["languages_url"]
                languages_response = requests.get(languages_url, headers=headers)
                if languages_response.status_code == 200:
                    repo["languages"] = languages_response.json()
        else:
            current_app.logger.error(f"GitHub API error: {response.status_code}")
            # Fall back to cached method if direct call fails
            repos = get_repositories(per_page=100, force_refresh=True)
    except Exception as e:
        current_app.logger.error(f"Error retrieving repositories: {str(e)}")
        # Fall back to cached method if direct call fails
        repos = get_repositories(per_page=100, force_refresh=True)
    
    return render_template('projects.html', 
                          repositories=repos, 
                          profile=user_profile)

@bp.route('/about')
def about():
    """Render the about page with education and certification data."""
    resume_data = get_resume_data()
    return render_template('about.html', resume_data=resume_data)

@bp.route('/resume')
def resume():
    """Render the interactive resume page."""
    resume_data = get_resume_data()
    return render_template('resume.html', resume_data=resume_data)

@bp.route('/download-resume')
def download_resume():
    """Download the resume PDF."""
    # The directory where your PDF is stored
    # You'll need to place your actual PDF resume in this directory
    resume_dir = os.path.join(bp.root_path, 'static', 'files')
    return send_from_directory(
        directory=resume_dir,
        path='resume.pdf',
        as_attachment=True,
        download_name='Matthew_Pergolski_Resume.pdf'
    ) 
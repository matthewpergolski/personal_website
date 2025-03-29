from flask import Blueprint, render_template, send_from_directory
from app.github_api import get_user_profile, get_repositories, get_visualization_data
import os

# Create a blueprint without specific URL prefix since routes will be added at the app level
bp = Blueprint('main', __name__, url_prefix=None)

@bp.route('/')
def index():
    """Render the homepage with GitHub user profile."""
    user_profile = get_user_profile()
    return render_template('index.html', profile=user_profile)

@bp.route('/projects')
def projects():
    """Render the projects page with GitHub repositories."""
    repos = get_repositories()
    return render_template('projects.html', repositories=repos)

@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@bp.route('/dashboard')
def dashboard():
    """Render the data science dashboard page."""
    user_profile = get_user_profile()
    repos = get_repositories()
    viz_data = get_visualization_data()
    return render_template('dashboard.html', profile=user_profile, repositories=repos, viz_data=viz_data)

@bp.route('/resume')
def resume():
    """Render the interactive resume page."""
    return render_template('resume.html')

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
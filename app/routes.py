from flask import Blueprint, render_template
from app.github_api import get_user_profile, get_repositories

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
    return render_template('dashboard.html', profile=user_profile, repositories=repos) 
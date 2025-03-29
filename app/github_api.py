import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"

# Get GitHub access token from environment variables
GITHUB_TOKEN = os.getenv("mlp_github_token")

# Set up headers for GitHub API requests
headers = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None,
    "Accept": "application/vnd.github.v3+json"
}

def get_user_profile():
    """Fetch authenticated GitHub user profile information."""
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # When using a token, we can use /user endpoint to get the authenticated user's info
        response = requests.get(
            f"{GITHUB_API_URL}/user", 
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch user profile: {str(e)}"}

def get_repositories(sort="updated", per_page=10):
    """Fetch authenticated user's GitHub repositories.
    
    Args:
        sort (str): How to sort repositories ('created', 'updated', 'pushed', 'full_name')
        per_page (int): Number of repositories to return per page
        
    Returns:
        dict: Repository data or error message
    """
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # Get authenticated user's repositories
        response = requests.get(
            f"{GITHUB_API_URL}/user/repos",
            headers=headers,
            params={"sort": sort, "per_page": per_page}
        )
        response.raise_for_status()
        
        repos = response.json()
        
        # Add additional data for each repo like languages used
        for repo in repos:
            # Fetch languages for the repository
            languages_url = repo["languages_url"]
            languages_response = requests.get(languages_url, headers=headers)
            if languages_response.status_code == 200:
                repo["languages"] = languages_response.json()
                
        return repos
    except requests.RequestException as e:
        return {"error": f"Failed to fetch repositories: {str(e)}"}

def get_visualization_data():
    """Return sample data for visualizations when actual GitHub data is not available.
    
    This function provides consistent sample data for the dashboard visualizations
    when the user hasn't configured GitHub authentication or for demo purposes.
    
    Returns:
        dict: Sample visualization data for charts and graphs
    """
    return {
        "language_distribution": {
            "Python": 45,
            "JavaScript": 20,
            "R": 15,
            "SQL": 10,
            "Java": 5,
            "Other": 5
        },
        "contributions": {
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "values": [12, 19, 25, 32, 28, 24, 18, 27, 39, 45, 38, 30]
        },
        "repository_sizes": {
            "names": ["Data Analysis", "ML Project", "NLP Research", "Visualization", "Web App"],
            "code_size": [350, 520, 280, 190, 430],
            "commits": [45, 65, 30, 25, 50]
        },
        "stars_timeline": {
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "cumulative": [5, 12, 20, 25, 35, 45, 55, 70, 85, 100, 120, 145]
        },
        "ml_models": {
            "metrics": ["Accuracy", "Precision", "Recall", "F1 Score", "Training Speed", "Inference Speed"],
            "models": {
                "Random Forest": [85, 82, 80, 81, 70, 90],
                "Neural Network": [90, 87, 85, 86, 60, 75],
                "Gradient Boosting": [88, 90, 83, 87, 75, 82]
            }
        },
        "is_sample_data": True
    } 
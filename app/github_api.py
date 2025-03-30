import os
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import Counter
import logging

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

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
CACHE_EXPIRY = 3600  # Cache expiry in seconds (1 hour)

# Set up cache directory if it doesn't exist
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def _get_cache_path(cache_key):
    """Get the file path for a cache entry."""
    return os.path.join(CACHE_DIR, f"{cache_key}.json")

def _read_from_cache(cache_key):
    """Read data from cache if it exists and is not expired."""
    cache_path = _get_cache_path(cache_key)
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data['timestamp'] < CACHE_EXPIRY:
                print(f"[DEBUG] Using cached data for {cache_key}")
                return cache_data['data']
            else:
                print(f"[DEBUG] Cache expired for {cache_key}")
        except Exception as e:
            print(f"[DEBUG] Error reading cache: {str(e)}")
    
    return None

def _write_to_cache(cache_key, data):
    """Write data to cache with current timestamp."""
    cache_path = _get_cache_path(cache_key)
    
    try:
        with open(cache_path, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'data': data
            }, f)
        print(f"[DEBUG] Cached data for {cache_key}")
    except Exception as e:
        print(f"[DEBUG] Error writing to cache: {str(e)}")

def get_user_profile():
    """Fetch authenticated GitHub user profile information with caching."""
    cache_key = "user_profile"
    
    # Try to get from cache first
    cached_data = _read_from_cache(cache_key)
    if cached_data:
        return cached_data
    
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        # When using a token, we can use /user endpoint to get the authenticated user's info
        response = requests.get(
            f"{GITHUB_API_URL}/user", 
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        # Cache the result
        _write_to_cache(cache_key, result)
        
        return result
    except requests.RequestException as e:
        return {"error": f"Failed to fetch user profile: {str(e)}"}

def get_repositories(sort="updated", per_page=10, force_refresh=False):
    """Fetch authenticated user's GitHub repositories with caching.
    
    Args:
        sort (str): How to sort repositories ('created', 'updated', 'pushed', 'full_name')
        per_page (int): Number of repositories to return per page
        force_refresh (bool): Whether to bypass the cache and fetch fresh data
        
    Returns:
        dict: Repository data or error message
    """
    # Always force refresh by default for repositories
    force_refresh = True
    
    cache_key = f"repositories_{sort}_{per_page}"
    
    # Delete any existing cache for repositories
    cache_path = _get_cache_path(cache_key)
    if os.path.exists(cache_path):
        print(f"[DEBUG] Deleting existing cache at {cache_path}")
        try:
            os.remove(cache_path)
        except Exception as e:
            print(f"[DEBUG] Error deleting cache: {str(e)}")
    
    # Try to get from cache first (unless force_refresh is True)
    if not force_refresh:
        cached_data = _read_from_cache(cache_key)
        if cached_data:
            print(f"[DEBUG] Using cached data with {len(cached_data)} repositories")
            return cached_data
    
    if not GITHUB_TOKEN:
        return {"error": "GitHub token not configured"}
    
    try:
        print(f"[DEBUG] Fetching {per_page} repositories sorted by {sort}")
        # Get authenticated user's repositories
        # Explicitly including visibility=all parameter to get all repositories
        response = requests.get(
            f"{GITHUB_API_URL}/user/repos",
            headers=headers,
            params={
                "sort": sort, 
                "per_page": per_page,
                "visibility": "all",
                "affiliation": "owner,collaborator,organization_member"
            }
        )
        response.raise_for_status()
        
        repos = response.json()
        print(f"[DEBUG] Retrieved {len(repos)} repositories from GitHub API")
        
        # Add additional data for each repo like languages used
        for repo in repos:
            # Fetch languages for the repository
            languages_url = repo["languages_url"]
            languages_response = requests.get(languages_url, headers=headers)
            if languages_response.status_code == 200:
                repo["languages"] = languages_response.json()
        
        # Cache the result
        _write_to_cache(cache_key, repos)
        
        return repos
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch repositories: {str(e)}")
        return {"error": f"Failed to fetch repositories: {str(e)}"}

def get_language_distribution(limit=8, return_bytes=False):
    """Fetch language distribution across all user repositories with caching.
    
    This function aggregates language data across all repositories and returns
    the distribution as percentages. Languages less common than the top 'limit'
    are grouped into 'Other'.
    
    Args:
        limit (int): Number of top languages to show individually
        return_bytes (bool): Whether to return total bytes and raw language data
        
    Returns:
        dict or tuple: Language distribution data or tuple with distribution, raw data, and total bytes
    """
    cache_key = f"language_distribution_{limit}"
    
    # Try to get from cache first
    cached_data = _read_from_cache(cache_key)
    if cached_data and not return_bytes:
        return cached_data
    
    if not GITHUB_TOKEN:
        print("[DEBUG] No GitHub token found, using sample data")
        # Return sample data if token is not available
        return get_visualization_data()["language_distribution"]
    
    try:
        print(f"[DEBUG] Fetching repositories with token: {GITHUB_TOKEN[:4]}...")
        # Get all user repositories (up to 100)
        response = requests.get(
            f"{GITHUB_API_URL}/user/repos",
            headers=headers,
            params={"per_page": 100}
        )
        response.raise_for_status()
        repos = response.json()
        print(f"[DEBUG] Found {len(repos)} repositories")
        
        # Collect language bytes from all repositories
        all_languages = Counter()
        for repo in repos:
            print(f"[DEBUG] Processing repo: {repo['name']}")
            # Fetch languages for the repository
            languages_url = repo["languages_url"]
            languages_response = requests.get(languages_url, headers=headers)
            if languages_response.status_code == 200:
                repo_languages = languages_response.json()
                print(f"[DEBUG] Languages in {repo['name']}: {repo_languages}")
                
                # Combine Jupyter Notebook and Python
                if 'Jupyter Notebook' in repo_languages:
                    jupyter_bytes = repo_languages['Jupyter Notebook']
                    # Transfer 80% of Jupyter Notebook bytes to Python
                    python_equivalent = int(jupyter_bytes * 0.8)
                    
                    # Add the Python equivalent to existing Python bytes or create a new entry
                    if 'Python' in repo_languages:
                        repo_languages['Python'] += python_equivalent
                    else:
                        repo_languages['Python'] = python_equivalent
                    
                    # Leave 20% as Jupyter Notebook to represent the actual notebook format
                    repo_languages['Jupyter Notebook'] = jupyter_bytes - python_equivalent
                    
                all_languages.update(repo_languages)
        
        # If no languages were found, return sample data
        if not all_languages:
            print("[DEBUG] No languages found in repositories, using sample data")
            return get_visualization_data()["language_distribution"]
            
        # Calculate total bytes
        total_bytes = sum(all_languages.values())
        print(f"[DEBUG] Total bytes across all repos: {total_bytes}")
        
        # Sort languages by byte count
        sorted_languages = all_languages.most_common(limit)
        print(f"[DEBUG] Top languages: {sorted_languages}")
        
        # Calculate percentages for top languages with one decimal place for small values
        language_distribution = {}
        
        for lang, bytes_count in sorted_languages:
            percentage = (bytes_count / total_bytes) * 100
            # For small percentages (< 1%), use one decimal place
            if percentage < 1:
                percentage = round(percentage, 1)
                # Ensure it's at least 0.1%
                if percentage == 0 and bytes_count > 0:
                    percentage = 0.1
            else:
                percentage = round(percentage)
            language_distribution[lang] = percentage
        
        # Add "Other" category for remaining languages
        remaining_languages = dict(all_languages.most_common()[limit:])
        other_bytes = sum(remaining_languages.values())
        if other_bytes > 0:
            other_percentage = (other_bytes / total_bytes) * 100
            if other_percentage < 1:
                other_percentage = round(other_percentage, 1)
                if other_percentage == 0:
                    other_percentage = 0.1
            else:
                other_percentage = round(other_percentage)
            
            if other_percentage > 0:
                language_distribution["Other"] = other_percentage
        
        # Ensure percentages are close to 100% (might not add up exactly due to rounding)
        print(f"[DEBUG] Final language distribution: {language_distribution}")
        
        # Cache the result
        _write_to_cache(cache_key, language_distribution)
        
        if return_bytes:
            return language_distribution, dict(all_languages), total_bytes
        return language_distribution
    except requests.RequestException as e:
        print(f"[DEBUG] API request error: {str(e)}")
        # Return sample data if API request fails
        if return_bytes:
            sample_data = get_visualization_data()["language_distribution"]
            return sample_data, {}, 50000000
        return get_visualization_data()["language_distribution"]

def get_visualization_data():
    """Return visualization data for dashboard charts.
    
    If GitHub authentication is configured, this function will fetch real
    language distribution data. Otherwise, it provides sample data.
    
    Returns:
        dict: Visualization data for charts and graphs
    """
    # Get language distribution data
    all_languages, language_distribution, total_bytes = {}, {}, 0
    
    if GITHUB_TOKEN:
        # Get cached language data and total bytes if available
        cache_key = "language_distribution_8"
        language_data = _read_from_cache(cache_key)
        if language_data:
            language_distribution = language_data
            total_bytes = _read_from_cache("total_bytes") or 50000000
        else:
            # Calculate them from API
            language_distribution, all_languages, total_bytes = get_language_distribution(return_bytes=True)
            # Cache total bytes
            _write_to_cache("total_bytes", total_bytes)
    else:
        # Sample data
        language_distribution = {
            "Python": 45,
            "JavaScript": 20,
            "R": 15, 
            "SQL": 10,
            "Java": 5,
            "Other": 5
        }
        total_bytes = 50000000  # 50MB sample
    
    # Determine if using sample data
    is_sample_data = not GITHUB_TOKEN
    
    return {
        "language_distribution": language_distribution,
        "total_bytes": total_bytes,
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
        "is_sample_data": is_sample_data
    } 
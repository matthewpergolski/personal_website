"""
Test script to verify GitHub API connection and language distribution data.
"""
import os
import sys
from dotenv import load_dotenv
from app.github_api import get_user_profile, get_repositories, get_language_distribution

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if GitHub token is configured
    token = os.getenv("mlp_github_token")
    if not token:
        print("ERROR: GitHub token not found. Please set mlp_github_token in .env file.")
        print("Example: mlp_github_token=ghp_YOUR_TOKEN_HERE")
        sys.exit(1)
    
    print(f"Found GitHub token: {token[:4]}...")
    
    # Test user profile
    print("\n--- Testing User Profile ---")
    profile = get_user_profile()
    if 'error' in profile:
        print(f"ERROR: {profile['error']}")
    else:
        print(f"Successfully connected to GitHub as: {profile.get('login', 'Unknown')}")
        print(f"Name: {profile.get('name', 'Not provided')}")
        print(f"Repos: {profile.get('public_repos', 0)} public, {profile.get('owned_private_repos', 0)} private")
    
    # Test repositories
    print("\n--- Testing Repositories ---")
    repos = get_repositories(per_page=5)
    if isinstance(repos, dict) and 'error' in repos:
        print(f"ERROR: {repos['error']}")
    else:
        print(f"Successfully retrieved {len(repos)} repositories:")
        for repo in repos:
            print(f"- {repo['name']} ({repo['language'] or 'No primary language'})")
    
    # Test language distribution
    print("\n--- Testing Language Distribution ---")
    languages = get_language_distribution()
    print("\nLanguage Distribution:")
    for lang, percentage in languages.items():
        print(f"- {lang}: {percentage}%")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main() 
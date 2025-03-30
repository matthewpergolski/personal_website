#!/usr/bin/env python3
"""
Direct GitHub API Test Script

This script directly fetches repositories from GitHub API without any caching.
Run this from the command line to check how many repositories are returned.
"""

import os
import requests
import json
from dotenv import load_dotenv

def fetch_repositories_directly():
    """Fetch repositories directly from GitHub API"""
    # Load environment variables
    load_dotenv(override=True)
    
    # Get GitHub token
    github_token = os.getenv("mlp_github_token")
    if not github_token:
        print("ERROR: GitHub token not found in environment variables")
        return
    
    print(f"Using token: {github_token[:4]}...")
    
    # Define headers
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Make direct API call to GitHub
    try:
        print("Making direct API call to GitHub...")
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
        
        # Check response status
        if response.status_code == 200:
            repos = response.json()
            print(f"SUCCESS: Retrieved {len(repos)} repositories directly from GitHub API")
            
            # Print repository names
            for i, repo in enumerate(repos, 1):
                print(f"{i}. {repo['name']} ({repo['html_url']})")
                
            return repos
        else:
            print(f"ERROR: GitHub API responded with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: Exception occurred while fetching repositories: {str(e)}")
        return None

if __name__ == "__main__":
    # Run the script directly
    fetch_repositories_directly() 
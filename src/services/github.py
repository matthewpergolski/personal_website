import os
import time
import httpx
import asyncio
from typing import Any, Dict, List, Optional, Tuple


async def fetch_github_projects() -> List[Dict[str, Any]]:
    """Fetch all GitHub repositories for the configured user (paginated)."""
    try:
        username = os.getenv("GITHUB_USERNAME")
        token = os.getenv("GITHUB_TOKEN")

        if not username or not token:
            return []

        async with httpx.AsyncClient(timeout=20.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            }

            page = 1
            per_page = 100
            all_repos: List[Dict[str, Any]] = []
            while True:
                url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page={per_page}&page={page}"
                response = await client.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"GitHub API Error: {response.status_code}")
                    break
                repos = response.json()
                if not repos:
                    break
                all_repos.extend(repos)
                page += 1

            processed = [
                {
                    "full_name": repo.get("full_name"),
                    "name": repo["name"],
                    "description": repo["description"] or "No description available",
                    "url": repo["html_url"],
                    "language": repo["language"] or "Mixed",
                    "stars": repo["stargazers_count"],
                    "updated": repo["updated_at"][:10],
                    "topics": repo.get("topics", []),
                }
                for repo in all_repos
                if not repo.get("fork", False)
            ]
            return processed

    except Exception as e:
        print(f"Error fetching GitHub projects: {e}")
        return []


async def fetch_github_profile() -> Optional[Dict[str, Any]]:
    """Fetch GitHub user profile details (avatar, name, bio, counts)."""
    try:
        username = os.getenv("GITHUB_USERNAME")
        token = os.getenv("GITHUB_TOKEN")
        if not username or not token:
            return None
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            }
            url = f"https://api.github.com/users/{username}"
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                print(f"GitHub Profile Error: {r.status_code}")
                return None
            j = r.json()
            return {
                "name": j.get("name") or j.get("login"),
                "login": j.get("login"),
                "bio": j.get("bio"),
                "avatar_url": j.get("avatar_url"),
                "html_url": j.get("html_url"),
                "public_repos": j.get("public_repos", 0),
                "followers": j.get("followers", 0),
                "following": j.get("following", 0),
                "company": j.get("company"),
                "location": j.get("location"),
            }
    except Exception as e:
        print(f"Error fetching GitHub profile: {e}")
        return None


# --------------------------- Language bytes aggregation ---------------------------
_LANG_CACHE: Dict[str, Tuple[float, Dict[str, int]]] = {}
_LANG_TTL_SECONDS = 6 * 60 * 60  # 6 hours


async def _fetch_repo_languages(client: httpx.AsyncClient, full_name: str, headers: Dict[str, str], sem: asyncio.Semaphore) -> Dict[str, int]:
    async with sem:
        try:
            r = await client.get(f"https://api.github.com/repos/{full_name}/languages", headers=headers)
            if r.status_code == 200:
                data = r.json() or {}
                # Ensure ints
                return {k: int(v) for k, v in data.items()}
        except Exception:
            pass
    return {}


async def fetch_language_bytes_aggregate() -> Dict[str, int]:
    """Aggregate language bytes across all non-fork repos for the configured user.

    Cached for several hours to avoid rate-limit and latency.
    """
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")
    if not username or not token:
        return {}

    now = time.time()
    cached = _LANG_CACHE.get(username)
    if cached and (now - cached[0]) < _LANG_TTL_SECONDS:
        return cached[1]

    repos = await fetch_github_projects()
    if not repos:
        return {}

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    sem = asyncio.Semaphore(6)
    async with httpx.AsyncClient(timeout=20.0) as client:
        tasks = [
            _fetch_repo_languages(client, r["full_name"], headers, sem)
            for r in repos if r.get("full_name")
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    aggregate: Dict[str, int] = {}
    for res in results:
        if isinstance(res, dict):
            for lang, bytes_ in res.items():
                aggregate[lang] = aggregate.get(lang, 0) + int(bytes_)

    _LANG_CACHE[username] = (now, aggregate)
    return aggregate

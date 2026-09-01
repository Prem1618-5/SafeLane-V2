import os
import httpx
import logging

logger = logging.getLogger('safelane.platform')

GITHUB_API_BASE = "https://api.github.com"
GITHUB_OAUTH_BASE = "https://github.com/login/oauth"


async def exchange_code_for_token(code: str) -> str:
    """Exchange an OAuth authorization code for a GitHub access token."""
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_OAUTH_BASE}/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            raise ValueError(f"GitHub OAuth token exchange failed: {response.status_code}")

        data = response.json()
        token = data.get("access_token")
        if not token:
            error = data.get("error_description", data.get("error", "Unknown error"))
            raise ValueError(f"GitHub OAuth error: {error}")
        return token


async def get_github_user(token: str) -> dict:
    """Fetch the authenticated user's profile from GitHub."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        if response.status_code != 200:
            raise ValueError("Invalid GitHub token")
        return response.json()


async def validate_token(token: str) -> dict:
    """Validate a GitHub token by fetching the user profile. Alias for get_github_user."""
    return await get_github_user(token)


async def list_user_repos(token: str) -> list[dict]:
    """List repositories accessible by the authenticated user."""
    repos = []
    async with httpx.AsyncClient() as client:
        page = 1
        while page <= 5:  # Cap at 500 repos
            response = await client.get(
                f"{GITHUB_API_BASE}/user/repos",
                params={"per_page": 100, "sort": "updated", "page": page},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch repositories: {response.status_code}")

            batch = response.json()
            if not batch:
                break

            repos.extend([
                {
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "owner": r["owner"]["login"],
                    "private": r["private"],
                    "description": r.get("description", ""),
                    "language": r.get("language"),
                    "updated_at": r.get("updated_at"),
                    "default_branch": r.get("default_branch", "main"),
                }
                for r in batch
            ])
            page += 1
    return repos

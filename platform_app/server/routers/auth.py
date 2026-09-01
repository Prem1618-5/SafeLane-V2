import os
import secrets
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from platform_app.server.services.auth_service import create_jwt, verify_jwt, encrypt_token
from platform_app.server.services.github_service import exchange_code_for_token, get_github_user
from platform_app.server.services.db import upsert_user

logger = logging.getLogger('safelane.platform')

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token", auto_error=False)

# In-memory state store for CSRF protection (use Redis in production)
_oauth_states: set[str] = set()

GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
OAUTH_SCOPES = "repo,read:user,read:org"


@router.get("/github/login")
async def github_login():
    """Redirect the user to GitHub's OAuth authorization page."""
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID is not configured")

    state = secrets.token_urlsafe(32)
    _oauth_states.add(state)

    redirect_url = (
        f"{GITHUB_OAUTH_AUTHORIZE_URL}"
        f"?client_id={client_id}"
        f"&scope={OAUTH_SCOPES}"
        f"&state={state}"
    )
    return RedirectResponse(url=redirect_url)


@router.get("/github/callback")
async def github_callback(code: str = Query(...), state: str = Query(...)):
    """Handle the OAuth callback from GitHub. Exchange code for token, create session."""
    # Verify CSRF state
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")
    _oauth_states.discard(state)

    try:
        # 1. Exchange code for access token
        access_token = await exchange_code_for_token(code)

        # 2. Fetch user profile from GitHub
        user_info = await get_github_user(access_token)

        github_username = user_info["login"]
        github_id = user_info["id"]

        # 3. Encrypt and store the token in the database
        encrypted = encrypt_token(access_token)
        await upsert_user(
            github_id=github_id,
            github_username=github_username,
            encrypted_token=encrypted,
        )

        # 4. Issue a session JWT (contains ONLY username, id, exp — NO raw tokens)
        jwt_token = create_jwt({
            "github_username": github_username,
            "github_id": github_id,
        })

        # 5. Redirect to frontend with the JWT
        frontend_url = os.environ.get("FRONTEND_URL", "")
        redirect_target = f"{frontend_url}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=redirect_target)

    except ValueError as e:
        logger.error(f"OAuth callback failed: {e}")
        frontend_url = os.environ.get("FRONTEND_URL", "")
        return RedirectResponse(url=f"{frontend_url}/auth/callback?error={str(e)}")


async def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]):
    """Dependency to extract and verify the current user from JWT."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return verify_jwt(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    """Return the current user's profile (no sensitive data)."""
    return {
        "github_username": current_user["github_username"],
        "github_id": current_user["github_id"],
    }

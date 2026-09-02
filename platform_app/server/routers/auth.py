import os
import secrets
import hashlib
import base64
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
from typing import Annotated
from platform_app.server.services.auth_service import create_jwt, verify_jwt, encrypt_token
from platform_app.server.services.github_service import exchange_code_for_token, get_github_user
from platform_app.server.services.db import upsert_user

logger = logging.getLogger('safelane.platform')

router = APIRouter()

# In-memory state + PKCE verifier store (use Redis in production)
_oauth_states: set[str] = set()
_oauth_verifiers: dict[str, str] = {}  # state -> code_verifier

GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
OAUTH_SCOPES = "repo,read:user,read:org"

# Cookie config
SESSION_COOKIE_NAME = "safelane_session"
SESSION_MAX_AGE = 86400  # 24 hours


def _generate_pkce_pair() -> tuple[str, str]:
    """Generate a PKCE code_verifier and S256 code_challenge pair."""
    code_verifier = secrets.token_urlsafe(96)  # 128 chars URL-safe
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


@router.get("/github/login")
async def github_login():
    """Redirect the user to GitHub's OAuth authorization page with PKCE."""
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID is not configured")

    state = secrets.token_urlsafe(32)
    _oauth_states.add(state)

    # PKCE: generate code_verifier + S256 code_challenge
    code_verifier, code_challenge = _generate_pkce_pair()
    _oauth_verifiers[state] = code_verifier

    redirect_url = (
        f"{GITHUB_OAUTH_AUTHORIZE_URL}"
        f"?client_id={client_id}"
        f"&scope={OAUTH_SCOPES}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    return RedirectResponse(url=redirect_url)


@router.get("/github/callback")
async def github_callback(code: str = Query(...), state: str = Query(...)):
    """Handle the OAuth callback from GitHub. Exchange code for token, create session."""
    # Verify CSRF state
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid OAuth state parameter")
    _oauth_states.discard(state)

    # PKCE: retrieve and consume the stored code_verifier
    code_verifier = _oauth_verifiers.pop(state, None)

    try:
        # 1. Exchange code for access token (with PKCE verifier)
        access_token = await exchange_code_for_token(code, code_verifier=code_verifier)

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

        # 5. Set JWT as HttpOnly cookie and redirect (no ?token= in URL)
        frontend_url = os.environ.get("FRONTEND_URL", "")
        response = RedirectResponse(url=f"{frontend_url}/auth/callback")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=jwt_token,
            httponly=True,
            secure=os.environ.get("COOKIE_SECURE", "true").lower() != "false",
            samesite="strict",
            max_age=SESSION_MAX_AGE,
            path="/",
        )
        return response

    except ValueError as e:
        logger.error(f"OAuth callback failed: {e}")
        frontend_url = os.environ.get("FRONTEND_URL", "")
        return RedirectResponse(url=f"{frontend_url}/auth/callback?error={str(e)}")


async def get_current_user(request: Request):
    """Dependency to extract and verify the current user from session cookie or Bearer token.
    Supports both HttpOnly cookie (primary) and Authorization header (fallback for API clients)."""
    # Primary: read from HttpOnly cookie
    token = request.cookies.get(SESSION_COOKIE_NAME)

    # Fallback: read from Authorization header (for API/webhook clients)
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return verify_jwt(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def read_users_me(request: Request):
    """Return the current user's profile (no sensitive data)."""
    current_user = await get_current_user(request)
    return {
        "github_username": current_user["github_username"],
        "github_id": current_user["github_id"],
    }


@router.post("/logout")
async def logout(response: Response):
    """Clear the session cookie."""
    resp = Response(content='{"status": "logged_out"}', media_type="application/json")
    resp.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return resp

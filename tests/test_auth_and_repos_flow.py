"""End-to-End and Integration tests for GitHub OAuth flow, session cookies, and repository listing.

Verifies:
1. Unauthenticated requests to `/api/github/user-repos` and `/api/auth/me` return 401 Unauthorized.
2. Full OAuth login flow: `/api/auth/github/login` -> `/api/auth/github/callback` sets HttpOnly session cookie.
3. Authenticated session validation on `/api/auth/me` returning user identity (used by frontend `checkSession()`).
4. Authenticated repository listing on `/api/github/user-repos` returning 200 OK with GitHub repo data.
5. Proves that once authenticated, no 401 redirect loop occurs.
6. Logout endpoint `/api/auth/logout` clears session cookie and revokes authenticated access.
"""
import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet

# Ensure required environment variables
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-auth-flow-testing-12345")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("GITHUB_CLIENT_ID", "mock_github_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "mock_github_client_secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")

from platform_app.server.services.auth_service import create_jwt, reset_singletons
from platform_app.server.routers.auth import (
    router as auth_router,
    SESSION_COOKIE_NAME,
    _oauth_states,
    _oauth_verifiers,
)
from platform_app.server.routers.github_setup import router as github_router


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Ensure clean cryptographic singletons and environment for every test."""
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-for-auth-flow-testing-12345")
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    monkeypatch.setenv("GITHUB_CLIENT_ID", "mock_github_client_id")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "mock_github_client_secret")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:5173")
    monkeypatch.setenv("COOKIE_SECURE", "false")
    reset_singletons()
    _oauth_states.clear()
    _oauth_verifiers.clear()
    yield
    reset_singletons()
    _oauth_states.clear()
    _oauth_verifiers.clear()


@pytest.fixture
def app():
    """Create FastAPI application with auth and github routers."""
    test_app = FastAPI(title="SafeLane Auth Test App")
    test_app.include_router(auth_router, prefix="/api/auth")
    test_app.include_router(github_router, prefix="/api/github")
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.mark.unit
def test_unauthenticated_user_repos_returns_401(client):
    """Unauthenticated access attempt to /api/github/user-repos must return 401."""
    response = client.get("/api/github/user-repos")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_unauthenticated_auth_me_returns_401(client):
    """Unauthenticated access attempt to /api/auth/me must return 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_oauth_login_redirect_and_pkce(client):
    """GET /api/auth/github/login must redirect to GitHub with state and PKCE code challenge."""
    response = client.get("/api/auth/github/login", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers.get("location", "")
    assert "https://github.com/login/oauth/authorize" in location
    assert "client_id=mock_github_client_id" in location
    assert "code_challenge=" in location
    assert "code_challenge_method=S256" in location
    assert "state=" in location
    assert len(_oauth_states) == 1


@pytest.mark.unit
def test_full_oauth_login_and_repos_flow_breaks_login_loop(client):
    """Simulate full OAuth login flow, session cookie issuance, and subsequent authenticated repo fetch.

    This test directly validates that the continuous 401 redirect loop is broken:
    1. Client starts unauthenticated (gets 401).
    2. Client initiates OAuth login and receives state/PKCE challenge.
    3. GitHub callback completes, sets HttpOnly `safelane_session` cookie.
    4. Client calls `/api/auth/me` with cookie -> receives 200 OK with user profile (isAuthenticated = true).
    5. Client calls `/api/github/user-repos` with cookie -> receives 200 OK with repository data (no 401 loop).
    """
    # Step 1: Verify unauthenticated state
    unauth_me = client.get("/api/auth/me")
    assert unauth_me.status_code == 401

    unauth_repos = client.get("/api/github/user-repos")
    assert unauth_repos.status_code == 401

    # Step 2: Initiate OAuth login to establish state and PKCE verifier
    login_resp = client.get("/api/auth/github/login", follow_redirects=False)
    assert login_resp.status_code == 307
    state = list(_oauth_states)[0]
    assert state in _oauth_verifiers

    # Step 3: Handle OAuth callback
    mock_gh_user = {"login": "octocat", "id": 583231}
    mock_repos = [
        {
            "name": "safelane",
            "full_name": "octocat/safelane",
            "owner": "octocat",
            "private": False,
            "description": "SafeLane PR Risk Gate",
            "language": "Python",
            "updated_at": "2026-09-02T18:00:00Z",
            "default_branch": "main",
        },
        {
            "name": "developer-portal",
            "full_name": "octocat/developer-portal",
            "owner": "octocat",
            "private": True,
            "description": "Internal developer portal",
            "language": "TypeScript",
            "updated_at": "2026-09-01T12:00:00Z",
            "default_branch": "main",
        },
    ]

    with patch("platform_app.server.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange, \
         patch("platform_app.server.routers.auth.get_github_user", new_callable=AsyncMock) as mock_get_user, \
         patch("platform_app.server.routers.auth.upsert_user", new_callable=AsyncMock) as mock_upsert, \
         patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:

        mock_exchange.return_value = "gho_mock_token_abcdef123456"
        mock_get_user.return_value = mock_gh_user
        mock_upsert.return_value = None
        mock_get_token.return_value = "gho_mock_token_abcdef123456"
        mock_list_repos.return_value = mock_repos

        # Callback request
        callback_resp = client.get(
            f"/api/auth/github/callback?code=mock_code_123&state={state}",
            follow_redirects=False,
        )
        assert callback_resp.status_code == 307
        assert callback_resp.headers["location"] == "http://localhost:5173/auth/callback"
        assert SESSION_COOKIE_NAME in callback_resp.cookies

        # Step 4: Verify session (/api/auth/me) with cookie transmitted
        me_resp = client.get("/api/auth/me")
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["github_username"] == "octocat"
        assert me_data["github_id"] == 583231
        # Ensure no raw tokens leaked
        assert "token" not in me_data
        assert "pat" not in me_data
        assert "encrypted_token" not in me_data

        # Step 5: Verify protected repo access (/api/github/user-repos) with cookie transmitted
        repos_resp = client.get("/api/github/user-repos")
        assert repos_resp.status_code == 200
        repos_data = repos_resp.json()
        assert len(repos_data) == 2
        assert repos_data[0]["full_name"] == "octocat/safelane"
        assert repos_data[1]["full_name"] == "octocat/developer-portal"

        # Step 6: Verify repeated calls stay authenticated (loop prevention)
        for _ in range(3):
            subsequent_me = client.get("/api/auth/me")
            assert subsequent_me.status_code == 200
            subsequent_repos = client.get("/api/github/user-repos")
            assert subsequent_repos.status_code == 200


@pytest.mark.unit
def test_authenticated_user_repos_with_direct_cookie(client):
    """Direct verification of /api/github/user-repos when valid session cookie is provided."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    mock_repos = [
        {
            "name": "safelane",
            "full_name": "octocat/safelane",
            "owner": "octocat",
            "private": False,
            "description": "SafeLane PR Risk Gate",
            "language": "Python",
            "updated_at": "2026-09-02T18:00:00Z",
            "default_branch": "main",
        }
    ]

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:

        mock_get_token.return_value = "gho_valid_token"
        mock_list_repos.return_value = mock_repos

        response = client.get("/api/github/user-repos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "safelane"


@pytest.mark.unit
def test_authenticated_user_repos_github_token_expired(client):
    """When GitHub API rejects stored token with expiration/invalid error, endpoint returns 401."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:

        mock_get_token.return_value = "gho_expired_token"
        mock_list_repos.side_effect = ValueError("GitHub token invalid or expired. Please re-authenticate.")

        response = client.get("/api/github/user-repos")
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower() or "re-authenticate" in response.json()["detail"].lower()


@pytest.mark.unit
def test_logout_clears_session_and_revokes_access(client):
    """POST /api/auth/logout should delete the session cookie and return 401 on subsequent requests."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    # Verify session active
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200

    # Logout
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "logged_out"

    # Subsequent /api/auth/me should fail with 401
    post_logout_me = client.get("/api/auth/me")
    assert post_logout_me.status_code == 401

    # Subsequent /api/github/user-repos should fail with 401
    post_logout_repos = client.get("/api/github/user-repos")
    assert post_logout_repos.status_code == 401

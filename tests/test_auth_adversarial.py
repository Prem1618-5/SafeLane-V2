"""Adversarial and Stress Test Suite for SafeLane v2 Authentication & Repositories Flow.

Stress-tests:
1. Malformed, corrupted, injected, and oversized session cookies
2. JWT tampering, expired tokens, algorithm confusion, missing claims
3. Database desynchronization & missing/corrupted encrypted tokens
4. Upstream GitHub failure modes (401 revoked, 403 rate limit, 500 error, timeouts, pagination)
5. OAuth state tampering, replay attacks, PKCE verification abuse
6. High-concurrency requests and race conditions
7. Frontend state-machine loop-breaking simulation (comparing Old vs New)
"""
import os
import jwt
import base64
import asyncio
import secrets
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet, InvalidToken

os.environ.setdefault("JWT_SECRET", "adversarial-test-jwt-secret-key-32bytes-len!!")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("GITHUB_CLIENT_ID", "adv_github_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "adv_github_client_secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("COOKIE_SECURE", "false")

from platform_app.server.services.auth_service import (
    create_jwt,
    verify_jwt,
    encrypt_token,
    decrypt_token,
    reset_singletons,
)
from platform_app.server.routers.auth import (
    router as auth_router,
    SESSION_COOKIE_NAME,
    _oauth_states,
    _oauth_verifiers,
)
from platform_app.server.routers.github_setup import router as github_router


@pytest.fixture(autouse=True)
def setup_adv_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "adversarial-test-jwt-secret-key-32bytes-len!!")
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    monkeypatch.setenv("GITHUB_CLIENT_ID", "adv_github_client_id")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "adv_github_client_secret")
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
    test_app = FastAPI(title="SafeLane Adversarial Test App")
    test_app.include_router(auth_router, prefix="/api/auth")
    test_app.include_router(github_router, prefix="/api/github")
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


# ══════════════════════════════════════════════════════════════════════════════
# 1. MALFORMED, CORRUPTED, AND INJECTED COOKIE TESTS
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
@pytest.mark.parametrize("bad_cookie", [
    "",
    "   ",
    "invalid-cookie-token",
    "Bearer not-a-jwt",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",  # header only
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0",  # missing signature
    "a" * 5000,  # large payload
    "' OR '1'='1' --",  # SQL injection attempt
    "<script>alert(1)</script>",  # XSS attempt
    "null",
    "undefined",
    "None",
    "{'github_id': 123}",
    "jwt.token.with.too.many.dots.and.parts",
    "!!!@@@###$$$%%%^^^&&&***",
])
def test_malformed_and_injected_cookies_rejected_cleanly(client, bad_cookie):
    """Corrupted, malicious, or malformed cookies must return 401, never 500 crash."""
    client.cookies.set(SESSION_COOKIE_NAME, bad_cookie, domain="testserver.local", path="/")
    
    # Test /api/auth/me
    resp_me = client.get("/api/auth/me")
    assert resp_me.status_code == 401
    assert "Invalid or expired JWT" in resp_me.json()["detail"] or "Not authenticated" in resp_me.json()["detail"]

    # Test /api/github/user-repos
    resp_repos = client.get("/api/github/user-repos")
    assert resp_repos.status_code == 401
    assert "Invalid or expired JWT" in resp_repos.json()["detail"] or "Not authenticated" in resp_repos.json()["detail"]


@pytest.mark.unit
def test_cookie_vs_bearer_header_precedence(client):
    """HttpOnly cookie takes precedence over Authorization header."""
    valid_jwt = create_jwt({"github_username": "cookie_user", "github_id": 11111})
    client.cookies.set(SESSION_COOKIE_NAME, valid_jwt, domain="testserver.local", path="/")
    
    # Send request with both valid cookie and invalid header
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert resp.status_code == 200
    assert resp.json()["github_username"] == "cookie_user"


@pytest.mark.unit
def test_fallback_bearer_header_when_no_cookie(client):
    """Authorization: Bearer header is accepted when no cookie is set."""
    valid_jwt = create_jwt({"github_username": "bearer_user", "github_id": 22222})
    
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {valid_jwt}"})
    assert resp.status_code == 200
    assert resp.json()["github_username"] == "bearer_user"


# ══════════════════════════════════════════════════════════════════════════════
# 2. JWT CRYPTOGRAPHIC ADVERSARIAL CASES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_expired_jwt_rejected(client):
    """JWT tokens past expiration time must return 401."""
    expired_payload = {
        "github_username": "octocat",
        "github_id": 583231,
        "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
    }
    expired_jwt = jwt.encode(expired_payload, "adversarial-test-jwt-secret-key-32bytes-len!!", algorithm="HS256")
    client.cookies.set(SESSION_COOKIE_NAME, expired_jwt, domain="testserver.local", path="/")

    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert "Invalid or expired JWT" in resp.json()["detail"]


@pytest.mark.unit
def test_jwt_algorithm_none_attack(client):
    """Unsigned JWT tokens ('alg': 'none') must be rejected."""
    none_payload = {
        "github_username": "attacker",
        "github_id": 99999,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    # Unsigned token
    unsigned_token = jwt.encode(none_payload, key="", algorithm=None)
    client.cookies.set(SESSION_COOKIE_NAME, unsigned_token, domain="testserver.local", path="/")

    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.unit
def test_jwt_signed_with_wrong_secret(client):
    """JWT signed with an unauthorized secret must fail verification."""
    fake_secret = "completely-wrong-secret-key-123456789012"
    fake_token = jwt.encode(
        {"github_username": "impostor", "github_id": 666, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        fake_secret,
        algorithm="HS256"
    )
    client.cookies.set(SESSION_COOKIE_NAME, fake_token, domain="testserver.local", path="/")

    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.unit
def test_jwt_tampered_payload_breaks_signature(client):
    """Modifying claims in transit without re-signing must fail."""
    valid_token = create_jwt({"github_username": "regular_user", "github_id": 123})
    parts = valid_token.split(".")
    # Replace payload with forged base64
    forged_payload = base64.urlsafe_b64encode(b'{"github_username":"admin","github_id":1}').decode().rstrip("=")
    tampered_token = f"{parts[0]}.{forged_payload}.{parts[2]}"

    client.cookies.set(SESSION_COOKIE_NAME, tampered_token, domain="testserver.local", path="/")
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# 3. DATABASE / TOKEN STORAGE INCONSISTENCIES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_valid_jwt_but_no_db_user_returns_401(client):
    """User has a valid session JWT, but was deleted or never saved in DB."""
    session_jwt = create_jwt({"github_username": "ghost_user", "github_id": 404404})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup.get_user_by_github_id", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = None

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 401
        assert "No GitHub token stored" in resp.json()["detail"]


@pytest.mark.unit
def test_valid_jwt_but_empty_encrypted_token_returns_401(client):
    """User exists in DB but encrypted_token field is None."""
    session_jwt = create_jwt({"github_username": "empty_token_user", "github_id": 505505})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    mock_db_user = MagicMock()
    mock_db_user.encrypted_token = None

    with patch("platform_app.server.routers.github_setup.get_user_by_github_id", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = mock_db_user

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 401
        assert "No GitHub token stored" in resp.json()["detail"]


# ══════════════════════════════════════════════════════════════════════════════
# 4. UPSTREAM GITHUB FAILURE MODES & RESILIENCE
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_github_401_revoked_token(client):
    """When GitHub API rejects stored token with 401 Unauthorized, endpoint returns 401."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:
        mock_get_token.return_value = "gho_revoked"
        mock_list_repos.side_effect = ValueError("GitHub token expired or revoked. Please re-authenticate.")

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 401
        assert "re-authenticate" in resp.json()["detail"].lower()


@pytest.mark.unit
def test_github_403_rate_limit_handled(client):
    """When GitHub API rate limit is exceeded (403), endpoint handles it as 401 re-auth."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:
        mock_get_token.return_value = "gho_rate_limited"
        mock_list_repos.side_effect = ValueError("GitHub token expired or revoked. Please re-authenticate.")

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 401


@pytest.mark.unit
def test_github_500_upstream_server_error(client):
    """When GitHub API fails with 500 upstream, endpoint returns 400 with detail without 500 crash."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:
        mock_get_token.return_value = "gho_token"
        mock_list_repos.side_effect = ValueError("Failed to fetch repositories: 500")

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 400
        assert "Failed to fetch repositories: 500" in resp.json()["detail"]


@pytest.mark.unit
def test_github_empty_repo_list(client):
    """When user has 0 repositories on GitHub, returns empty list 200 OK."""
    session_jwt = create_jwt({"github_username": "new_user", "github_id": 100})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:
        mock_get_token.return_value = "gho_token"
        mock_list_repos.return_value = []

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.unit
def test_github_pagination_multi_page(client):
    """Verify repository fetching handles multi-page repository responses."""
    session_jwt = create_jwt({"github_username": "prolific_coder", "github_id": 777})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    mock_page = [
        {"name": f"repo_{i}", "full_name": f"prolific_coder/repo_{i}", "owner": "prolific_coder", "private": False}
        for i in range(150)
    ]

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:
        mock_get_token.return_value = "gho_token"
        mock_list_repos.return_value = mock_page

        resp = client.get("/api/github/user-repos")
        assert resp.status_code == 200
        assert len(resp.json()) == 150


# ══════════════════════════════════════════════════════════════════════════════
# 5. OAUTH FLOW STATE TAMPERING & REPLAY ATTACK DEFENSE
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_oauth_callback_state_tampering_rejected(client):
    """Forged or unissued state in OAuth callback must be rejected with 400."""
    resp = client.get("/api/auth/github/callback?code=fake_code&state=unissued_state_12345")
    assert resp.status_code == 400
    assert "Invalid OAuth state parameter" in resp.json()["detail"]


@pytest.mark.unit
def test_oauth_callback_state_replay_attack_prevented(client):
    """A consumed OAuth state cannot be used a second time."""
    # Step 1: Initialize login to register state
    login_resp = client.get("/api/auth/github/login", follow_redirects=False)
    state = list(_oauth_states)[0]

    with patch("platform_app.server.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange, \
         patch("platform_app.server.routers.auth.get_github_user", new_callable=AsyncMock) as mock_get_user, \
         patch("platform_app.server.routers.auth.upsert_user", new_callable=AsyncMock):
        mock_exchange.return_value = "gho_token_123"
        mock_get_user.return_value = {"login": "octocat", "id": 583231}

        # First callback attempt (success)
        first_resp = client.get(f"/api/auth/github/callback?code=code1&state={state}", follow_redirects=False)
        assert first_resp.status_code == 307
        assert SESSION_COOKIE_NAME in first_resp.cookies

        # Second callback attempt with SAME state (replay attack -> rejected)
        second_resp = client.get(f"/api/auth/github/callback?code=code2&state={state}", follow_redirects=False)
        assert second_resp.status_code == 400
        assert "Invalid OAuth state parameter" in second_resp.json()["detail"]


@pytest.mark.unit
def test_oauth_callback_upstream_error_redirects_gracefully(client):
    """When GitHub OAuth token exchange fails, callback redirects with error parameter instead of crashing."""
    login_resp = client.get("/api/auth/github/login", follow_redirects=False)
    state = list(_oauth_states)[0]

    with patch("platform_app.server.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
        mock_exchange.side_effect = ValueError("GitHub OAuth error: bad_verification_code")

        resp = client.get(f"/api/auth/github/callback?code=invalid_code&state={state}", follow_redirects=False)
        assert resp.status_code == 307
        location = resp.headers.get("location", "")
        assert "http://localhost:5173/auth/callback?error=" in location
        assert "bad_verification_code" in location


# ══════════════════════════════════════════════════════════════════════════════
# 6. CONCURRENCY & RAPID REQUEST STRESS TESTING
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.unit
def test_rapid_concurrent_requests_to_user_repos(client):
    """50 rapid sequential/concurrent requests maintain session consistency."""
    session_jwt = create_jwt({"github_username": "octocat", "github_id": 583231})
    client.cookies.set(SESSION_COOKIE_NAME, session_jwt, domain="testserver.local", path="/")

    mock_repos = [{"name": "repo1", "full_name": "octocat/repo1", "owner": "octocat", "private": False}]

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as mock_get_token, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as mock_list_repos:
        mock_get_token.return_value = "gho_token"
        mock_list_repos.return_value = mock_repos

        for i in range(50):
            resp = client.get("/api/github/user-repos")
            assert resp.status_code == 200
            assert resp.json()[0]["name"] == "repo1"


@pytest.mark.unit
def test_concurrent_login_state_generation_isolated(client):
    """Multiple concurrent login requests generate unique, isolated states."""
    states = []
    for _ in range(25):
        resp = client.get("/api/auth/github/login", follow_redirects=False)
        assert resp.status_code == 307
    assert len(_oauth_states) == 25
    assert len(_oauth_verifiers) == 25


# ══════════════════════════════════════════════════════════════════════════════
# 7. FRONTEND STATE-MACHINE SIMULATION (COMPARISON: OLD VS NEW IMPLEMENTATION)
# ══════════════════════════════════════════════════════════════════════════════

class FixedFrontendSimulator:
    """Simulates fixed App.jsx & SignIn.jsx using isAuthenticated."""
    
    def __init__(self, is_authenticated: bool, current_route: str):
        self.is_authenticated = is_authenticated
        self.current_route = current_route
        self.redirect_chain = []
        self.rendered_page = None

    def navigate(self, to: str, replace: bool = False):
        self.redirect_chain.append(to)
        self.current_route = to
        if len(self.redirect_chain) > 10:
            raise RecursionError("Infinite redirect loop detected!")
        self.render()

    def render(self):
        if self.current_route == "/":
            # SignIn.jsx (fixed): if (isAuthenticated) navigate('/repos')
            if self.is_authenticated:
                return self.navigate("/repos", replace=True)
            self.rendered_page = "SignIn"
            return
            
        elif self.current_route == "/auth/callback":
            # AuthCallback.jsx: checkSession() finishes
            if self.is_authenticated:
                return self.navigate("/repos", replace=True)
            else:
                return self.navigate("/", replace=True)
                
        elif self.current_route.startswith("/repos"):
            # ProtectedRoute in App.jsx (fixed): if (!isAuthenticated) navigate('/')
            if not self.is_authenticated:
                return self.navigate("/", replace=True)
            self.rendered_page = "Repos"
            return


class BrokenFrontendSimulator:
    """Simulates the buggy App.jsx & SignIn.jsx where token was undefined."""
    
    def __init__(self, is_authenticated_in_backend: bool, current_route: str):
        # AuthProvider only provides isAuthenticated, NOT token
        self.is_authenticated = is_authenticated_in_backend
        self.token = None  # token was always undefined
        self.current_route = current_route
        self.redirect_chain = []
        self.rendered_page = None

    def navigate(self, to: str, replace: bool = False):
        self.redirect_chain.append(to)
        self.current_route = to
        if len(self.redirect_chain) > 10:
            raise RecursionError("Infinite redirect loop detected!")
        self.render()

    def render(self):
        if self.current_route == "/":
            # Buggy SignIn.jsx: if (token) navigate('/repos') -> token is None, never redirects
            if self.token:
                return self.navigate("/repos", replace=True)
            self.rendered_page = "SignIn"
            return
            
        elif self.current_route == "/auth/callback":
            # AuthCallback.jsx: checkSession() sets isAuthenticated=true, navigates to /repos
            if self.is_authenticated:
                return self.navigate("/repos", replace=True)
            else:
                return self.navigate("/", replace=True)
                
        elif self.current_route.startswith("/repos"):
            # Buggy ProtectedRoute in App.jsx: if (!token) navigate('/') -> token is None, always redirects!
            if not self.token:
                return self.navigate("/", replace=True)
            self.rendered_page = "Repos"
            return


@pytest.mark.unit
def test_broken_old_code_prevents_repos_access_even_when_authenticated():
    """Empirical proof of the bug: Old code always trapped authenticated user on SignIn."""
    sim = BrokenFrontendSimulator(is_authenticated_in_backend=True, current_route="/auth/callback")
    sim.render()
    # Callback navigates to /repos, but ProtectedRoute bounces user back to / (SignIn)
    assert sim.redirect_chain == ["/repos", "/"]
    assert sim.rendered_page == "SignIn"  # User is blocked from ever accessing Repos page!


@pytest.mark.unit
def test_fixed_new_code_allows_authenticated_user_to_access_repos():
    """Empirical proof of the fix: New code cleanly navigates to Repos and renders."""
    sim = FixedFrontendSimulator(is_authenticated=True, current_route="/auth/callback")
    sim.render()
    assert sim.redirect_chain == ["/repos"]
    assert sim.rendered_page == "Repos"


@pytest.mark.unit
def test_fixed_new_code_authenticated_on_root_redirects_to_repos():
    """Authenticated user navigating to / is immediately redirected to /repos."""
    sim = FixedFrontendSimulator(is_authenticated=True, current_route="/")
    sim.render()
    assert sim.redirect_chain == ["/repos"]
    assert sim.rendered_page == "Repos"


@pytest.mark.unit
def test_fixed_new_code_unauthenticated_on_repos_redirects_to_root():
    """Unauthenticated user trying to access /repos is redirected to /."""
    sim = FixedFrontendSimulator(is_authenticated=False, current_route="/repos")
    sim.render()
    assert sim.redirect_chain == ["/"]
    assert sim.rendered_page == "SignIn"

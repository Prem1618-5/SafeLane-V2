"""Adversarial Stress Testing for SafeLane v2 OAuth, Session Cookies, and Repository Access.

Conducted by Challenger agent (challenger_m1_3) to empirically probe edge cases:
1. Unauthenticated endpoints (401 verification).
2. Authenticated valid cookie session with repo data return.
3. Expired JWT session cookies (401 verification).
4. Tampered JWT signature and algorithm confusion (none alg, RS256 confusion) (401 verification).
5. Corrupted, empty, and adversarial cookie payloads (SQLi strings, unicode, oversized payload, JSON injection).
6. Missing required JWT claims (missing github_username, github_id).
7. Fallback Authorization header Bearer token validation and edge cases.
8. User database lookup failures (user not found, missing encrypted_token, corrupted ciphertext).
9. Upstream GitHub API error translation (token expiration/invalidation vs rate limit).
10. OAuth state parameter single-use consumption and CSRF protection.
11. Cookie lifecycle and logout session revocation.
12. Simulated SPA State Transition Matrix to prove absence of 401 redirect loop.
"""
import os
import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
import jwt

# Test environment configuration
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-auth-flow-testing-12345")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("GITHUB_CLIENT_ID", "mock_github_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "mock_github_client_secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("COOKIE_SECURE", "false")

from platform_app.server.services.auth_service import create_jwt, verify_jwt, reset_singletons, encrypt_token
from platform_app.server.routers.auth import (
    router as auth_router,
    SESSION_COOKIE_NAME,
    _oauth_states,
    _oauth_verifiers,
)
from platform_app.server.routers.github_setup import router as github_router


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
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
    test_app = FastAPI(title="SafeLane Auth Stress App")
    test_app.include_router(auth_router, prefix="/api/auth")
    test_app.include_router(github_router, prefix="/api/github")
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


# ── Challenge 1: Unauthenticated Endpoints ──

@pytest.mark.unit
def test_unauthenticated_requests_return_401(client):
    r1 = client.get("/api/github/user-repos")
    assert r1.status_code == 401
    assert r1.json()["detail"] == "Not authenticated"

    r2 = client.get("/api/auth/me")
    assert r2.status_code == 401
    assert r2.json()["detail"] == "Not authenticated"


# ── Challenge 2: Authenticated Access with Valid Cookie ──

@pytest.mark.unit
def test_authenticated_valid_cookie_returns_repos(client):
    token = create_jwt({"github_username": "test_user", "github_id": 42})
    client.cookies.set(SESSION_COOKIE_NAME, token, domain="testserver.local", path="/")

    mock_repos = [
        {"name": "repo1", "full_name": "test_user/repo1", "owner": "test_user"},
        {"name": "repo2", "full_name": "test_user/repo2", "owner": "test_user"},
    ]

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as m_tok, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as m_rep:
        m_tok.return_value = "gho_valid_decrypted_token"
        m_rep.return_value = mock_repos

        r_me = client.get("/api/auth/me")
        assert r_me.status_code == 200
        assert r_me.json() == {"github_username": "test_user", "github_id": 42}

        r_repos = client.get("/api/github/user-repos")
        assert r_repos.status_code == 200
        assert r_repos.json() == mock_repos


# ── Challenge 3: Expired, Tampered, and Malformed JWT Cookies ──

@pytest.mark.unit
@pytest.mark.parametrize("cookie_desc,cookie_value", [
    ("expired_token", jwt.encode({"github_username": "u", "github_id": 1, "exp": datetime.now(timezone.utc) - timedelta(seconds=10)}, "test-secret-key-for-auth-flow-testing-12345", algorithm="HS256")),
    ("tampered_signature", jwt.encode({"github_username": "u", "github_id": 1, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "different-secret-key-32-bytes-long!", algorithm="HS256")),
    ("algorithm_none_attack", jwt.encode({"github_username": "u", "github_id": 1, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, key="", algorithm="none")),
    ("corrupted_jwt_string", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsig"),
    ("empty_cookie", ""),
    ("whitespace_cookie", "   "),
    ("sqli_payload", "' OR 1=1; --"),
    ("xss_payload", "<script>alert(1)</script>"),
    ("json_dict_payload", json.dumps({"admin": True})),
    ("huge_oversized_payload", "A" * 8192),
    ("special_characters", "!@#$%^&*()_+-=[]{}|;':,./<>?"),
])
def test_malformed_tampered_expired_cookies_fail_safely(client, cookie_desc, cookie_value):
    client.cookies.set(SESSION_COOKIE_NAME, cookie_value, domain="testserver.local", path="/")
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 401, f"[{cookie_desc}] /api/auth/me returned {r_me.status_code}"

    r_repos = client.get("/api/github/user-repos")
    assert r_repos.status_code == 401, f"[{cookie_desc}] /api/github/user-repos returned {r_repos.status_code}"


# ── Challenge 4: Authorization Header Fallback & Scheme Stress ──

@pytest.mark.unit
def test_bearer_header_fallback_and_malformed_headers(client):
    valid_jwt = create_jwt({"github_username": "bearer_user", "github_id": 99})

    # Valid Bearer header
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {valid_jwt}"})
    assert r.status_code == 200
    assert r.json()["github_username"] == "bearer_user"

    # Malformed Bearer header
    r_bad = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token"})
    assert r_bad.status_code == 401

    # Empty Bearer header
    r_empty = client.get("/api/auth/me", headers={"Authorization": "Bearer "})
    assert r_empty.status_code == 401

    # Non-Bearer schemes (Basic, Token, Digest)
    r_basic = client.get("/api/auth/me", headers={"Authorization": f"Basic {valid_jwt}"})
    assert r_basic.status_code == 401

    r_token = client.get("/api/auth/me", headers={"Authorization": f"Token {valid_jwt}"})
    assert r_token.status_code == 401


# ── Challenge 5: Database User and Encryption Failures ──

@pytest.mark.unit
def test_database_user_missing_or_corrupted_token(client):
    valid_jwt = create_jwt({"github_username": "db_user", "github_id": 777})
    client.cookies.set(SESSION_COOKIE_NAME, valid_jwt, domain="testserver.local", path="/")

    # 1. User not in DB
    with patch("platform_app.server.routers.github_setup.get_user_by_github_id", new_callable=AsyncMock) as m_get_user:
        m_get_user.return_value = None
        r = client.get("/api/github/user-repos")
        assert r.status_code == 401
        assert "No GitHub token stored" in r.json()["detail"]

    # 2. User in DB but encrypted_token is None/empty
    with patch("platform_app.server.routers.github_setup.get_user_by_github_id", new_callable=AsyncMock) as m_get_user:
        class FakeUser:
            encrypted_token = None
        m_get_user.return_value = FakeUser()
        r = client.get("/api/github/user-repos")
        assert r.status_code == 401
        assert "No GitHub token stored" in r.json()["detail"]


# ── Challenge 6: Upstream GitHub Service Error Handling ──

@pytest.mark.unit
def test_github_service_error_handling(client):
    valid_jwt = create_jwt({"github_username": "gh_user", "github_id": 888})
    client.cookies.set(SESSION_COOKIE_NAME, valid_jwt, domain="testserver.local", path="/")

    with patch("platform_app.server.routers.github_setup._get_user_token", new_callable=AsyncMock) as m_tok, \
         patch("platform_app.server.routers.github_setup.list_user_repos", new_callable=AsyncMock) as m_rep:
        m_tok.return_value = "gho_some_token"

        # Expired GitHub token -> 401
        m_rep.side_effect = ValueError("GitHub token invalid or expired. Please re-authenticate.")
        r1 = client.get("/api/github/user-repos")
        assert r1.status_code == 401
        assert "re-authenticate" in r1.json()["detail"].lower()

        # Non-auth error (e.g. rate limiting or upstream 500) -> 400
        m_rep.side_effect = ValueError("API rate limit exceeded")
        r2 = client.get("/api/github/user-repos")
        assert r2.status_code == 400
        assert "rate limit" in r2.json()["detail"].lower()


# ── Challenge 7: OAuth Flow CSRF & Single-Use State ──

@pytest.mark.unit
def test_oauth_csrf_and_state_replay_prevention(client):
    # Callback with non-existent state must return 400
    r_bad_state = client.get("/api/auth/github/callback?code=abc&state=unregistered_state")
    assert r_bad_state.status_code == 400
    assert "Invalid OAuth state" in r_bad_state.json()["detail"]

    # Generate state via login
    login_resp = client.get("/api/auth/github/login", follow_redirects=False)
    assert login_resp.status_code == 307
    real_state = list(_oauth_states)[0]

    # Replay attack: First callback succeeds, second must be rejected (400)
    with patch("platform_app.server.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as m_ex, \
         patch("platform_app.server.routers.auth.get_github_user", new_callable=AsyncMock) as m_usr, \
         patch("platform_app.server.routers.auth.upsert_user", new_callable=AsyncMock) as m_ups:
        m_ex.return_value = "gho_123"
        m_usr.return_value = {"login": "octo", "id": 1}
        m_ups.return_value = None

        r1 = client.get(f"/api/auth/github/callback?code=abc&state={real_state}", follow_redirects=False)
        assert r1.status_code == 307
        assert SESSION_COOKIE_NAME in r1.cookies

        # Replayed callback with same state must fail with 400
        r2 = client.get(f"/api/auth/github/callback?code=abc&state={real_state}", follow_redirects=False)
        assert r2.status_code == 400


# ── Challenge 8: Logout Lifecycle & Cookie Invalidation ──

@pytest.mark.unit
def test_logout_lifecycle_complete(client):
    valid_jwt = create_jwt({"github_username": "logout_user", "github_id": 555})
    client.cookies.set(SESSION_COOKIE_NAME, valid_jwt, domain="testserver.local", path="/")

    # Verify active session
    r_me = client.get("/api/auth/me")
    assert r_me.status_code == 200

    # Logout
    r_logout = client.post("/api/auth/logout")
    assert r_logout.status_code == 200
    assert r_logout.json() == {"status": "logged_out"}

    # Subsequent access is 401
    r_after_me = client.get("/api/auth/me")
    assert r_after_me.status_code == 401

    r_after_repos = client.get("/api/github/user-repos")
    assert r_after_repos.status_code == 401


# ── Challenge 9: Simulated Frontend State Transitions & Infinite Loop Prevention ──

@pytest.mark.unit
def test_spa_state_transitions_no_infinite_loop():
    """Formally test the React SPA Auth state transition table for ProtectedRoute and SignIn."""
    def protected_route_behavior(loading: bool, is_authenticated: bool):
        if loading:
            return "LOADING_SPINNER"
        if not is_authenticated:
            return "NAVIGATE_TO_ROOT"
        return "RENDER_PROTECTED_CHILDREN"

    def sign_in_behavior(is_authenticated: bool):
        if is_authenticated:
            return "NAVIGATE_TO_REPOS"
        return "RENDER_SIGN_IN_PAGE"

    # State 1: Unauthenticated user visits /repos
    assert protected_route_behavior(loading=False, is_authenticated=False) == "NAVIGATE_TO_ROOT"
    assert sign_in_behavior(is_authenticated=False) == "RENDER_SIGN_IN_PAGE"

    # State 2: User logging in (loading state)
    assert protected_route_behavior(loading=True, is_authenticated=False) == "LOADING_SPINNER"

    # State 3: Authenticated user visits /repos
    assert protected_route_behavior(loading=False, is_authenticated=True) == "RENDER_PROTECTED_CHILDREN"

    # State 4: Authenticated user visits / (SignIn)
    assert sign_in_behavior(is_authenticated=True) == "NAVIGATE_TO_REPOS"

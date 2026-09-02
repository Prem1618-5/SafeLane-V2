"""Advanced Concurrency, Session Isolation, and Boundary Stress Tests for SafeLane v2."""
import os
import concurrent.futures
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
import jwt

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-auth-flow-testing-12345")
os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("GITHUB_CLIENT_ID", "mock_github_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "mock_github_client_secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")
os.environ.setdefault("COOKIE_SECURE", "false")

from platform_app.server.services.auth_service import create_jwt, reset_singletons
from platform_app.server.routers.auth import router as auth_router, SESSION_COOKIE_NAME, _oauth_states, _oauth_verifiers
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
    test_app = FastAPI(title="SafeLane Concurrency Stress App")
    test_app.include_router(auth_router, prefix="/api/auth")
    test_app.include_router(github_router, prefix="/api/github")
    return test_app

@pytest.mark.unit
def test_concurrent_multi_user_session_isolation(app):
    """Ensure that 20 concurrent users with distinct session cookies never leak data across requests."""
    
    async def mock_get_token(current_user):
        return f"gho_token_{current_user['github_id']}"

    async def mock_list_repos(token):
        user_id = token.replace("gho_token_", "")
        return [{"name": f"repo_{user_id}", "full_name": f"user_{user_id}/repo_{user_id}"}]

    with patch("platform_app.server.routers.github_setup._get_user_token", side_effect=mock_get_token), \
         patch("platform_app.server.routers.github_setup.list_user_repos", side_effect=mock_list_repos):

        def run_user_session(user_id):
            client = TestClient(app)
            username = f"user_{user_id}"
            token = create_jwt({"github_username": username, "github_id": user_id})
            client.cookies.set(SESSION_COOKIE_NAME, token, domain="testserver.local", path="/")

            for _ in range(5):
                r_me = client.get("/api/auth/me")
                assert r_me.status_code == 200
                assert r_me.json()["github_username"] == username
                assert r_me.json()["github_id"] == user_id

                r_repos = client.get("/api/github/user-repos")
                assert r_repos.status_code == 200
                assert r_repos.json()[0]["full_name"] == f"{username}/repo_{user_id}"
            return True

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_user_session, i) for i in range(1, 21)]
            for f in concurrent.futures.as_completed(futures):
                assert f.result() is True

@pytest.mark.unit
def test_jwt_expiration_exact_boundary(app):
    """Test token expiration right at boundary conditions."""
    client = TestClient(app)
    secret = "test-secret-key-for-auth-flow-testing-12345"

    # Token expired 1 second ago -> 401
    past_token = jwt.encode(
        {"github_username": "past", "github_id": 1, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        secret,
        algorithm="HS256"
    )
    client.cookies.set(SESSION_COOKIE_NAME, past_token, domain="testserver.local", path="/")
    assert client.get("/api/auth/me").status_code == 401

    # Token valid for 10 seconds -> 200
    future_token = jwt.encode(
        {"github_username": "future", "github_id": 2, "exp": datetime.now(timezone.utc) + timedelta(seconds=10)},
        secret,
        algorithm="HS256"
    )
    client.cookies.set(SESSION_COOKIE_NAME, future_token, domain="testserver.local", path="/")
    assert client.get("/api/auth/me").status_code == 200
    assert client.get("/api/auth/me").json()["github_username"] == "future"

@pytest.mark.unit
def test_cookie_tamper_bitflip(app):
    """Test bit-flipping on valid JWT signature to ensure cryptographic validation never panics."""
    client = TestClient(app)
    valid_token = create_jwt({"github_username": "victim", "github_id": 100})
    header, payload, sig = valid_token.split(".")

    # Tamper with signature: flip last char
    flipped_char = 'B' if sig[-1] != 'B' else 'C'
    tampered_token = f"{header}.{payload}.{sig[:-1]}{flipped_char}"

    client.cookies.set(SESSION_COOKIE_NAME, tampered_token, domain="testserver.local", path="/")
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid or expired JWT"

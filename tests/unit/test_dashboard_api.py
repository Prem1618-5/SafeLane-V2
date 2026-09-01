"""Tests for dashboard REST API endpoints."""
import pytest
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Set env vars before imports
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-dashboard-tests")
os.environ.setdefault("ENCRYPTION_KEY", "dGVzdC1lbmNyeXB0aW9uLWtleS0xMjM0NTY3ODkwYWJj")

from server.services.auth_service import create_jwt, reset_singletons
from server.routers.dashboard import router as dashboard_router
from server.routers.auth import router as auth_router


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-dashboard-secret")
    from cryptography.fernet import Fernet
    monkeypatch.setenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
    reset_singletons()
    yield
    reset_singletons()


@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(dashboard_router, prefix="/api/dashboard")
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)


@pytest.fixture
def auth_header():
    token = create_jwt({"github_username": "testuser", "github_id": 99999})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.unit
def test_dashboard_repos_unauthenticated(client):
    """Unauthenticated requests to dashboard should return 401."""
    resp = client.get("/api/dashboard/repos")
    assert resp.status_code == 401


@pytest.mark.unit
def test_dashboard_repos_authenticated(client, auth_header):
    """Authenticated requests should return a list (possibly empty)."""
    with patch("server.routers.dashboard.list_registrations", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        resp = client.get("/api/dashboard/repos", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.unit
def test_dashboard_repos_with_data(client, auth_header):
    """Dashboard should return repo data with safety scores."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.owner = "testorg"
    mock_reg.repo = "testrepo"
    mock_reg.is_active = True
    mock_reg.last_synced_at = None
    mock_reg.sync_error = None
    mock_reg.created_at = None

    with patch("server.routers.dashboard.list_registrations", new_callable=AsyncMock) as mock_list, \
         patch("server.routers.dashboard.get_analysis_records", new_callable=AsyncMock) as mock_analysis:
        mock_list.return_value = [mock_reg]
        mock_analysis.return_value = []

        resp = client.get("/api/dashboard/repos", headers=auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["full_name"] == "testorg/testrepo"
        assert data[0]["is_active"] is True


@pytest.mark.unit
def test_dashboard_repo_detail_not_found(client, auth_header):
    """Request for non-existent repo should return 404."""
    with patch("server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = client.get("/api/dashboard/repos/999", headers=auth_header)
        assert resp.status_code == 404


@pytest.mark.unit
def test_dashboard_repo_detail_wrong_user(client, auth_header):
    """Request for another user's repo should return 404."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.user_id = 11111  # Different from auth user (99999)

    with patch("server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_reg
        resp = client.get("/api/dashboard/repos/1", headers=auth_header)
        assert resp.status_code == 404


@pytest.mark.unit
def test_dashboard_pr_detail_unauthenticated(client):
    """PR detail endpoint should require authentication."""
    resp = client.get("/api/dashboard/repos/1/prs/42")
    assert resp.status_code == 401


@pytest.mark.unit
def test_me_endpoint(client, auth_header):
    """The /me endpoint should return user info without sensitive data."""
    resp = client.get("/api/auth/me", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["github_username"] == "testuser"
    assert data["github_id"] == 99999
    assert "pat" not in data
    assert "token" not in data

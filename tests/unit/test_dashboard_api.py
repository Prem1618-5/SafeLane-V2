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

from platform_app.server.services.auth_service import create_jwt, reset_singletons
from platform_app.server.routers.dashboard import router as dashboard_router
from platform_app.server.routers.auth import router as auth_router
from platform_app.server.routers.registrations import router as registrations_router


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
    app.include_router(registrations_router, prefix="/api/registrations")
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
    with patch("platform_app.server.routers.dashboard.list_registrations", new_callable=AsyncMock) as mock_list:
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

    with patch("platform_app.server.routers.dashboard.list_registrations", new_callable=AsyncMock) as mock_list, \
         patch("platform_app.server.routers.dashboard.get_analysis_records", new_callable=AsyncMock) as mock_analysis:
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
    with patch("platform_app.server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = client.get("/api/dashboard/repos/999", headers=auth_header)
        assert resp.status_code == 404


@pytest.mark.unit
def test_dashboard_repo_detail_wrong_user(client, auth_header):
    """Request for another user's repo should return 404."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.user_id = 11111  # Different from auth user (99999)

    with patch("platform_app.server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_reg
        resp = client.get("/api/dashboard/repos/1", headers=auth_header)
        assert resp.status_code == 404


@pytest.mark.unit
def test_dashboard_pr_detail_unauthenticated(client):
    """PR detail endpoint should require authentication."""
    resp = client.get("/api/dashboard/repos/1/prs/42")
    assert resp.status_code == 401


@pytest.mark.unit
def test_dashboard_pr_detail_authenticated_with_changed_files(client, auth_header):
    """PR detail endpoint should return parsed changed_files, evidence_results, and security_findings."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.user_id = 99999

    mock_analysis = MagicMock()
    mock_analysis.id = 101
    mock_analysis.pr_number = 42
    mock_analysis.head_sha = "abc1234567"
    mock_analysis.confidence_score = 85
    mock_analysis.decision = "greenlight"
    mock_analysis.risk_brief = "Low risk PR"
    mock_analysis.rollback_playbook = None
    mock_analysis.created_at = None
    mock_analysis.evidence_json = json.dumps([
        {
            "module": "verification_readiness",
            "status": "warning",
            "risk_score_modifier": 10,
            "findings": [
                "Missing test for src/utils.py",
                "Deleted test file detected: tests/old_test.py",
            ],
            "recommended_action": "Add tests for src/utils.py",
        }
    ])
    mock_analysis.security_findings_json = json.dumps([
        {
            "rule_id": "SEC-001",
            "severity": "info",
            "file": "src/config.py",
            "evidence": "Debug flag detected",
            "remediation": "Disable debug in prod",
        }
    ])

    with patch("platform_app.server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get_reg, \
         patch("platform_app.server.routers.dashboard.get_analysis_by_pr", new_callable=AsyncMock) as mock_get_pr:
        mock_get_reg.return_value = mock_reg
        mock_get_pr.return_value = mock_analysis

        resp = client.get("/api/dashboard/repos/1/prs/42", headers=auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 101
        assert data["pr_number"] == 42
        assert data["decision"] == "GREENLIGHT"
        assert data["confidence_score"] == 85
        assert "src/utils.py" in data["changed_files"]
        assert "tests/old_test.py" in data["changed_files"]
        assert "src/config.py" in data["changed_files"]
        assert len(data["evidence_results"]) == 1
        assert len(data["security_findings"]) == 1


@pytest.mark.unit
def test_dashboard_pr_detail_analysis_not_found(client, auth_header):
    """PR detail endpoint should return 404 when analysis does not exist."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.user_id = 99999

    with patch("platform_app.server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get_reg, \
         patch("platform_app.server.routers.dashboard.get_analysis_by_pr", new_callable=AsyncMock) as mock_get_pr:
        mock_get_reg.return_value = mock_reg
        mock_get_pr.return_value = None

        resp = client.get("/api/dashboard/repos/1/prs/999", headers=auth_header)
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Analysis not found for this PR"


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


@pytest.mark.unit
def test_dashboard_sync_repo(client, auth_header):
    """POST /api/dashboard/repos/{reg_id}/sync should trigger background sync."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.user_id = 99999

    with patch("platform_app.server.routers.dashboard.get_registration_by_id", new_callable=AsyncMock) as mock_get_reg, \
         patch("platform_app.server.services.sync_service.sync_repository", new_callable=AsyncMock) as mock_sync:
        mock_get_reg.return_value = mock_reg

        resp = client.post("/api/dashboard/repos/1/sync", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == {"status": "sync_triggered", "reg_id": 1}


@pytest.mark.unit
def test_registration_deactivate_endpoint(client, auth_header):
    """POST /api/registrations/{reg_id}/deactivate should mark registration inactive."""
    mock_reg = MagicMock()
    mock_reg.id = 1
    mock_reg.user_id = 99999
    mock_reg.is_active = True

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_reg
    mock_session.execute.return_value = mock_result

    class MockAsyncSessionContext:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, *args):
            pass

    with patch("platform_app.server.routers.registrations.async_session", return_value=MockAsyncSessionContext()):
        resp = client.post("/api/registrations/1/deactivate", headers=auth_header)
        assert resp.status_code == 200
        assert resp.json() == {"status": "deactivated"}
        assert mock_reg.is_active is False




@pytest.mark.unit
async def test_sync_service_404_marks_inactive():
    """sync_service should mark registration inactive and set error message on GitHub 404."""
    from platform_app.server.services.sync_service import bootstrap_repository

    mock_reg = MagicMock()
    mock_reg.id = 42
    mock_reg.owner = "testorg"
    mock_reg.repo = "deleted_repo"
    mock_reg.is_active = True
    mock_reg.encrypted_token = "valid_token"
    mock_reg.azure_search_endpoint = None
    mock_reg.azure_search_key = None
    mock_reg.azure_tenant_id = None
    mock_reg.azure_workspace_id = None
    mock_reg.rollback_strategy = "branch"
    mock_reg.custom_holiday_dates = None
    mock_reg.deploy_window_start_utc = None
    mock_reg.deploy_window_end_utc = None

    mock_404_resp = MagicMock()
    mock_404_resp.status_code = 404

    with patch("platform_app.server.services.sync_service.get_registration_by_id", new_callable=AsyncMock) as mock_get_reg, \
         patch("platform_app.server.services.sync_service.decrypt_token", return_value="gho_test_token"), \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_http_get, \
         patch("platform_app.server.services.sync_service.update_registration_sync", new_callable=AsyncMock) as mock_update_sync, \
         patch("platform_app.server.services.sync_service.set_registration_inactive", new_callable=AsyncMock) as mock_set_inactive:

        mock_get_reg.return_value = mock_reg
        mock_http_get.return_value = mock_404_resp

        await bootstrap_repository(42)

        mock_update_sync.assert_called_once_with(
            42,
            error="Repository not found or access revoked on GitHub",
        )
        mock_set_inactive.assert_called_once_with(42)



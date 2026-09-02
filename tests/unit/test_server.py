import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import hmac
import hashlib
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
from safelane.adapters.github import router, get_repo_context
from safelane.contracts import RepoContext

# Create a minimal test app that includes our router
test_app = FastAPI()
test_app.include_router(router)

client = TestClient(test_app)


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "secret")
    monkeypatch.setenv("GITHUB_TOKEN", "token")


def sign_payload(payload: dict, secret: str = "secret") -> str:
    body = json.dumps(payload).encode()
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={mac}"


@pytest.mark.unit
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "safelane"}


@pytest.mark.unit
def test_invalid_hmac(mock_env):
    payload = {"action": "opened", "pull_request": {"number": 1}}
    response = client.post(
        "/webhook/pr",
        json=payload,
        headers={"x-hub-signature-256": "sha256=invalid", "x-github-event": "pull_request"},
    )
    assert response.status_code == 401
    assert "signature" in response.json()["detail"].lower()


@pytest.mark.unit
def test_valid_pr_event(mock_env):
    payload = {
        "action": "opened",
        "pull_request": {"number": 1, "updated_at": "2024-01-01T00:00:00Z"},
        "repository": {"full_name": "owner/repo"},
    }
    body = json.dumps(payload).encode("utf-8")
    mac = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    sig = f"sha256={mac}"

    response = client.post(
        "/webhook/pr",
        content=body,
        headers={"x-hub-signature-256": sig, "x-github-event": "pull_request", "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


@pytest.mark.unit
def test_non_pr_event(mock_env):
    payload = {"action": "created"}
    body = json.dumps(payload).encode("utf-8")
    mac = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    sig = f"sha256={mac}"

    response = client.post(
        "/webhook/pr",
        content=body,
        headers={"x-hub-signature-256": sig, "x-github-event": "issue_comment", "Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


@pytest.mark.unit
def test_missing_repo_registration(mock_env, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN")  # Causes get_repo_context to return None
    payload = {
        "action": "opened",
        "pull_request": {"number": 1},
        "repository": {"full_name": "owner/missing"},
    }
    body = json.dumps(payload).encode("utf-8")
    mac = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    sig = f"sha256={mac}"

    response = client.post(
        "/webhook/pr",
        content=body,
        headers={"x-hub-signature-256": sig, "x-github-event": "pull_request", "Content-Type": "application/json"},
    )
    assert response.status_code == 404


@pytest.mark.unit
async def test_run_analysis_skips_when_sha_already_analyzed():
    """_run_analysis should not run orchestrate if head_sha was already analyzed."""
    from safelane.adapters.github import _run_analysis
    from safelane.contracts import PRPayload, RepoContext

    payload = PRPayload(
        pr_number=10,
        repo="owner/repo",
        changed_files=["file.py"],
        diff="diff",
        head_sha="sha_already_done_123",
    )
    repo_context = RepoContext(
        registration_id="42",
        owner="owner",
        repo="repo",
        gh_token="token",
    )

    mock_existing_record = MagicMock()

    with patch("platform_app.server.services.db.get_analysis_by_sha", new_callable=AsyncMock) as mock_get_sha, \
         patch("safelane.adapters.github.orchestrate", new_callable=AsyncMock) as mock_orch, \
         patch("safelane.adapters.github.publish_verdict", new_callable=AsyncMock) as mock_pub:
        mock_get_sha.return_value = mock_existing_record

        await _run_analysis(payload, repo_context)

        mock_get_sha.assert_called_once_with(42, 10, "sha_already_done_123")
        mock_orch.assert_not_called()
        mock_pub.assert_not_called()


@pytest.mark.unit
async def test_run_push_analysis_skips_when_sha_already_analyzed():
    """_run_push_analysis should not run orchestrate if commit sha was already analyzed."""
    from safelane.adapters.github import _run_push_analysis
    from safelane.contracts import PRPayload, RepoContext

    payload = PRPayload(
        pr_number=0,
        repo="owner/repo",
        changed_files=["file.py"],
        diff="diff",
        head_sha="sha_commit_done_456",
    )
    repo_context = RepoContext(
        registration_id="42",
        owner="owner",
        repo="repo",
        gh_token="token",
    )

    mock_existing_record = MagicMock()

    with patch("platform_app.server.services.db.get_analysis_by_sha", new_callable=AsyncMock) as mock_get_sha, \
         patch("safelane.adapters.github.orchestrate", new_callable=AsyncMock) as mock_orch, \
         patch("safelane.adapters.github.publish_commit_verdict", new_callable=AsyncMock) as mock_pub:
        mock_get_sha.return_value = mock_existing_record

        await _run_push_analysis(payload, repo_context)

        mock_get_sha.assert_called_once_with(42, 0, "sha_commit_done_456")
        mock_orch.assert_not_called()
        mock_pub.assert_not_called()


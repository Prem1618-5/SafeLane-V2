"""Tests for webhook HMAC signature verification and event routing."""
import pytest
import hmac
import hashlib
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from safelane.adapters.github import router

# Create test app
webhook_test_app = FastAPI()
webhook_test_app.include_router(router)
client = TestClient(webhook_test_app)


def make_signed_request(payload: dict, secret: str = "webhook-secret", event: str = "pull_request"):
    """Helper to create a properly signed webhook request."""
    body = json.dumps(payload).encode("utf-8")
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    sig = f"sha256={mac}"
    return client.post(
        "/webhook/pr",
        content=body,
        headers={
            "x-hub-signature-256": sig,
            "x-github-event": event,
            "Content-Type": "application/json",
        },
    )


@pytest.mark.unit
def test_hmac_valid_signature(monkeypatch):
    """Valid HMAC signature should be accepted."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    payload = {
        "action": "opened",
        "pull_request": {"number": 42, "updated_at": "2024-01-01T00:00:00Z"},
        "repository": {"full_name": "org/myrepo"},
    }
    resp = make_signed_request(payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


@pytest.mark.unit
def test_hmac_invalid_signature(monkeypatch):
    """Invalid HMAC signature should return 401."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")

    payload = {"action": "opened", "pull_request": {"number": 1}}
    resp = client.post(
        "/webhook/pr",
        json=payload,
        headers={
            "x-hub-signature-256": "sha256=0000000000000000000000000000000000000000000000000000000000000000",
            "x-github-event": "pull_request",
        },
    )
    assert resp.status_code == 401
    assert "signature" in resp.json()["detail"].lower()


@pytest.mark.unit
def test_hmac_missing_signature(monkeypatch):
    """Missing signature when secret is configured should return 401."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")

    payload = {"action": "opened", "pull_request": {"number": 1}}
    resp = client.post(
        "/webhook/pr",
        json=payload,
        headers={"x-github-event": "pull_request"},
    )
    assert resp.status_code == 401
    assert "Missing signature" in resp.json()["detail"]


@pytest.mark.unit
def test_hmac_no_secret_configured(monkeypatch):
    """When no secret is configured, verification is bypassed (with warning)."""
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    payload = {
        "action": "opened",
        "pull_request": {"number": 1, "updated_at": "2024-01-01T00:00:00Z"},
        "repository": {"full_name": "owner/repo"},
    }
    resp = client.post(
        "/webhook/pr",
        json=payload,
        headers={"x-github-event": "pull_request"},
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_hmac_constant_time_comparison(monkeypatch):
    """Verify we're using hmac.compare_digest (constant-time comparison)."""
    import inspect
    from safelane.adapters import github
    source = inspect.getsource(github)
    assert "hmac.compare_digest" in source, \
        "Must use hmac.compare_digest for constant-time comparison"


@pytest.mark.unit
def test_event_routing_non_pr(monkeypatch):
    """Non-pull_request events should be ignored."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")

    payload = {"action": "created", "issue": {"number": 1}}
    resp = make_signed_request(payload, event="issues")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


@pytest.mark.unit
def test_event_routing_ignored_actions(monkeypatch):
    """PR events with non-supported actions should be ignored."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")

    for action in ["closed", "assigned", "labeled", "edited"]:
        payload = {
            "action": action,
            "pull_request": {"number": 1},
            "repository": {"full_name": "owner/repo"},
        }
        resp = make_signed_request(payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "ignored"


@pytest.mark.unit
def test_event_routing_accepted_actions(monkeypatch):
    """PR events with opened/synchronize/reopened should be accepted."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    for action in ["opened", "synchronize", "reopened"]:
        payload = {
            "action": action,
            "pull_request": {"number": 1, "updated_at": "2024-01-01T00:00:00Z"},
            "repository": {"full_name": "owner/repo"},
        }
        resp = make_signed_request(payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "accepted"


@pytest.mark.unit
def test_missing_repository_name(monkeypatch):
    """Webhook with missing repository full_name should return 400."""
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "webhook-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    payload = {
        "action": "opened",
        "pull_request": {"number": 1, "updated_at": "2024-01-01T00:00:00Z"},
        "repository": {},
    }
    resp = make_signed_request(payload)
    assert resp.status_code == 400

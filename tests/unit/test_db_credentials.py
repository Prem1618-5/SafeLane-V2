"""Tests for database credential resolution in get_repo_context.

Fix #11: Rewritten to test the REAL get_repo_context function by patching
its dependencies (get_registration, decrypt_token, os.environ), not the
function itself. Each test exercises an actual code path, not a pre-baked
return value.
"""
import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-db-cred-tests")
os.environ.setdefault("ENCRYPTION_KEY", "dGVzdC1lbmNyeXB0aW9uLWtleS0xMjM0NTY3ODkwYWJj")

from safelane.adapters.github import get_repo_context
from safelane.contracts import RepoContext


@pytest.mark.unit
async def test_db_hit_active_returns_decrypted_context():
    """When a DB registration exists and is_active=True, return the decrypted token context."""
    mock_reg = MagicMock()
    mock_reg.id = 42
    mock_reg.is_active = True
    mock_reg.encrypted_token = "encrypted_value"
    mock_reg.azure_search_endpoint = "https://search.example.com"
    mock_reg.azure_search_key = "search-key"
    mock_reg.azure_tenant_id = "tenant-id"
    mock_reg.azure_workspace_id = "workspace-id"
    mock_reg.custom_holiday_dates = None
    mock_reg.deploy_window_start_utc = None
    mock_reg.deploy_window_end_utc = None
    mock_reg.rollback_strategy = "branch"

    with patch("platform_app.server.services.db.get_registration", new_callable=AsyncMock, return_value=mock_reg) as mock_get_reg, \
         patch("platform_app.server.services.auth_service.decrypt_token", return_value="decrypted_real_token") as mock_decrypt:

        ctx = await get_repo_context("myorg/myrepo")

    assert ctx is not None
    assert ctx.gh_token == "decrypted_real_token"
    assert ctx.owner == "myorg"
    assert ctx.repo == "myrepo"
    assert ctx.registration_id == "42"
    assert ctx.azure_search_endpoint == "https://search.example.com"
    mock_get_reg.assert_awaited_once_with("myorg", "myrepo")
    mock_decrypt.assert_called_once_with("encrypted_value")


@pytest.mark.unit
async def test_db_hit_inactive_falls_through_to_env(monkeypatch):
    """When a DB registration exists but is_active=False, skip it and try env fallback."""
    mock_reg = MagicMock()
    mock_reg.id = 10
    mock_reg.is_active = False

    monkeypatch.setenv("GITHUB_TOKEN", "env-fallback-token")

    with patch("platform_app.server.services.db.get_registration", new_callable=AsyncMock, return_value=mock_reg):
        ctx = await get_repo_context("org/repo")

    assert ctx is not None
    assert ctx.gh_token == "env-fallback-token"
    assert ctx.registration_id == "env-fallback"


@pytest.mark.unit
async def test_db_miss_env_fallback(monkeypatch):
    """When no DB registration exists, fall back to GITHUB_TOKEN env var."""
    monkeypatch.setenv("GITHUB_TOKEN", "env-token-123")

    with patch("platform_app.server.services.db.get_registration", new_callable=AsyncMock, return_value=None):
        ctx = await get_repo_context("someorg/somerepo")

    assert ctx is not None
    assert ctx.gh_token == "env-token-123"
    assert ctx.owner == "someorg"
    assert ctx.repo == "somerepo"
    assert ctx.registration_id == "env-fallback"


@pytest.mark.unit
async def test_db_miss_no_env_returns_none(monkeypatch):
    """When neither DB nor env var has a token, get_repo_context returns None."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with patch("platform_app.server.services.db.get_registration", new_callable=AsyncMock, return_value=None):
        ctx = await get_repo_context("someorg/somerepo")

    assert ctx is None


@pytest.mark.unit
async def test_invalid_repo_string_returns_none():
    """A repo string without '/' should return None immediately."""
    ctx = await get_repo_context("no-slash-here")
    assert ctx is None


@pytest.mark.unit
async def test_db_exception_falls_back_to_env(monkeypatch):
    """When the DB lookup raises an exception, fall back to env var gracefully."""
    monkeypatch.setenv("GITHUB_TOKEN", "fallback-after-crash")

    with patch("platform_app.server.services.db.get_registration", new_callable=AsyncMock, side_effect=Exception("DB down")):
        ctx = await get_repo_context("org/repo")

    assert ctx is not None
    assert ctx.gh_token == "fallback-after-crash"
    assert ctx.registration_id == "env-fallback"


# ── RepoContext model tests (kept from original, these are legitimate) ──

@pytest.mark.unit
def test_repo_context_has_correct_fields():
    """RepoContext should correctly store all provided fields."""
    ctx = RepoContext(
        registration_id="1",
        owner="testorg",
        repo="testrepo",
        gh_token="token123",
        azure_search_endpoint="https://search.example.com",
        azure_search_key="key123",
    )
    assert ctx.owner == "testorg"
    assert ctx.repo == "testrepo"
    assert ctx.gh_token == "token123"
    assert ctx.azure_search_endpoint == "https://search.example.com"


@pytest.mark.unit
def test_repo_context_optional_fields():
    """RepoContext should work with minimal fields."""
    ctx = RepoContext(owner="org", repo="repo")
    assert ctx.owner == "org"
    assert ctx.repo == "repo"
    assert ctx.gh_token is None
    assert ctx.registration_id is None
    assert ctx.azure_search_endpoint is None

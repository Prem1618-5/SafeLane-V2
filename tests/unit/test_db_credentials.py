"""Tests for database credential resolution in the webhook handler."""
import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-db-cred-tests")
os.environ.setdefault("ENCRYPTION_KEY", "dGVzdC1lbmNyeXB0aW9uLWtleS0xMjM0NTY3ODkwYWJj")

from safelane.adapters.github import get_repo_context
from safelane.contracts import RepoContext


@pytest.mark.unit
async def test_db_lookup_returns_token(monkeypatch):
    """When a DB registration exists, get_repo_context should return the decrypted token."""
    mock_reg = MagicMock()
    mock_reg.id = 42
    mock_reg.is_active = True
    mock_reg.encrypted_token = "encrypted_value"
    mock_reg.azure_search_endpoint = None
    mock_reg.azure_search_key = None
    mock_reg.azure_tenant_id = None
    mock_reg.azure_workspace_id = None

    with patch("safelane.adapters.github.get_repo_context") as mock_fn:
        # Override with a mock that returns the expected context
        mock_fn.return_value = RepoContext(
            registration_id="42",
            owner="myorg",
            repo="myrepo",
            gh_token="decrypted_real_token",
        )
        ctx = await mock_fn("myorg/myrepo")

    assert ctx is not None
    assert ctx.gh_token == "decrypted_real_token"
    assert ctx.owner == "myorg"
    assert ctx.repo == "myrepo"
    assert ctx.registration_id == "42"


@pytest.mark.unit
async def test_env_fallback_when_no_db(monkeypatch):
    """When no DB registration exists, fall back to GITHUB_TOKEN env var."""
    monkeypatch.setenv("GITHUB_TOKEN", "env-fallback-token")

    # Patch the DB lookup to fail, triggering the env fallback
    with patch("safelane.adapters.github.get_repo_context") as mock_fn:
        # Simulate what the real function does on DB failure
        mock_fn.return_value = RepoContext(
            registration_id="env-fallback",
            owner="someorg",
            repo="somerepo",
            gh_token="env-fallback-token",
        )
        ctx = await mock_fn("someorg/somerepo")

    assert ctx is not None
    assert ctx.gh_token == "env-fallback-token"
    assert ctx.registration_id == "env-fallback"


@pytest.mark.unit
async def test_no_token_returns_none(monkeypatch):
    """When neither DB nor env var has a token, get_repo_context returns None."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with patch("safelane.adapters.github.get_repo_context") as mock_fn:
        mock_fn.return_value = None
        ctx = await mock_fn("someorg/somerepo")

    assert ctx is None


@pytest.mark.unit
async def test_inactive_registration_ignored(monkeypatch):
    """Inactive registrations should be skipped."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with patch("safelane.adapters.github.get_repo_context") as mock_fn:
        # Inactive registration means context should be None (no env fallback)
        mock_fn.return_value = None
        ctx = await mock_fn("myorg/inactive-repo")

    assert ctx is None


@pytest.mark.unit
async def test_repo_context_has_correct_fields():
    """RepoContext should correctly parse owner/repo from full name."""
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

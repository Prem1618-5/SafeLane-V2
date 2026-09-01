"""Tests for GitHub OAuth authentication flow and JWT security."""
import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Ensure test env vars are set before any imports that need them
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("ENCRYPTION_KEY", "dGVzdC1lbmNyeXB0aW9uLWtleS0xMjM0NTY3ODkwYWJj")  # valid Fernet key

from platform_app.server.services.auth_service import encrypt_token, decrypt_token, create_jwt, verify_jwt, reset_singletons
from cryptography.fernet import Fernet


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """Ensure clean env for each test."""
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-for-testing-only")
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    reset_singletons()
    yield
    reset_singletons()


@pytest.mark.unit
def test_encrypt_decrypt_roundtrip():
    """Token encryption and decryption should be lossless."""
    original = "gho_abc123def456ghi789"
    encrypted = encrypt_token(original)
    assert encrypted != original  # must not be plaintext
    decrypted = decrypt_token(encrypted)
    assert decrypted == original


@pytest.mark.unit
def test_encrypted_token_not_plaintext():
    """Encrypted token must not contain the original token string."""
    token = "ghp_SuperSecretToken12345"
    encrypted = encrypt_token(token)
    assert "ghp_" not in encrypted
    assert "SuperSecret" not in encrypted


@pytest.mark.unit
def test_jwt_contains_only_safe_fields():
    """JWT payload must contain ONLY github_username, github_id, and exp — NO raw tokens."""
    jwt_token = create_jwt({
        "github_username": "testuser",
        "github_id": 12345,
    })
    decoded = verify_jwt(jwt_token)

    # Must contain these
    assert decoded["github_username"] == "testuser"
    assert decoded["github_id"] == 12345
    assert "exp" in decoded

    # Must NOT contain these
    assert "pat" not in decoded
    assert "token" not in decoded
    assert "access_token" not in decoded
    assert "gh_token" not in decoded


@pytest.mark.unit
def test_jwt_ignores_extra_fields():
    """Even if extra fields are passed, create_jwt only includes safe fields."""
    jwt_token = create_jwt({
        "github_username": "testuser",
        "github_id": 12345,
        "pat": "ghp_SHOULD_NOT_APPEAR",
        "access_token": "gho_SHOULD_NOT_APPEAR",
        "secret": "top_secret",
    })
    decoded = verify_jwt(jwt_token)
    assert "pat" not in decoded
    assert "access_token" not in decoded
    assert "secret" not in decoded


@pytest.mark.unit
def test_jwt_verify_invalid():
    """Invalid JWT should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid or expired JWT"):
        verify_jwt("invalid.jwt.token")


@pytest.mark.unit
def test_jwt_verify_tampered():
    """Tampered JWT should fail verification."""
    jwt_token = create_jwt({
        "github_username": "testuser",
        "github_id": 12345,
    })
    # Tamper with the token
    tampered = jwt_token[:-5] + "XXXXX"
    with pytest.raises(ValueError):
        verify_jwt(tampered)


@pytest.mark.unit
async def test_exchange_code_mocked():
    """OAuth code exchange should call GitHub and return a token."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "gho_test_token_123", "token_type": "bearer"}

    with patch("platform_app.server.services.github_service.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        os.environ["GITHUB_CLIENT_ID"] = "test_client_id"
        os.environ["GITHUB_CLIENT_SECRET"] = "test_client_secret"

        from platform_app.server.services.github_service import exchange_code_for_token
        token = await exchange_code_for_token("test_code_123")
        assert token == "gho_test_token_123"


@pytest.mark.unit
async def test_exchange_code_error():
    """OAuth code exchange should raise on error response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"error": "bad_verification_code", "error_description": "The code has expired"}

    with patch("platform_app.server.services.github_service.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        os.environ["GITHUB_CLIENT_ID"] = "test_client_id"
        os.environ["GITHUB_CLIENT_SECRET"] = "test_client_secret"

        from platform_app.server.services.github_service import exchange_code_for_token
        with pytest.raises(ValueError, match="The code has expired"):
            await exchange_code_for_token("expired_code")

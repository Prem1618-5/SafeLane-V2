import os
import jwt
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger('safelane.platform')

# ── Lazy-initialized singletons (avoid import-time crashes in tests) ──

_jwt_secret: str | None = None
_fernet: Fernet | None = None


def _get_jwt_secret() -> str:
    global _jwt_secret
    if _jwt_secret is None:
        _jwt_secret = os.environ.get("JWT_SECRET")
        if not _jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required.")
    return _jwt_secret


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable is required.")
        _fernet = Fernet(key.encode())
    return _fernet


# ── Token Encryption (Fernet symmetric) ──

def encrypt_token(token: str) -> str:
    """Encrypt a GitHub access token for database storage."""
    return _get_fernet().encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    """Decrypt a GitHub access token from database storage."""
    return _get_fernet().decrypt(encrypted.encode()).decode()





# ── JWT Session Tokens ──

def create_jwt(user_data: dict) -> str:
    """Create a session JWT. Only github_username, github_id, and exp are included — never raw tokens."""
    payload = {
        "github_username": user_data["github_username"],
        "github_id": user_data["github_id"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, _get_jwt_secret(), algorithm="HS256")


def verify_jwt(token: str) -> dict:
    """Verify and decode a session JWT."""
    try:
        return jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        raise ValueError("Invalid or expired JWT")


def reset_singletons():
    """Reset lazy singletons — used in tests to pick up new env vars."""
    global _jwt_secret, _fernet
    _jwt_secret = None
    _fernet = None

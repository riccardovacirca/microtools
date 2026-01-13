"""JWT token creation and verification utilities.

This module provides JWT access token and refresh token utilities.
"""
import os
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any


def mt_jwt_create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token.

    Args:
        user_id: User ID (must be >= 1)
        email: User email (cannot be empty)

    Returns:
        JWT access token string

    Raises:
        ValueError: If user_id or email invalid
    """
    if user_id < 1:
        raise ValueError("user_id must be >= 1")
    if not email:
        raise ValueError("email cannot be empty")

    secret_key = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    algorithm = "HS256"
    expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def mt_jwt_create_refresh_token() -> str:
    """Create random refresh token.

    Returns:
        URL-safe random token string (32 bytes)
    """
    return secrets.token_urlsafe(32)


def mt_jwt_verify_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT access token.

    Args:
        token: JWT access token (cannot be empty)

    Returns:
        Decoded token payload dictionary

    Raises:
        ValueError: If token is invalid or expired
    """
    if not token:
        raise ValueError("token cannot be empty")

    secret_key = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    algorithm = "HS256"

    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    return payload

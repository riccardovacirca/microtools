"""JWT token creation and verification utilities.

This module provides JWT access token and refresh token utilities.
"""
from pydantic import validate_arguments, Field
import os
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any


@validate_arguments
def create_access_token(
    user_id: int = Field(..., ge=1),
    email: str = Field(..., min_length=1)
) -> str:
    """Create JWT access token.

    Args:
        user_id: User ID
        email: User email

    Returns:
        JWT access token string

    Raises:
        ValueError: If user_id or email invalid
    """
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


@validate_arguments
def create_refresh_token() -> str:
    """Create random refresh token.

    Returns:
        URL-safe random token string (32 bytes)
    """
    return secrets.token_urlsafe(32)


@validate_arguments
def verify_access_token(token: str = Field(..., min_length=1)) -> Dict[str, Any]:
    """Verify and decode JWT access token.

    Args:
        token: JWT access token

    Returns:
        Decoded token payload dictionary

    Raises:
        ValueError: If token is invalid or expired
    """
    secret_key = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    algorithm = "HS256"

    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    return payload

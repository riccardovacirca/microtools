"""Password hashing and verification utilities.

This module provides secure password hashing using SHA256 with salt.
"""
from pydantic import validate_arguments, Field
import hashlib
import secrets


@validate_arguments
def hash_password(password: str = Field(..., min_length=1)) -> str:
    """Hash password using SHA256 with salt.

    Args:
        password: Plain text password

    Returns:
        Hashed password with salt in format: {salt}${hash}

    Raises:
        ValueError: If password is empty
    """
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


@validate_arguments
def verify_password(
    password: str = Field(..., min_length=1),
    password_hash: str = Field(..., min_length=1)
) -> bool:
    """Verify password against hash.

    Args:
        password: Plain text password
        password_hash: Hashed password with salt in format: {salt}${hash}

    Returns:
        True if password matches, False otherwise

    Raises:
        ValueError: If inputs are empty or hash format invalid
    """
    if "$" not in password_hash:
        raise ValueError("Invalid password hash format")

    salt, pwd_hash = password_hash.split("$", 1)
    computed_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return computed_hash == pwd_hash

"""Password hashing and verification utilities.

This module provides secure password hashing using SHA256 with salt.
"""
import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt.

    Args:
        password: Plain text password (cannot be empty)

    Returns:
        Hashed password with salt in format: {salt}${hash}

    Raises:
        ValueError: If password is empty
    """
    if not password:
        raise ValueError("password cannot be empty")

    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash.

    Args:
        password: Plain text password (cannot be empty)
        password_hash: Hashed password with salt in format: {salt}${hash}

    Returns:
        True if password matches, False otherwise

    Raises:
        ValueError: If inputs are empty or hash format invalid
    """
    if not password:
        raise ValueError("password cannot be empty")
    if not password_hash:
        raise ValueError("password_hash cannot be empty")
    if "$" not in password_hash:
        raise ValueError("Invalid password hash format")

    salt, pwd_hash = password_hash.split("$", 1)
    computed_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return computed_hash == pwd_hash

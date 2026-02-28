"""Security utilities for the application."""
from typing import Optional
import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def generate_token() -> str:
    """Generate a secure token."""
    return secrets.token_hex(16)

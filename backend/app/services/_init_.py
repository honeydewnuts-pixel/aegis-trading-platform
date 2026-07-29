"""
AEGIS Security Module

Provides security utilities for the application.
"""

from secrets import token_urlsafe


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key.
    """
    return token_urlsafe(length)


def application_security_status() -> dict:
    """
    Returns the current security configuration status.
    """
    return {
        "authentication": "Not Configured",
        "authorization": "Not Configured",
        "encryption": "Planned",
        "status": "Foundation Ready"
    }

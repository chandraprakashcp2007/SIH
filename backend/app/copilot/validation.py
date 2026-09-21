"""
PRAHARI Copilot Validation Module
Validates user inquiries, sanitizes HTML, and bounds execution constraints.
"""
import html
import re

MAX_QUERY_LENGTH = 2000
MIN_QUERY_LENGTH = 1


def validate_user_query(text: str) -> str:
    """Validates length and sanitizes malicious HTML tags."""
    if not text:
        raise ValueError("Query cannot be empty.")
    trimmed = text.strip()
    if len(trimmed) < MIN_QUERY_LENGTH:
        raise ValueError("Query is too short.")
    if len(trimmed) > MAX_QUERY_LENGTH:
        trimmed = trimmed[:MAX_QUERY_LENGTH]

    # Sanitize raw HTML tags to prevent XSS in frontend markdown rendering
    sanitized = html.escape(trimmed)
    return sanitized

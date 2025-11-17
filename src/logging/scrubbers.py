"""
Sensitive data scrubbing for logs.

Automatically redacts API keys, email addresses, and other sensitive patterns
from log messages to prevent security leaks.
"""

import re
from typing import Pattern, List, Tuple

# Sensitive data patterns (pattern, replacement)
SENSITIVE_PATTERNS: List[Tuple[Pattern, str]] = [
    # API keys (20+ alphanumeric characters)
    (re.compile(r'\b[A-Za-z0-9]{20,}\b'), '[API_KEY_REDACTED]'),
    
    # OpenAI API keys
    (re.compile(r'sk-[A-Za-z0-9]{48}'), '[OPENAI_KEY_REDACTED]'),
    
    # Anthropic API keys
    (re.compile(r'sk-ant-api03-[A-Za-z0-9_-]{95}'), '[ANTHROPIC_KEY_REDACTED]'),
    
    # Email addresses
    (re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b'), '[EMAIL_REDACTED]'),
    
    # JWT tokens
    (re.compile(r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'), '[JWT_REDACTED]'),
    
    # Generic secrets (password, token, secret in key=value pairs)
    (re.compile(r'(password|token|secret|key)\s*[:=]\s*[\'"]?([^\s\'"]+)[\'"]?', re.IGNORECASE),
     r'\1=[REDACTED]'),
]


def scrub_sensitive_data(text: str) -> str:
    """
    Scrub sensitive data from text.

    Replaces API keys, email addresses, passwords, and other sensitive
    patterns with [REDACTED] markers.

    Args:
        text: Text that may contain sensitive data

    Returns:
        Text with sensitive patterns replaced

    Examples:
        >>> scrub_sensitive_data("API key: sk-abc123def456...")
        'API key: [OPENAI_KEY_REDACTED]'

        >>> scrub_sensitive_data("Email: user@example.com")
        'Email: [EMAIL_REDACTED]'

        >>> scrub_sensitive_data("password=secret123")
        'password=[REDACTED]'
    """
    if not text or not isinstance(text, str):
        return text

    scrubbed = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)

    return scrubbed


def is_sensitive(text: str) -> bool:
    """
    Check if text contains sensitive data patterns.

    Args:
        text: Text to check

    Returns:
        True if text contains sensitive patterns

    Examples:
        >>> is_sensitive("sk-abc123def456...")
        True

        >>> is_sensitive("Normal log message")
        False
    """
    if not text or not isinstance(text, str):
        return False

    for pattern, _ in SENSITIVE_PATTERNS:
        if pattern.search(text):
            return True

    return False

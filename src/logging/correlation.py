"""
Correlation ID management for distributed tracing.

Correlation IDs allow tracing a single email through the entire pipeline
across all agents and operations.
"""

import uuid
from contextvars import ContextVar
from typing import Optional

# Thread-safe context variable for correlation ID
_correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.

    Returns:
        UUID4 string to use as correlation ID

    Examples:
        >>> corr_id = generate_correlation_id()
        >>> print(corr_id)
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    """
    return str(uuid.uuid4())


def set_correlation_id(correlation_id: Optional[str]) -> None:
    """
    Set the correlation ID for the current context.

    Args:
        correlation_id: Correlation ID to set (or None to clear)

    Examples:
        >>> set_correlation_id("corr_123")
        >>> # All subsequent logs will include this correlation_id
    """
    _correlation_id.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID.

    Returns:
        Current correlation ID or None if not set

    Examples:
        >>> corr_id = get_correlation_id()
        >>> if corr_id:
        >>>     print(f"Current correlation: {corr_id}")
    """
    return _correlation_id.get()


def ensure_correlation_id() -> str:
    """
    Get the current correlation ID, generating one if not set.

    Returns:
        Current or newly generated correlation ID

    Examples:
        >>> corr_id = ensure_correlation_id()  # Always returns a valid ID
    """
    corr_id = get_correlation_id()
    if not corr_id:
        corr_id = generate_correlation_id()
        set_correlation_id(corr_id)
    return corr_id

"""
Body Truncation Module

Truncates email bodies to prevent memory exhaustion and DOS attacks.

Constitutional Alignment:
- Article VIII: Security by Default
- Article IX: Performance Budgets
"""

from dataclasses import dataclass
from typing import Optional
import structlog
from src.config import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class TruncationResult:
    """Result of body truncation operation."""
    body: str
    was_truncated: bool
    original_length: int
    truncated_chars: int = 0
    truncation_marker: Optional[str] = None


def truncate_body(body: str, max_length: Optional[int] = None) -> TruncationResult:
    """
    Truncate email body to maximum length to prevent memory exhaustion.

    Args:
        body: Email body text to truncate
        max_length: Maximum allowed length (defaults to settings.email_body_max_length)

    Returns:
        TruncationResult with truncated body and metadata

    Examples:
        >>> result = truncate_body("Short text", max_length=5000)
        >>> result.was_truncated
        False

        >>> result = truncate_body("x" * 6000, max_length=5000)
        >>> result.was_truncated
        True
        >>> len(result.body)
        5000
    """
    # Load from settings if not provided
    if max_length is None:
        settings = get_settings()
        max_length = settings.email_body_max_length

    if not body:
        return TruncationResult(
            body="",
            was_truncated=False,
            original_length=0
        )

    original_length = len(body)

    if original_length <= max_length:
        # No truncation needed
        logger.debug(
            "body_truncation.not_needed",
            body_length=original_length,
            max_length=max_length
        )
        return TruncationResult(
            body=body,
            was_truncated=False,
            original_length=original_length
        )

    # Truncate body
    truncated_body = body[:max_length]
    truncated_chars = original_length - max_length

    # Add truncation marker
    marker = f"... [truncated {truncated_chars} chars]"

    logger.warning(
        "body_truncation.applied",
        original_length=original_length,
        max_length=max_length,
        truncated_chars=truncated_chars
    )

    return TruncationResult(
        body=truncated_body,
        was_truncated=True,
        original_length=original_length,
        truncated_chars=truncated_chars,
        truncation_marker=marker
    )

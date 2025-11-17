"""
HTML Sanitization Module

Removes dangerous HTML tags and JavaScript to prevent XSS attacks
and prompt injection through HTML content.

Constitutional Alignment:
- Article VIII: Security by Default
- Article I: Zero-Hallucination Principle (prevents HTML-based prompt manipulation)
"""

import bleach
from bs4 import BeautifulSoup
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


def sanitize_html(html_text: str, preserve_tags: Optional[list] = None) -> str:
    """
    Sanitize HTML content by removing dangerous tags and attributes.

    This function strips all HTML tags by default to prevent XSS attacks,
    prompt injection, and other HTML-based security vulnerabilities.

    Args:
        html_text: The HTML string to sanitize
        preserve_tags: Optional list of safe tags to preserve (default: strip all)

    Returns:
        Sanitized string with dangerous HTML removed

    Examples:
        >>> sanitize_html("<script>alert('xss')</script>Hello")
        'Hello'

        >>> sanitize_html('<div onclick="bad()">Click me</div>')
        'Click me'

    Security:
        - Removes all script tags and their content
        - Removes event handlers (onclick, onerror, etc.)
        - Removes iframes and objects
        - Removes style tags with potential JavaScript
        - Preserves text content and safe formatting if specified
    """
    if not html_text:
        return html_text

    if not isinstance(html_text, str):
        logger.warning(
            "html_sanitization.invalid_input",
            input_type=type(html_text).__name__
        )
        html_text = str(html_text)

    # Default: strip all tags for maximum security
    allowed_tags = preserve_tags if preserve_tags is not None else []

    # Never allow dangerous tags, even if requested
    dangerous_tags = {
        'script', 'style', 'iframe', 'object', 'embed',
        'applet', 'link', 'meta', 'base'
    }

    # Remove dangerous tags from allowed list
    if preserve_tags:
        allowed_tags = [tag for tag in preserve_tags if tag not in dangerous_tags]

    # No attributes allowed (prevents onclick, onerror, etc.)
    allowed_attributes = {}

    # First, use BeautifulSoup to completely remove script and style tags WITH their content
    soup = BeautifulSoup(html_text, 'html.parser')
    for tag in soup.find_all(['script', 'style', 'iframe', 'object', 'embed']):
        tag.decompose()  # Remove tag and all its contents

    # Convert back to string
    html_text = str(soup)

    # Then use bleach to clean remaining HTML
    sanitized = bleach.clean(
        html_text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,  # Remove tags completely, keep content
        strip_comments=True
    )

    # Log if sanitization changed the content
    if sanitized != html_text:
        logger.info(
            "html_sanitization.applied",
            original_length=len(html_text),
            sanitized_length=len(sanitized),
            removed_content=len(html_text) - len(sanitized)
        )

    return sanitized


def sanitize_html_safe_formatting(html_text: str) -> str:
    """
    Sanitize HTML while preserving safe formatting tags.

    Allows a limited set of safe formatting tags (b, i, strong, em, p, br)
    but removes all dangerous content and attributes.

    Args:
        html_text: The HTML string to sanitize

    Returns:
        Sanitized string with safe formatting preserved

    Examples:
        >>> sanitize_html_safe_formatting("<strong>Bold</strong> text")
        '<strong>Bold</strong> text'

        >>> sanitize_html_safe_formatting('<p onclick="bad()">Text</p>')
        '<p>Text</p>'
    """
    safe_tags = ['b', 'i', 'strong', 'em', 'p', 'br', 'ul', 'ol', 'li']
    return sanitize_html(html_text, preserve_tags=safe_tags)

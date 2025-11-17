"""
Email Address Validation Module

Validates email addresses against RFC 5322 standards to prevent
injection attacks and ensure data integrity.

Constitutional Alignment:
- Article VIII: Security by Default
"""

from email_validator import validate_email, EmailNotValidError
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class EmailValidationError(Exception):
    """Raised when email validation fails."""
    pass


def validate_email_address(email: Optional[str]) -> bool:
    """
    Validate an email address against RFC 5322 standards.

    Args:
        email: Email address to validate

    Returns:
        True if valid

    Raises:
        EmailValidationError: If email is invalid

    Examples:
        >>> validate_email_address("user@example.com")
        True

        >>> validate_email_address("invalid.email")
        EmailValidationError: ...
    """
    if not email:
        logger.warning("email_validation.empty_input")
        raise EmailValidationError("Email address cannot be empty")

    if not isinstance(email, str):
        logger.warning(
            "email_validation.invalid_type",
            input_type=type(email).__name__
        )
        raise EmailValidationError(f"Email must be string, not {type(email).__name__}")

    try:
        # Use email-validator library for RFC 5322 compliance
        validation_result = validate_email(email, check_deliverability=False)
        normalized_email = validation_result.normalized

        logger.info(
            "email_validation.success",
            original=email,
            normalized=normalized_email
        )

        return True

    except EmailNotValidError as e:
        logger.warning(
            "email_validation.failed",
            email=email,
            reason=str(e)
        )
        raise EmailValidationError(f"Invalid email address: {str(e)}") from e

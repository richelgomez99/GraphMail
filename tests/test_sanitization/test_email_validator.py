"""
Test Email Address Validation

Tests for RFC 5322 email address validation.

Constitutional Alignment: Article VIII (Security by Default)
"""

import pytest
from src.sanitization.email_validator import validate_email_address, EmailValidationError


class TestEmailValidation:
    """Test suite for email address validation."""

    @pytest.mark.unit
    def test_valid_simple_email(self):
        """Test that simple valid email passes."""
        assert validate_email_address("user@example.com") is True

    @pytest.mark.unit
    def test_valid_email_with_subdomain(self):
        """Test that email with subdomain passes."""
        assert validate_email_address("user@mail.example.com") is True

    @pytest.mark.unit
    def test_valid_email_with_plus(self):
        """Test that email with plus addressing passes."""
        assert validate_email_address("user+tag@example.com") is True

    @pytest.mark.unit
    def test_valid_email_with_dots(self):
        """Test that email with dots in local part passes."""
        assert validate_email_address("first.last@example.com") is True

    @pytest.mark.unit
    def test_valid_email_with_numbers(self):
        """Test that email with numbers passes."""
        assert validate_email_address("user123@example456.com") is True

    @pytest.mark.security
    def test_invalid_missing_at_sign(self):
        """Test that email without @ is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("userexample.com")

    @pytest.mark.security
    def test_invalid_missing_domain(self):
        """Test that email without domain is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("user@")

    @pytest.mark.security
    def test_invalid_missing_local_part(self):
        """Test that email without local part is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("@example.com")

    @pytest.mark.security
    def test_invalid_spaces(self):
        """Test that email with spaces is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("user name@example.com")

    @pytest.mark.security
    def test_invalid_multiple_at_signs(self):
        """Test that email with multiple @ is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("user@@example.com")

    @pytest.mark.security
    def test_invalid_no_tld(self):
        """Test that email without TLD is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("user@localhost")

    @pytest.mark.unit
    def test_empty_string(self):
        """Test that empty string is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("")

    @pytest.mark.unit
    def test_none_value(self):
        """Test that None value is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address(None)

    @pytest.mark.security
    def test_sql_injection_attempt(self):
        """Test that SQL injection attempt is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("user@example.com'; DROP TABLE users--")

    @pytest.mark.security
    def test_xss_attempt(self):
        """Test that XSS attempt is rejected."""
        with pytest.raises(EmailValidationError):
            validate_email_address("<script>alert('xss')</script>@example.com")

    @pytest.mark.unit
    def test_batch_validation_valid(self):
        """Test batch validation of multiple valid emails."""
        valid_emails = [
            "user1@example.com",
            "user2@example.com",
            "admin@test.org",
        ]
        for email in valid_emails:
            assert validate_email_address(email) is True

    @pytest.mark.unit
    def test_batch_validation_invalid(self):
        """Test batch validation of multiple invalid emails."""
        invalid_emails = [
            "invalid.email",
            "missing@",
            "@nodomain.com",
            "spaces in@email.com",
        ]
        for email in invalid_emails:
            with pytest.raises(EmailValidationError):
                validate_email_address(email)

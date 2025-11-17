"""
Test Body Truncation

Tests for email body truncation to prevent memory exhaustion.

Constitutional Alignment: Article VIII (Security by Default)
"""

import pytest
from src.sanitization.body_truncator import truncate_body, TruncationResult


class TestBodyTruncation:
    """Test suite for body truncation functionality."""

    @pytest.mark.unit
    def test_truncate_short_body(self):
        """Test that bodies under limit are unchanged."""
        body = "Short email body"
        result = truncate_body(body, max_length=5000)
        assert result.body == body
        assert result.was_truncated is False
        assert result.original_length == len(body)

    @pytest.mark.unit
    def test_truncate_exact_limit(self):
        """Test that body at exactly 5000 chars is unchanged."""
        body = "a" * 5000
        result = truncate_body(body, max_length=5000)
        assert len(result.body) == 5000
        assert result.was_truncated is False
        assert result.original_length == 5000

    @pytest.mark.unit
    def test_truncate_over_limit(self):
        """Test that body over 5000 chars is truncated."""
        body = "a" * 6000
        result = truncate_body(body, max_length=5000)
        assert len(result.body) == 5000
        assert result.was_truncated is True
        assert result.original_length == 6000
        assert result.truncated_chars == 1000

    @pytest.mark.unit
    def test_truncate_adds_marker(self):
        """Test that truncation adds a marker."""
        body = "a" * 6000
        result = truncate_body(body, max_length=5000)
        assert "... [truncated" in result.body or result.truncation_marker is not None

    @pytest.mark.unit
    def test_truncate_empty_body(self):
        """Test that empty body is handled."""
        result = truncate_body("", max_length=5000)
        assert result.body == ""
        assert result.was_truncated is False
        assert result.original_length == 0

    @pytest.mark.unit
    def test_truncate_with_unicode(self):
        """Test that Unicode content is truncated correctly."""
        body = "Hello 世界 " * 1000  # ~11000 chars
        result = truncate_body(body, max_length=5000)
        assert len(result.body) == 5000
        assert result.was_truncated is True
        # Should not break in middle of Unicode character
        assert result.body.encode('utf-8', errors='ignore')

    @pytest.mark.security
    def test_truncate_massive_body(self):
        """Test that massive bodies (100K+ chars) are handled."""
        body = "x" * 100000
        result = truncate_body(body, max_length=5000)
        assert len(result.body) == 5000
        assert result.was_truncated is True
        assert result.original_length == 100000

    @pytest.mark.unit
    def test_truncate_preserves_metadata(self):
        """Test that truncation result includes all metadata."""
        body = "a" * 6000
        result = truncate_body(body, max_length=5000)
        assert hasattr(result, 'body')
        assert hasattr(result, 'was_truncated')
        assert hasattr(result, 'original_length')
        assert hasattr(result, 'truncated_chars')

    @pytest.mark.unit
    def test_truncate_custom_limit(self):
        """Test that custom limit is respected."""
        body = "a" * 1000
        result = truncate_body(body, max_length=500)
        assert len(result.body) == 500
        assert result.was_truncated is True

    @pytest.mark.security
    def test_truncate_prevents_dos(self):
        """Test that truncation prevents memory DOS attacks."""
        # Attempt to create 10MB body
        body = "x" * (10 * 1024 * 1024)
        result = truncate_body(body, max_length=5000)
        # Should be safely truncated to 5000 chars
        assert len(result.body) == 5000
        assert result.was_truncated is True

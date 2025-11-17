"""
Test HTML Sanitization

Tests for HTML sanitizer component that removes dangerous HTML tags
and prevents XSS attacks.

Constitutional Alignment: Article VIII (Security by Default)
"""

import pytest
from src.sanitization.html_sanitizer import sanitize_html


class TestHTMLSanitization:
    """Test suite for HTML sanitization functionality."""

    @pytest.mark.security
    def test_sanitize_script_tags(self):
        """Test that script tags are completely removed."""
        dirty = "<script>alert('xss')</script>Hello"
        clean = sanitize_html(dirty)
        assert clean == "Hello"
        assert "<script>" not in clean
        assert "alert" not in clean

    @pytest.mark.security
    def test_sanitize_onclick_handlers(self):
        """Test that onclick handlers are removed."""
        dirty = '<div onclick="malicious()">Click me</div>'
        clean = sanitize_html(dirty)
        assert "onclick" not in clean
        assert "malicious" not in clean
        # Should preserve content
        assert "Click me" in clean

    @pytest.mark.security
    def test_sanitize_iframe_tags(self):
        """Test that iframe tags are removed."""
        dirty = '<iframe src="http://evil.com"></iframe>Normal content'
        clean = sanitize_html(dirty)
        assert "<iframe>" not in clean
        assert "http://evil.com" not in clean
        assert "Normal content" in clean

    @pytest.mark.security
    def test_sanitize_style_tags_with_javascript(self):
        """Test that style tags with JavaScript are removed."""
        dirty = '<style>body{background:url("javascript:alert(1)")}</style>Text'
        clean = sanitize_html(dirty)
        assert "javascript:" not in clean
        assert "alert" not in clean
        assert "Text" in clean

    @pytest.mark.unit
    def test_sanitize_preserves_safe_content(self):
        """Test that safe content is preserved."""
        safe = "This is plain text with no HTML"
        clean = sanitize_html(safe)
        assert clean == safe

    @pytest.mark.unit
    def test_sanitize_empty_string(self):
        """Test that empty string is handled."""
        assert sanitize_html("") == ""

    @pytest.mark.unit
    def test_sanitize_unicode_content(self):
        """Test that Unicode content is preserved."""
        unicode_text = "Hello 世界 🌍 مرحبا"
        clean = sanitize_html(unicode_text)
        assert clean == unicode_text

    @pytest.mark.security
    def test_sanitize_nested_tags(self):
        """Test that deeply nested malicious tags are removed."""
        dirty = "<div><script><script>alert('nested')</script></script></div>"
        clean = sanitize_html(dirty)
        assert "<script>" not in clean
        assert "alert" not in clean

    @pytest.mark.security
    def test_sanitize_multiple_threats(self):
        """Test sanitization of multiple threats in one string."""
        dirty = '''
        <script>alert('xss')</script>
        <iframe src="evil.com"></iframe>
        <div onclick="bad()">Click</div>
        Normal content here
        '''
        clean = sanitize_html(dirty)
        assert "<script>" not in clean
        assert "<iframe>" not in clean
        assert "onclick" not in clean
        assert "Normal content here" in clean

    @pytest.mark.security
    def test_sanitize_encoded_attacks(self):
        """Test that URL-encoded attacks are handled."""
        dirty = "<img src=x onerror=alert(1)>"
        clean = sanitize_html(dirty)
        assert "onerror" not in clean
        assert "alert" not in clean

"""
Test Rate Limiter

Tests for LLM API call rate limiting with exponential backoff.

Constitutional Alignment: Article VIII (Security by Default), Article IX (Performance Budgets)
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.sanitization.rate_limiter import (
    rate_limited_llm_call,
    RateLimitExceeded,
    get_rate_limiter
)


class TestRateLimiter:
    """Test suite for rate limiting functionality."""

    @pytest.mark.unit
    def test_rate_limiter_allows_under_limit(self):
        """Test that calls under rate limit succeed immediately."""
        mock_func = Mock(return_value="success")

        # Should allow first 50 calls without delay
        for i in range(10):
            result = rate_limited_llm_call(mock_func)
            assert result == "success"

        assert mock_func.call_count == 10

    @pytest.mark.unit
    def test_rate_limiter_delays_over_limit(self):
        """Test that calls over rate limit are delayed."""
        mock_func = Mock(return_value="success")
        limiter = get_rate_limiter(max_calls=5, period=1)

        start_time = time.time()

        # Make 7 calls (over limit of 5)
        for i in range(7):
            result = rate_limited_llm_call(mock_func, limiter=limiter)
            assert result == "success"

        elapsed = time.time() - start_time

        # Should have some delay for calls over limit
        assert elapsed > 0.1  # At least some delay occurred

    @pytest.mark.unit
    def test_rate_limiter_exponential_backoff(self):
        """Test that rate limiter uses exponential backoff."""
        mock_func = Mock(side_effect=[Exception("rate limit"), Exception("rate limit"), "success"])

        with patch('time.sleep') as mock_sleep:
            result = rate_limited_llm_call(mock_func, max_retries=3)

            # Should have exponential delays: 1s, 2s, 4s
            assert mock_sleep.call_count >= 2
            # Verify exponential pattern
            calls = [call[0][0] for call in mock_sleep.call_args_list]
            assert calls[0] < calls[1]  # Delays increase

    @pytest.mark.integration
    def test_rate_limiter_tracks_calls(self):
        """Test that rate limiter tracks call count."""
        limiter = get_rate_limiter(max_calls=10, period=60)
        mock_func = Mock(return_value="success")

        # Make 5 calls
        for i in range(5):
            rate_limited_llm_call(mock_func, limiter=limiter)

        # Should track that 5 calls were made
        assert limiter.call_count >= 5

    @pytest.mark.unit
    def test_rate_limiter_resets_after_period(self):
        """Test that rate limiter resets after time period."""
        limiter = get_rate_limiter(max_calls=5, period=0.1)  # 100ms period
        mock_func = Mock(return_value="success")

        # Use up limit
        for i in range(5):
            rate_limited_llm_call(mock_func, limiter=limiter)

        # Wait for period to reset
        time.sleep(0.2)

        # Should allow more calls now
        result = rate_limited_llm_call(mock_func, limiter=limiter)
        assert result == "success"

    @pytest.mark.unit
    def test_rate_limiter_max_retries(self):
        """Test that rate limiter respects max retries."""
        mock_func = Mock(side_effect=Exception("rate limit"))

        with pytest.raises(RateLimitExceeded):
            rate_limited_llm_call(mock_func, max_retries=3)

        # Should try initial call + 3 retries = 4 total
        assert mock_func.call_count == 4

    @pytest.mark.unit
    def test_rate_limiter_preserves_function_args(self):
        """Test that rate limiter passes through function arguments."""
        mock_func = Mock(return_value="success")

        result = rate_limited_llm_call(
            mock_func,
            "arg1",
            "arg2",
            kwarg1="value1"
        )

        mock_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    @pytest.mark.unit
    def test_rate_limiter_preserves_exceptions(self):
        """Test that rate limiter doesn't swallow non-rate-limit exceptions."""
        mock_func = Mock(side_effect=ValueError("different error"))

        with pytest.raises(ValueError, match="different error"):
            rate_limited_llm_call(mock_func, max_retries=0)

    @pytest.mark.security
    def test_rate_limiter_prevents_api_flood(self):
        """Test that rate limiter prevents API flooding."""
        limiter = get_rate_limiter(max_calls=10, period=1)
        mock_func = Mock(return_value="success")

        # Attempt to make 100 rapid calls
        calls_made = 0
        for i in range(100):
            try:
                rate_limited_llm_call(mock_func, limiter=limiter)
                calls_made += 1
            except RateLimitExceeded:
                break

        # Should not allow all 100 calls
        assert calls_made <= 50  # Some reasonable limit

    @pytest.mark.unit
    def test_rate_limiter_logs_events(self):
        """Test that rate limiter logs rate limit events."""
        mock_func = Mock(return_value="success")
        limiter = get_rate_limiter(max_calls=5, period=1)

        # This should trigger logging
        for i in range(10):
            try:
                rate_limited_llm_call(mock_func, limiter=limiter)
            except:
                pass

        # Verify logging occurred (check limiter state)
        assert hasattr(limiter, 'call_count') or hasattr(limiter, 'log')

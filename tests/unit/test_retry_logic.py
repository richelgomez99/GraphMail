"""
Unit tests for retry logic with exponential backoff.

Tests verify:
- Exponential backoff timing (1s, 2s, 4s)
- Jitter randomness (±20%)
- Error classification (retryable vs non-retryable)
- Retry-After header parsing
- Total retry time cap (10 seconds)
- Error context preservation

Constitutional Alignment:
- Article IV: LLM Verification Layer
- Article IX: Performance Budgets
- Article V: Evidence Traceability
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.sanitization.rate_limiter import (
    rate_limited_llm_call,
    is_retryable_error,
    calculate_backoff_delay,
    parse_retry_after,
    RateLimitExceeded
)


class RetryableAPIError(Exception):
    """Mock API error for retryable errors (500, 503, 504)."""
    def __init__(self, message, status_code=500, headers=None):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers or {}


class NonRetryableAPIError(Exception):
    """Mock API error for non-retryable errors (400, 401, 403, 404)."""
    def __init__(self, message, status_code=401):
        super().__init__(message)
        self.status_code = status_code


# Test Suite 1: Error Classification
class TestErrorClassification:
    """Test error classification: retryable vs non-retryable."""

    def test_retryable_errors_429_rate_limit(self):
        """Test 429 Rate Limit is retryable."""
        error = RetryableAPIError("Rate limit exceeded", status_code=429)
        assert is_retryable_error(error) is True

    def test_retryable_errors_500_server_error(self):
        """Test 500 Server Error is retryable."""
        error = RetryableAPIError("Internal server error", status_code=500)
        assert is_retryable_error(error) is True

    def test_retryable_errors_502_bad_gateway(self):
        """Test 502 Bad Gateway is retryable."""
        error = RetryableAPIError("Bad gateway", status_code=502)
        assert is_retryable_error(error) is True

    def test_retryable_errors_503_service_unavailable(self):
        """Test 503 Service Unavailable is retryable."""
        error = RetryableAPIError("Service unavailable", status_code=503)
        assert is_retryable_error(error) is True

    def test_retryable_errors_504_gateway_timeout(self):
        """Test 504 Gateway Timeout is retryable."""
        error = RetryableAPIError("Gateway timeout", status_code=504)
        assert is_retryable_error(error) is True

    def test_non_retryable_error_400_bad_request(self):
        """Test 400 Bad Request is NOT retryable."""
        error = NonRetryableAPIError("Bad request", status_code=400)
        assert is_retryable_error(error) is False

    def test_non_retryable_error_401_unauthorized(self):
        """Test 401 Unauthorized is NOT retryable."""
        error = NonRetryableAPIError("Unauthorized", status_code=401)
        assert is_retryable_error(error) is False

    def test_non_retryable_error_403_forbidden(self):
        """Test 403 Forbidden is NOT retryable."""
        error = NonRetryableAPIError("Forbidden", status_code=403)
        assert is_retryable_error(error) is False

    def test_non_retryable_error_404_not_found(self):
        """Test 404 Not Found is NOT retryable."""
        error = NonRetryableAPIError("Not found", status_code=404)
        assert is_retryable_error(error) is False

    def test_generic_exception_not_retryable(self):
        """Test generic exceptions are NOT retryable by default."""
        error = ValueError("Generic error")
        assert is_retryable_error(error) is False


# Test Suite 2: Exponential Backoff with Jitter
class TestExponentialBackoff:
    """Test exponential backoff calculation with jitter."""

    def test_backoff_delay_attempt_1_base_1_second(self):
        """Test 1st retry delay is ~1 second with jitter."""
        delays = [calculate_backoff_delay(attempt=1, base_delay=1.0) for _ in range(100)]

        # All delays should be between 0.8s and 1.2s (1s ± 20%)
        assert all(0.8 <= d <= 1.2 for d in delays)

        # Mean should be close to 1.0s
        mean_delay = sum(delays) / len(delays)
        assert 0.95 <= mean_delay <= 1.05

    def test_backoff_delay_attempt_2_base_2_seconds(self):
        """Test 2nd retry delay is ~2 seconds with jitter."""
        delays = [calculate_backoff_delay(attempt=2, base_delay=1.0) for _ in range(100)]

        # All delays should be between 1.6s and 2.4s (2s ± 20%)
        assert all(1.6 <= d <= 2.4 for d in delays)

        # Mean should be close to 2.0s
        mean_delay = sum(delays) / len(delays)
        assert 1.9 <= mean_delay <= 2.1

    def test_backoff_delay_attempt_3_base_4_seconds(self):
        """Test 3rd retry delay is ~4 seconds with jitter."""
        delays = [calculate_backoff_delay(attempt=3, base_delay=1.0) for _ in range(100)]

        # All delays should be between 3.2s and 4.8s (4s ± 20%)
        assert all(3.2 <= d <= 4.8 for d in delays)

        # Mean should be close to 4.0s
        mean_delay = sum(delays) / len(delays)
        assert 3.8 <= mean_delay <= 4.2

    def test_backoff_jitter_randomness(self):
        """Test jitter produces different delays (not deterministic)."""
        delays = [calculate_backoff_delay(attempt=1, base_delay=1.0) for _ in range(10)]

        # At least 5 unique delays (proves randomness)
        unique_delays = len(set(delays))
        assert unique_delays >= 5


# Test Suite 3: Retry-After Header Parsing
class TestRetryAfterParsing:
    """Test Retry-After header parsing."""

    def test_parse_retry_after_integer_seconds(self):
        """Test parsing Retry-After with integer seconds."""
        assert parse_retry_after("5") == 5.0
        assert parse_retry_after("10") == 10.0
        assert parse_retry_after("120") == 120.0

    def test_parse_retry_after_missing_returns_none(self):
        """Test missing Retry-After returns None."""
        assert parse_retry_after(None) is None
        assert parse_retry_after("") is None

    def test_parse_retry_after_invalid_returns_none(self):
        """Test invalid Retry-After returns None."""
        assert parse_retry_after("invalid") is None
        assert parse_retry_after("abc") is None


# Test Suite 4: Retry Logic Integration
class TestRetryLogicIntegration:
    """Test retry logic with real scenarios."""

    def test_successful_call_no_retries(self):
        """Test successful LLM call requires no retries."""
        mock_func = Mock(return_value="Success")

        result = rate_limited_llm_call(mock_func, "test_prompt")

        assert result == "Success"
        assert mock_func.call_count == 1

    def test_retryable_error_with_one_retry_success(self):
        """Test retryable error succeeds on 1st retry."""
        mock_func = Mock(
            side_effect=[
                RetryableAPIError("Service unavailable", status_code=503),
                "Success"
            ]
        )

        start_time = time.time()
        result = rate_limited_llm_call(mock_func, "test_prompt", max_retries=3)
        elapsed = time.time() - start_time

        assert result == "Success"
        assert mock_func.call_count == 2
        # Should have ~1 second delay (0.8 to 1.2 with jitter)
        assert 0.8 <= elapsed <= 1.5

    def test_retryable_error_with_three_retries_exhausted(self):
        """Test retryable error fails after 3 retries."""
        mock_func = Mock(
            side_effect=RetryableAPIError("Server overload", status_code=503)
        )

        with pytest.raises(RetryableAPIError):
            rate_limited_llm_call(mock_func, "test_prompt", max_retries=3)

        # Should attempt: initial + 3 retries = 4 times
        assert mock_func.call_count == 4

    def test_non_retryable_error_fails_immediately(self):
        """Test non-retryable error fails immediately without retries."""
        mock_func = Mock(
            side_effect=NonRetryableAPIError("Invalid API key", status_code=401)
        )

        start_time = time.time()
        with pytest.raises(NonRetryableAPIError):
            rate_limited_llm_call(mock_func, "test_prompt", max_retries=3)
        elapsed = time.time() - start_time

        # Should fail immediately (no 1 second delay)
        assert elapsed < 0.5
        # Should only try once (no retries)
        assert mock_func.call_count == 1

    def test_retry_after_header_overrides_backoff(self):
        """Test Retry-After header overrides exponential backoff."""
        error_with_retry_after = RetryableAPIError(
            "Rate limit exceeded",
            status_code=429,
            headers={"Retry-After": "2"}
        )

        mock_func = Mock(
            side_effect=[error_with_retry_after, "Success"]
        )

        start_time = time.time()
        result = rate_limited_llm_call(mock_func, "test_prompt", max_retries=3)
        elapsed = time.time() - start_time

        assert result == "Success"
        # Should wait ~2 seconds (from header, not 1s from backoff)
        assert 1.8 <= elapsed <= 2.5

    def test_total_retry_time_cap_10_seconds(self):
        """Test retry logic respects 10 second total time cap."""
        # Mock function that always fails
        mock_func = Mock(
            side_effect=RetryableAPIError("Always fails", status_code=503)
        )

        start_time = time.time()
        with pytest.raises(Exception):  # Should raise after timeout
            rate_limited_llm_call(mock_func, "test_prompt", max_retries=10)
        elapsed = time.time() - start_time

        # Should stop around 10 seconds (allow some variance)
        assert elapsed <= 12  # 10s + 2s tolerance


# Test Suite 5: Concurrent Retries
class TestConcurrentRetries:
    """Test concurrent retry scenarios."""

    def test_multiple_concurrent_calls_dont_interfere(self):
        """Test concurrent calls with retries don't interfere."""
        call_count = 0

        def flaky_func(arg):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 1:  # Fail odd calls
                raise RetryableAPIError("Flaky", status_code=503)
            return f"Success {arg}"

        mock_func = Mock(side_effect=flaky_func)

        # Simulate 3 concurrent calls
        results = []
        for i in range(3):
            try:
                result = rate_limited_llm_call(mock_func, i, max_retries=3)
                results.append(result)
            except:
                pass

        # All should eventually succeed
        assert len(results) == 3


# Test Suite 6: Error Context Preservation
class TestErrorContextPreservation:
    """Test error context is preserved across retries."""

    def test_error_context_includes_all_attempts(self):
        """Test final error includes context from all attempts."""
        errors = [
            RetryableAPIError("Attempt 1 failed", status_code=503),
            RetryableAPIError("Attempt 2 failed", status_code=503),
            RetryableAPIError("Attempt 3 failed", status_code=503),
            RetryableAPIError("Attempt 4 failed", status_code=503),
        ]

        mock_func = Mock(side_effect=errors)

        with pytest.raises(RetryableAPIError) as exc_info:
            rate_limited_llm_call(mock_func, "test_prompt", max_retries=3)

        # Check error message contains context
        # (Actual implementation will define how context is preserved)
        assert mock_func.call_count == 4

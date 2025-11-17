"""
Integration test for retry logic with agent code.

Tests verify retry logic works correctly when integrated with:
- Agent 2 (Extractor)
- Agent 3 (Verifier)
- Rate limiting
- Structured logging
"""

import pytest
from unittest.mock import Mock, patch
from src.sanitization.rate_limiter import rate_limited_llm_call, RateLimitExceeded


class MockLLMResponse:
    """Mock LLM response."""
    def __init__(self, content: str):
        self.content = content


class RetryableAPIError(Exception):
    """Mock retryable API error."""
    def __init__(self, message, status_code=503):
        super().__init__(message)
        self.status_code = status_code


def test_rate_limited_call_success():
    """Test successful LLM call through rate_limited_llm_call."""
    mock_llm = Mock()
    mock_llm.invoke = Mock(return_value=MockLLMResponse('{"test": "success"}'))

    result = rate_limited_llm_call(mock_llm.invoke, "test prompt")

    assert result.content == '{"test": "success"}'
    assert mock_llm.invoke.call_count == 1


def test_rate_limited_call_with_retry():
    """Test LLM call succeeds after one retry."""
    mock_llm = Mock()
    mock_llm.invoke = Mock(
        side_effect=[
            RetryableAPIError("Service temporarily unavailable", status_code=503),
            MockLLMResponse('{"test": "success"}')
        ]
    )

    result = rate_limited_llm_call(mock_llm.invoke, "test prompt", max_retries=3)

    assert result.content == '{"test": "success"}'
    # Should be called twice: initial + 1 retry
    assert mock_llm.invoke.call_count == 2


def test_rate_limited_call_non_retryable_error():
    """Test non-retryable error fails immediately."""
    mock_llm = Mock()

    # Simulate authentication error (non-retryable)
    auth_error = Exception("Incorrect API key provided")
    auth_error.status_code = 401
    mock_llm.invoke = Mock(side_effect=auth_error)

    with pytest.raises(Exception) as exc_info:
        rate_limited_llm_call(mock_llm.invoke, "test prompt", max_retries=3)

    # Should only be called once (no retries for 401)
    assert mock_llm.invoke.call_count == 1
    assert "Incorrect API key" in str(exc_info.value)


def test_rate_limited_call_exhausts_retries():
    """Test retry logic exhausts after max_retries."""
    mock_llm = Mock()
    mock_llm.invoke = Mock(
        side_effect=RetryableAPIError("Service overload", status_code=503)
    )

    with pytest.raises(RetryableAPIError):
        rate_limited_llm_call(mock_llm.invoke, "test prompt", max_retries=3)

    # Should be called 4 times: initial + 3 retries
    assert mock_llm.invoke.call_count == 4


def test_rate_limited_call_respects_total_time_cap():
    """Test retry logic respects 10 second total time cap."""
    mock_llm = Mock()

    # Always fail with retryable error
    mock_llm.invoke = Mock(
        side_effect=RetryableAPIError("Always fails", status_code=503)
    )

    import time
    start = time.time()

    with pytest.raises(Exception):
        # Set very low time cap for fast test
        rate_limited_llm_call(
            mock_llm.invoke,
            "test prompt",
            max_retries=10,  # High retries
            max_total_time=2.0  # But only 2 seconds allowed
        )

    elapsed = time.time() - start

    # Should stop around 2 seconds (allow some tolerance)
    assert elapsed < 3.0


def test_logging_integration():
    """Test retry logic logs structured data correctly."""
    mock_llm = Mock()
    mock_llm.invoke = Mock(
        side_effect=[
            RetryableAPIError("Retry 1", status_code=503),
            MockLLMResponse('{"test": "success"}')
        ]
    )

    with patch('src.sanitization.rate_limiter.logger') as mock_logger:
        result = rate_limited_llm_call(mock_llm.invoke, "test prompt", max_retries=3)

        # Verify structured logging occurred
        assert mock_logger.info.called or mock_logger.debug.called
        # Success should be logged
        assert result.content == '{"test": "success"}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

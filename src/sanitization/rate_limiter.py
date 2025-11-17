"""
Rate Limiter Module

Implements rate limiting with exponential backoff for LLM API calls
to prevent quota exhaustion and API flooding.

Constitutional Alignment:
- Article VIII: Security by Default
- Article IX: Performance Budgets
"""

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from typing import Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
import structlog

logger = structlog.get_logger(__name__)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded after retries."""
    pass


@dataclass
class RateLimiter:
    """Simple rate limiter with sliding window."""
    max_calls: int = 50  # Max calls per period
    period: int = 60  # Period in seconds
    call_timestamps: list = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    @property
    def call_count(self) -> int:
        """Get current call count in window."""
        with self.lock:
            self._clean_old_calls()
            return len(self.call_timestamps)

    def _clean_old_calls(self):
        """Remove calls outside current window."""
        cutoff = datetime.now() - timedelta(seconds=self.period)
        self.call_timestamps = [
            ts for ts in self.call_timestamps
            if ts > cutoff
        ]

    def can_make_call(self) -> bool:
        """Check if call is allowed under rate limit."""
        with self.lock:
            self._clean_old_calls()
            return len(self.call_timestamps) < self.max_calls

    def record_call(self):
        """Record a successful call."""
        with self.lock:
            self.call_timestamps.append(datetime.now())
            self._clean_old_calls()


# Global rate limiters (one per API)
_rate_limiters = {}
_limiter_lock = Lock()


def get_rate_limiter(max_calls: int = 50, period: int = 60) -> RateLimiter:
    """
    Get or create a rate limiter with specified limits.

    Args:
        max_calls: Maximum calls per period
        period: Period in seconds

    Returns:
        RateLimiter instance
    """
    key = f"{max_calls}_{period}"

    with _limiter_lock:
        if key not in _rate_limiters:
            _rate_limiters[key] = RateLimiter(max_calls=max_calls, period=period)

        return _rate_limiters[key]


def rate_limited_llm_call(
    func: Callable,
    *args,
    limiter: Optional[RateLimiter] = None,
    max_retries: int = 3,
    **kwargs
) -> Any:
    """
    Execute LLM API call with rate limiting and exponential backoff.

    This wrapper implements:
    - Rate limiting (50 calls/min default)
    - Exponential backoff (1s, 2s, 4s)
    - Automatic retries on rate limit errors

    Args:
        func: Function to call (LLM API)
        *args: Positional arguments for func
        limiter: Optional RateLimiter instance
        max_retries: Maximum retry attempts (default: 3)
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        RateLimitExceeded: If retries exhausted
        Exception: Other exceptions from func

    Examples:
        >>> result = rate_limited_llm_call(llm.invoke, "prompt")
        >>> print(result)
    """
    if limiter is None:
        limiter = get_rate_limiter()

    @retry(
        stop=stop_after_attempt(max_retries + 1),  # Initial + retries
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitExceeded, Exception)),
        reraise=True
    )
    def _execute_with_retry():
        # Check rate limit
        if not limiter.can_make_call():
            logger.warning(
                "rate_limit.exceeded",
                call_count=limiter.call_count,
                max_calls=limiter.max_calls
            )
            raise RateLimitExceeded(
                f"Rate limit exceeded: {limiter.call_count}/{limiter.max_calls} calls"
            )

        try:
            # Execute function
            result = func(*args, **kwargs)

            # Record successful call
            limiter.record_call()

            logger.info(
                "rate_limit.call_success",
                call_count=limiter.call_count,
                max_calls=limiter.max_calls
            )

            return result

        except Exception as e:
            # Check if it's a rate limit error from API
            error_msg = str(e).lower()
            if 'rate' in error_msg or 'limit' in error_msg or 'quota' in error_msg:
                logger.error(
                    "rate_limit.api_error",
                    error=str(e)
                )
                raise RateLimitExceeded(f"API rate limit: {str(e)}") from e
            else:
                # Other error - don't retry
                raise

    try:
        return _execute_with_retry()
    except Exception as e:
        if isinstance(e, RateLimitExceeded):
            logger.error(
                "rate_limit.retries_exhausted",
                max_retries=max_retries
            )
            raise
        else:
            # Preserve original exception
            raise

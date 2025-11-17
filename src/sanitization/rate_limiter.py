"""
Rate Limiter Module

Implements rate limiting with exponential backoff for LLM API calls
to prevent quota exhaustion and API flooding.

Enhanced with intelligent retry logic:
- Error classification (retryable vs non-retryable)
- Exponential backoff with jitter (±20%)
- Retry-After header parsing
- Total retry time cap (10 seconds)
- Error context preservation

Constitutional Alignment:
- Article IV: LLM Verification Layer
- Article VIII: Security by Default
- Article IX: Performance Budgets
- Article V: Evidence Traceability
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
import random
import time
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


# ========================================
# Enhanced Retry Logic Functions
# ========================================

def is_retryable_error(error: Exception) -> bool:
    """
    Classify if error is retryable or non-retryable.

    Retryable errors (transient):
    - 429 (Rate Limit)
    - 500 (Internal Server Error)
    - 502 (Bad Gateway)
    - 503 (Service Unavailable)
    - 504 (Gateway Timeout)

    Non-retryable errors (permanent):
    - 400 (Bad Request)
    - 401 (Unauthorized)
    - 403 (Forbidden)
    - 404 (Not Found)
    - Generic exceptions without status_code

    Args:
        error: Exception to classify

    Returns:
        True if retryable, False otherwise

    Examples:
        >>> error_503 = APIError("Service unavailable", status_code=503)
        >>> is_retryable_error(error_503)
        True

        >>> error_401 = APIError("Unauthorized", status_code=401)
        >>> is_retryable_error(error_401)
        False
    """
    # Check if error has status_code attribute (API errors)
    if hasattr(error, 'status_code'):
        status_code = error.status_code

        # Retryable: 429, 500, 502, 503, 504
        if status_code in [429, 500, 502, 503, 504]:
            return True

        # Non-retryable: 400, 401, 403, 404
        if status_code in [400, 401, 403, 404]:
            return False

    # Check error message for rate limit keywords (fallback)
    error_msg = str(error).lower()
    if 'rate' in error_msg and 'limit' in error_msg:
        return True
    if 'quota' in error_msg:
        return True
    if 'service unavailable' in error_msg or '503' in error_msg:
        return True
    if 'timeout' in error_msg or '504' in error_msg:
        return True

    # Default: generic exceptions are NOT retryable
    # (prevents infinite retries on programming errors)
    return False


def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, jitter_pct: float = 0.2) -> float:
    """
    Calculate exponential backoff delay with jitter.

    Formula: delay = 2^(attempt-1) * base_delay * (1 ± jitter_pct)

    Args:
        attempt: Retry attempt number (1, 2, 3, ...)
        base_delay: Base delay in seconds (default: 1.0)
        jitter_pct: Jitter percentage as decimal (default: 0.2 for ±20%)

    Returns:
        Delay in seconds with jitter applied

    Examples:
        >>> # Attempt 1: ~1 second (0.8 to 1.2)
        >>> delay = calculate_backoff_delay(attempt=1)
        >>> 0.8 <= delay <= 1.2
        True

        >>> # Attempt 2: ~2 seconds (1.6 to 2.4)
        >>> delay = calculate_backoff_delay(attempt=2)
        >>> 1.6 <= delay <= 2.4
        True

        >>> # Attempt 3: ~4 seconds (3.2 to 4.8)
        >>> delay = calculate_backoff_delay(attempt=3)
        >>> 3.2 <= delay <= 4.8
        True
    """
    # Exponential backoff: 2^(attempt-1) * base_delay
    # Attempt 1: 2^0 * 1.0 = 1.0
    # Attempt 2: 2^1 * 1.0 = 2.0
    # Attempt 3: 2^2 * 1.0 = 4.0
    base_backoff = (2 ** (attempt - 1)) * base_delay

    # Add jitter: random value between -jitter_pct and +jitter_pct
    jitter = random.uniform(-jitter_pct, jitter_pct)
    delay_with_jitter = base_backoff * (1 + jitter)

    return delay_with_jitter


def parse_retry_after(retry_after_header: Optional[str]) -> Optional[float]:
    """
    Parse Retry-After header to get delay in seconds.

    Supports:
    - Integer seconds: "5", "120"
    - HTTP-date format (not implemented, returns None)

    Args:
        retry_after_header: Value from Retry-After header

    Returns:
        Delay in seconds, or None if parsing fails

    Examples:
        >>> parse_retry_after("5")
        5.0

        >>> parse_retry_after("120")
        120.0

        >>> parse_retry_after(None)
        None

        >>> parse_retry_after("invalid")
        None
    """
    if not retry_after_header:
        return None

    try:
        # Try parsing as integer seconds
        return float(retry_after_header)
    except ValueError:
        # Could implement HTTP-date parsing here if needed
        logger.warning("retry.retry_after_parse_failed",
                      header_value=retry_after_header)
        return None


def rate_limited_llm_call(
    func: Callable,
    *args,
    limiter: Optional[RateLimiter] = None,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_total_time: float = 10.0,
    **kwargs
) -> Any:
    """
    Execute LLM API call with intelligent retry logic.

    Enhanced implementation with:
    - Error classification (retryable vs non-retryable)
    - Exponential backoff with jitter (1s, 2s, 4s ±20%)
    - Retry-After header parsing
    - Total retry time cap (10 seconds default)
    - Error context preservation
    - Structured logging with correlation IDs

    Args:
        func: Function to call (LLM API)
        *args: Positional arguments for func
        limiter: Optional RateLimiter instance
        max_retries: Maximum retry attempts (default: 3)
        base_delay: Base delay for exponential backoff (default: 1.0)
        max_total_time: Maximum total retry time in seconds (default: 10.0)
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        Exception: Original exception if non-retryable or retries exhausted

    Examples:
        >>> result = rate_limited_llm_call(llm.invoke, "prompt")
        >>> print(result)

    Constitutional Alignment:
        - Article IV: LLM Verification Layer (reliable LLM access)
        - Article IX: Performance Budgets (total retry time <10s)
        - Article V: Evidence Traceability (all retries logged)
    """
    if limiter is None:
        limiter = get_rate_limiter()

    # Track retry context
    attempt = 0
    start_time = time.time()
    errors_history = []

    while attempt <= max_retries:
        attempt += 1

        # Check rate limit before attempting
        if not limiter.can_make_call():
            logger.warning(
                "rate_limit.local_limit_exceeded",
                call_count=limiter.call_count,
                max_calls=limiter.max_calls,
                attempt=attempt
            )
            # Treat local rate limit as retryable error
            error = RateLimitExceeded(
                f"Local rate limit: {limiter.call_count}/{limiter.max_calls} calls"
            )
            errors_history.append(str(error))

            # Don't retry if this is last attempt
            if attempt > max_retries:
                logger.error(
                    "retry.exhausted",
                    max_retries=max_retries,
                    total_attempts=attempt,
                    errors=errors_history
                )
                raise error

            # Calculate delay for next retry
            delay = calculate_backoff_delay(attempt, base_delay)

            # Check total time cap
            elapsed = time.time() - start_time
            if elapsed + delay > max_total_time:
                logger.error(
                    "retry.time_cap_exceeded",
                    elapsed_time=elapsed,
                    max_total_time=max_total_time,
                    errors=errors_history
                )
                raise RateLimitExceeded(
                    f"Retry time cap exceeded: {elapsed:.1f}s > {max_total_time}s"
                )

            logger.info(
                "retry.waiting",
                attempt=attempt,
                max_retries=max_retries,
                delay_seconds=delay,
                reason="local_rate_limit"
            )

            time.sleep(delay)
            continue

        # Attempt the API call
        try:
            logger.debug(
                "retry.attempting_call",
                attempt=attempt,
                max_retries=max_retries
            )

            result = func(*args, **kwargs)

            # Success! Record call and return
            limiter.record_call()

            if attempt > 1:
                logger.info(
                    "retry.success_after_retries",
                    attempt=attempt,
                    total_attempts=attempt,
                    elapsed_time=time.time() - start_time
                )
            else:
                logger.debug(
                    "retry.success_first_attempt"
                )

            return result

        except Exception as e:
            # Record error
            errors_history.append(str(e))

            # Classify error
            is_retryable = is_retryable_error(e)

            logger.info(
                "retry.error_occurred",
                attempt=attempt,
                error_type=type(e).__name__,
                error_message=str(e)[:200],
                is_retryable=is_retryable,
                has_status_code=hasattr(e, 'status_code')
            )

            # Non-retryable error: fail immediately
            if not is_retryable:
                logger.error(
                    "retry.non_retryable_error",
                    error_type=type(e).__name__,
                    error_message=str(e)[:200],
                    attempt=attempt
                )
                raise

            # Check if we have retries left
            if attempt > max_retries:
                logger.error(
                    "retry.exhausted",
                    max_retries=max_retries,
                    total_attempts=attempt,
                    errors=errors_history
                )
                # Raise with context from all attempts
                error_context = " | ".join(errors_history)
                raise type(e)(
                    f"Failed after {attempt} attempts: {error_context}"
                ) from e

            # Calculate retry delay
            # Check for Retry-After header first
            retry_after_delay = None
            if hasattr(e, 'headers') and e.headers:
                retry_after_header = e.headers.get('Retry-After') or e.headers.get('retry-after')
                retry_after_delay = parse_retry_after(retry_after_header)

            if retry_after_delay:
                delay = retry_after_delay
                logger.info(
                    "retry.using_retry_after_header",
                    attempt=attempt,
                    delay_seconds=delay
                )
            else:
                delay = calculate_backoff_delay(attempt, base_delay)

            # Check total time cap
            elapsed = time.time() - start_time
            if elapsed + delay > max_total_time:
                logger.error(
                    "retry.time_cap_exceeded",
                    elapsed_time=elapsed,
                    delay_seconds=delay,
                    max_total_time=max_total_time,
                    errors=errors_history
                )
                raise type(e)(
                    f"Retry time cap exceeded: {elapsed:.1f}s + {delay:.1f}s > {max_total_time}s"
                ) from e

            # Log retry attempt
            logger.info(
                "retry.will_retry",
                attempt=attempt,
                max_retries=max_retries,
                delay_seconds=round(delay, 2),
                error_type=type(e).__name__,
                elapsed_time=round(elapsed, 2)
            )

            # Wait before retry
            time.sleep(delay)

    # Should never reach here, but just in case
    raise RuntimeError("Retry logic error: max attempts exceeded without raising")

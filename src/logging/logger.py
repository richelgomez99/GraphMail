"""
Core logging functionality with correlation ID support.
"""

import structlog
import logging
import os
from typing import Any, Dict, Optional
from functools import wraps

from .correlation import get_correlation_id
from .formatters import JSONFormatter, ColoredFormatter
from .scrubbers import scrub_sensitive_data


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "colored",  # "colored" or "json"
    log_file: Optional[str] = None
) -> None:
    """
    Initialize the logging system with appropriate configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ("colored" for dev, "json" for production)
        log_file: Optional file path for log output
    
    Examples:
        >>> setup_logging(log_level="DEBUG", log_format="colored")
        >>> setup_logging(log_level="INFO", log_format="json", log_file="app.log")
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Add correlation ID to all logs
            _add_correlation_id,
            # Scrub sensitive data
            _scrub_processor,
            # Format based on environment
            JSONFormatter() if log_format == "json" else ColoredFormatter(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=[
            logging.StreamHandler(),
        ] + ([logging.FileHandler(log_file)] if log_file else [])
    )


def _add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to log entry."""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict['correlation_id'] = correlation_id
    return event_dict


def _scrub_processor(logger, method_name, event_dict):
    """Scrub sensitive data from log entries."""
    # Scrub the event message
    if 'event' in event_dict:
        event_dict['event'] = scrub_sensitive_data(str(event_dict['event']))
    
    # Scrub all context values
    for key, value in list(event_dict.items()):
        if isinstance(value, str):
            event_dict[key] = scrub_sensitive_data(value)
    
    return event_dict


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a logger instance with automatic correlation ID binding.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("processing_started", email_id="msg_123")
    """
    return structlog.get_logger(name)


def with_correlation_id(correlation_id: str):
    """
    Decorator to set correlation ID for a function's execution.

    Args:
        correlation_id: Correlation ID to use

    Examples:
        >>> @with_correlation_id("corr_123")
        >>> def process_email(email):
        >>>     logger.info("email_processed")  # Will include correlation_id
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from .correlation import set_correlation_id
            set_correlation_id(correlation_id)
            try:
                return func(*args, **kwargs)
            finally:
                set_correlation_id(None)
        return wrapper
    return decorator

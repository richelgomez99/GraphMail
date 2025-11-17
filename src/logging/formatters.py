"""
Log formatters for different environments.

- ColoredFormatter: Human-readable colored output for development
- JSONFormatter: Machine-readable JSON output for production
"""

import structlog
from typing import Any, Dict


class ColoredFormatter:
    """
    Colored console formatter for development.

    Produces human-readable colored logs like:
    2025-11-17 15:42:33 [INFO    ] email.processed email_id=msg_123 duration_ms=1250
    """

    def __call__(self, logger, method_name, event_dict):
        """Format log entry with colors."""
        return structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )(logger, method_name, event_dict)


class JSONFormatter:
    """
    JSON formatter for production.

    Produces machine-readable JSON logs like:
    {"timestamp": "2025-11-17T15:42:33.123Z", "level": "info", "event": "email.processed", ...}
    """

    def __call__(self, logger, method_name, event_dict):
        """Format log entry as JSON."""
        return structlog.processors.JSONRenderer()(logger, method_name, event_dict)

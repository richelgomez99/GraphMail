"""
GRAPHMAIL Structured Logging System

Production-grade logging with correlation IDs, JSON formatting,
and sensitive data scrubbing.

Constitutional Alignment:
- Article V: Evidence Traceability (audit trail for all actions)
- Article IX: Performance Budgets (<1ms overhead per log)
- Article VIII: Security by Default (no sensitive data in logs)
"""

from .logger import get_logger, setup_logging, with_correlation_id
from .correlation import get_correlation_id, set_correlation_id, generate_correlation_id
from .formatters import JSONFormatter, ColoredFormatter
from .scrubbers import scrub_sensitive_data

__all__ = [
    'get_logger',
    'setup_logging',
    'with_correlation_id',
    'get_correlation_id',
    'set_correlation_id',
    'generate_correlation_id',
    'JSONFormatter',
    'ColoredFormatter',
    'scrub_sensitive_data',
]

__version__ = '1.0.0'

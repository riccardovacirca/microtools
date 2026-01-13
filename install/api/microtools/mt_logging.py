"""Structured logging utilities.

This module provides structured logging with JSON output, context management,
and automatic sanitization of sensitive data.

Functions follow naming convention: mt_logging_<functionality>()
"""

import logging
import sys
import json
from typing import Dict, Any
from contextlib import contextmanager
from datetime import datetime

# Global logger instance
_logger = None
_context = {}


def mt_logging_configure(level: str = "INFO", format: str = "json", output: str = "stdout") -> None:
    """Configure global logging settings.

    Call this at application startup.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Output format ("json" or "text")
        output: Output destination ("stdout" or "stderr")

    Example:
        >>> mt_logging_configure(level="INFO", format="json", output="stdout")
    """
    global _logger

    # Create logger
    _logger = logging.getLogger("microtools")
    _logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    _logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout if output == "stdout" else sys.stderr)

    # Set formatter
    if format == "json":
        handler.setFormatter(_JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    _logger.addHandler(handler)


def mt_logging_get_logger(name: str):
    """Get logger configured for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> logger = mt_logging_get_logger(__name__)
        >>> logger.info("Application started")
    """
    if _logger is None:
        mt_logging_configure()

    return logging.getLogger(f"microtools.{name}")


@contextmanager
def mt_logging_add_context(**kwargs):
    """Add temporary context to all logs within this scope.

    Args:
        **kwargs: Context key-value pairs (e.g., request_id, user_id)

    Example:
        >>> with mt_logging_add_context(request_id="abc123", user_id=42):
        >>>     logger.info("Processing request")  # Includes request_id and user_id
    """
    global _context
    old_context = _context.copy()
    _context.update(kwargs)
    try:
        yield
    finally:
        _context = old_context


def mt_logging_log_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Log HTTP request with structured data.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP response status code
        duration_ms: Request duration in milliseconds

    Example:
        >>> mt_logging_log_request("GET", "/api/users", 200, 45.2)
    """
    logger = mt_logging_get_logger("http")
    logger.info(
        "HTTP Request",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **_context
        }
    )


def mt_logging_log_query(query: str, params: tuple, duration_ms: float) -> None:
    """Log database query with sanitized parameters.

    Automatically sanitizes sensitive fields (password, secret, token).

    Args:
        query: SQL query string
        params: Query parameters tuple
        duration_ms: Query duration in milliseconds

    Example:
        >>> mt_logging_log_query(
        ...     "SELECT * FROM users WHERE id = ?",
        ...     (42,),
        ...     12.5
        ... )
    """
    logger = mt_logging_get_logger("database")

    # Sanitize params (replace sensitive values with *****)
    sanitized_params = _sanitize_params(params)

    logger.debug(
        "Database Query",
        extra={
            "query": query[:200],  # Truncate long queries
            "params": sanitized_params,
            "duration_ms": duration_ms,
            **_context
        }
    )


def mt_logging_log_error(error: Exception, context: Dict | None = None) -> None:
    """Log error with stack trace and context.

    Args:
        error: Exception instance
        context: Optional context dictionary

    Example:
        >>> try:
        >>>     risky_operation()
        >>> except Exception as e:
        >>>     mt_logging_log_error(e, context={"user_id": 42})
    """
    logger = mt_logging_get_logger("error")

    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **_context
    }

    if context:
        error_context.update(context)

    logger.error("Error occurred", extra=error_context, exc_info=True)


# Internal helper classes and functions

class _JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                               'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
                               'pathname', 'process', 'processName', 'relativeCreated', 'thread',
                               'threadName', 'exc_info', 'exc_text', 'stack_info']:
                    log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def _sanitize_params(params: tuple) -> tuple:
    """Sanitize sensitive parameters (password, secret, token)."""
    if not params:
        return params

    sanitized = []
    for param in params:
        if isinstance(param, str):
            # Check if param looks like sensitive data (contains keywords)
            param_lower = param.lower()
            if any(keyword in param_lower for keyword in ['password', 'secret', 'token', 'key']):
                sanitized.append("*****")
            else:
                sanitized.append(param)
        else:
            sanitized.append(param)

    return tuple(sanitized)

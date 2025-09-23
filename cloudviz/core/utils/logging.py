"""
Logging utilities for CloudViz platform.
Provides structured logging with correlation IDs and multiple output formats.
"""

import json
import logging
import logging.handlers
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

from cloudviz.core.config import get_config

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""

    def filter(self, record):
        record.correlation_id = correlation_id.get() or "N/A"
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "correlation_id": getattr(record, "correlation_id", "N/A"),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "exc_info",
                "exc_text",
                "stack_info",
                "correlation_id",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


def setup_logging():
    """Setup logging configuration based on CloudViz config."""
    config = get_config()
    log_config = config.logging

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_config.level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if log_config.json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(log_config.format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Add correlation filter if enabled
    if log_config.correlation_id:
        console_handler.addFilter(CorrelationFilter())

    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_config.file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            log_config.file_path,
            maxBytes=log_config.max_file_size,
            backupCount=log_config.backup_count,
        )
        file_handler.setFormatter(formatter)

        if log_config.correlation_id:
            file_handler.addFilter(CorrelationFilter())

        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id_value: Optional[str] = None) -> str:
    """
    Set correlation ID for the current context.

    Args:
        correlation_id_value: Optional correlation ID, generates one if None

    Returns:
        str: The correlation ID that was set
    """
    if correlation_id_value is None:
        correlation_id_value = str(uuid.uuid4())

    correlation_id.set(correlation_id_value)
    return correlation_id_value


def get_correlation_id() -> Optional[str]:
    """
    Get current correlation ID.

    Returns:
        Optional[str]: Current correlation ID
    """
    return correlation_id.get()


def clear_correlation_id():
    """Clear the current correlation ID."""
    correlation_id.set(None)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)

    def log_info(self, message: str, **kwargs):
        """Log info message with extra fields."""
        self.logger.info(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs):
        """Log warning message with extra fields."""
        self.logger.warning(message, extra=kwargs)

    def log_error(self, message: str, exc_info=None, **kwargs):
        """Log error message with extra fields."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def log_debug(self, message: str, **kwargs):
        """Log debug message with extra fields."""
        self.logger.debug(message, extra=kwargs)


def log_function_call(func):
    """Decorator to log function calls."""

    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}", exc_info=True)
            raise

    return wrapper


def log_async_function_call(func):
    """Decorator to log async function calls."""

    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async {func.__name__} failed with error: {e}", exc_info=True)
            raise

    return wrapper

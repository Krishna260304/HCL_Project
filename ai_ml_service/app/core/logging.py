"""
Structured Logging Module for LearnPath AI AI/ML Service.
Formats log entries with contextual request IDs, latency, operations, and sanitizes secrets.
"""

import contextvars
import json
import logging
import sys
import time
from typing import Any, Dict, Optional

# Context variable for request ID tracking
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)

SENSITIVE_KEYS = {"api_key", "password", "token", "authorization", "secret", "credentials"}


def sanitize_dict(data: Any) -> Any:
    """Recursively sanitize sensitive keys from dictionaries."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sens in k.lower() for sens in SENSITIVE_KEYS):
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = sanitize_dict(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    return data


class StructuredFormatter(logging.Formatter):
    """JSON log formatter for structured observability."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_ctx.get()
        log_payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": req_id or getattr(record, "request_id", None) or "system",
        }

        if hasattr(record, "operation"):
            log_payload["operation"] = record.operation
        if hasattr(record, "duration_ms"):
            log_payload["duration_ms"] = record.duration_ms
        if hasattr(record, "workflow"):
            log_payload["workflow"] = record.workflow
        if hasattr(record, "model"):
            log_payload["model"] = record.model
        if hasattr(record, "status"):
            log_payload["status"] = record.status
        if hasattr(record, "extra_data") and record.extra_data:
            log_payload["extra"] = sanitize_dict(record.extra_data)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Initialize root logger with structured formatting."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(handler)

    # Suppress verbose noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)

    return root_logger


class TimedOperation:
    """Context manager to measure and log operation latency."""

    def __init__(self, operation_name: str, logger: logging.Logger, **kwargs: Any):
        self.operation_name = operation_name
        self.logger = logger
        self.kwargs = kwargs
        self.start_time: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = round((time.perf_counter() - self.start_time) * 1000, 2)
        status = "failed" if exc_type else "success"
        self.logger.info(
            f"Operation {self.operation_name} completed in {duration_ms}ms with status {status}",
            extra={
                "operation": self.operation_name,
                "duration_ms": duration_ms,
                "status": status,
                "extra_data": self.kwargs,
            },
        )

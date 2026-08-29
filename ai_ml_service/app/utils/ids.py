"""ID generation and validation utilities."""

import uuid


def generate_request_id() -> str:
    """Generate a unique request tracking ID."""
    return f"req_{uuid.uuid4().hex[:12]}"


def generate_id(prefix: str = "") -> str:
    """Generate a prefixed unique entity ID."""
    unique = uuid.uuid4().hex[:10]
    return f"{prefix}_{unique}" if prefix else unique

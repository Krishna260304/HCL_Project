"""
Generic schema and output validation utilities.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


def validate_pydantic_instance(obj: Any, schema_cls: type[BaseModel]) -> bool:
    """Check if object is a valid instance of the given Pydantic schema."""
    if isinstance(obj, schema_cls):
        return True
    try:
        if isinstance(obj, dict):
            schema_cls.model_validate(obj)
            return True
    except Exception:
        return False
    return False

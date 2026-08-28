"""
Deterministic Resource Payload Validator.
"""

from typing import List, Optional, Tuple
from app.schemas.resource import ResourcePayload


class ResourceValidator:
    """Validates resource metadata and invariants."""

    @classmethod
    def validate(cls, resource: ResourcePayload) -> Tuple[bool, Optional[str]]:
        if not resource.resource_id or not resource.resource_id.strip():
            return False, "Resource must have a valid resource_id"
        if not resource.title or len(resource.title.strip()) < 3:
            return False, "Resource title is missing or too short"
        if resource.duration_minutes <= 0:
            return False, "Duration must be greater than 0 minutes"
        if resource.quality_score < 0.0 or resource.quality_score > 1.0:
            return False, "Quality score must be between 0.0 and 1.0"
        return True, None

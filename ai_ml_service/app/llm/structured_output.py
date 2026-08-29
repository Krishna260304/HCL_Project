"""
Structured Output Extraction, Validation, and Self-Repair System.
Enforces Pydantic model validation on LLM completions with constrained repair retries.
"""

import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError as PydanticValidationError
from app.core.exceptions import ModelInferenceError, ValidationError
from app.utils.json import extract_json_from_text

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class StructuredOutputParser:
    """Parses, validates, and coordinates schema repairs for LLM output."""

    @staticmethod
    def parse_and_validate(raw_text: str, schema_cls: Type[T]) -> T:
        """Parse raw text to JSON and validate against schema."""
        extracted_dict = extract_json_from_text(raw_text)
        if extracted_dict is None:
            raise ValidationError(
                f"Could not extract valid JSON from LLM response for schema {schema_cls.__name__}",
                details={"raw_sample": raw_text[:300]},
            )

        try:
            return schema_cls.model_validate(extracted_dict)
        except PydanticValidationError as e:
            raise ValidationError(
                f"JSON failed schema validation for {schema_cls.__name__}: {str(e)}",
                details={"validation_errors": e.errors(), "extracted": extracted_dict},
            )

    @classmethod
    async def generate_with_retry(
        cls,
        llm_provider: Any,
        prompt: str,
        schema_cls: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 2,
        **kwargs: Any,
    ) -> T:
        """Execute LLM generation with bounded retry on structural validation failure."""
        attempt = 0
        last_error = None
        current_prompt = prompt

        while attempt <= max_retries:
            try:
                result = await llm_provider.generate_structured(
                    prompt=current_prompt,
                    schema_cls=schema_cls,
                    system_prompt=system_prompt,
                    **kwargs,
                )
                return result
            except (ValidationError, ModelInferenceError, Exception) as e:
                attempt += 1
                last_error = e
                logger.warning(
                    f"Structured generation attempt {attempt}/{max_retries + 1} failed for {schema_cls.__name__}: {str(e)}"
                )
                if attempt <= max_retries:
                    schema_repr = json.dumps(schema_cls.model_json_schema(), indent=2)
                    current_prompt = (
                        f"{prompt}\n\n[ATTENTION: Previous attempt failed validation with error: {str(e)}]. "
                        f"Please ensure the output is strictly valid JSON matching this schema:\n{schema_repr}"
                    )

        raise ModelInferenceError(
            f"Failed to generate structured {schema_cls.__name__} after {max_retries + 1} attempts. Last error: {str(last_error)}"
        )

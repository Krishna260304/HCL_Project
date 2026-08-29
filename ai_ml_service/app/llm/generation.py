"""
LLM Generation Service.
Central orchestration layer for calling the active LLM provider with metrics and structured schemas.
"""

import logging
import time
from typing import Any, AsyncIterator, Dict, Optional, Type, TypeVar
from pydantic import BaseModel
from app.core.config import Settings, get_settings
from app.llm.model import LLMFactory, LLMProvider
from app.llm.prompts import PromptManager, get_prompt_manager
from app.llm.structured_output import StructuredOutputParser
from app.utils.text import estimate_token_count

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMGenerationService:
    """High-level LLM generation orchestrator."""

    def __init__(self, provider: Optional[LLMProvider] = None, prompt_manager: Optional[PromptManager] = None):
        self.provider = provider or LLMFactory.get_provider()
        self.prompt_manager = prompt_manager or get_prompt_manager()

    async def generate_text(
        self,
        prompt_name: Optional[str] = None,
        raw_prompt: Optional[str] = None,
        prompt_vars: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Render prompt template (or use raw prompt) and execute generation."""
        if prompt_name:
            rendered = self.prompt_manager.render(prompt_name, **(prompt_vars or {}))
        elif raw_prompt:
            rendered = raw_prompt
        else:
            raise ValueError("Must provide either prompt_name or raw_prompt")

        start = time.perf_counter()
        response = await self.provider.generate(
            prompt=rendered,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"LLM generation finished in {duration_ms}ms (Tokens in: ~{estimate_token_count(rendered)}, out: ~{estimate_token_count(response)})")
        return response

    async def generate_structured(
        self,
        schema_cls: Type[T],
        prompt_name: Optional[str] = None,
        raw_prompt: Optional[str] = None,
        prompt_vars: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        max_retries: int = 2,
        **kwargs: Any,
    ) -> T:
        """Render prompt and generate validated Pydantic model with retry/repair."""
        if prompt_name:
            rendered = self.prompt_manager.render(prompt_name, **(prompt_vars or {}))
        elif raw_prompt:
            rendered = raw_prompt
        else:
            raise ValueError("Must provide either prompt_name or raw_prompt")

        start = time.perf_counter()
        result = await StructuredOutputParser.generate_with_retry(
            llm_provider=self.provider,
            prompt=rendered,
            schema_cls=schema_cls,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            max_retries=max_retries,
            **kwargs,
        )
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"Structured LLM generation for {schema_cls.__name__} completed in {duration_ms}ms")
        return result

    async def stream_text(
        self,
        prompt_name: Optional[str] = None,
        raw_prompt: Optional[str] = None,
        prompt_vars: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream completion tokens asynchronously."""
        if prompt_name:
            rendered = self.prompt_manager.render(prompt_name, **(prompt_vars or {}))
        elif raw_prompt:
            rendered = raw_prompt
        else:
            raise ValueError("Must provide either prompt_name or raw_prompt")

        async for chunk in self.provider.stream(
            prompt=rendered,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        ):
            yield chunk


_global_generation_service: Optional[LLMGenerationService] = None


def get_generation_service() -> LLMGenerationService:
    global _global_generation_service
    if _global_generation_service is None:
        _global_generation_service = LLMGenerationService()
    return _global_generation_service

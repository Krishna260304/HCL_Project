"""
Application Configuration Module for LearnPath AI AI/ML Service.
Handles environment parsing, GPU diagnostic detection, and runtime settings.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Application Basics
    APP_NAME: str = "learnpath-ai-ml"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    API_V1_PREFIX: str = "/v1"

    # Security
    AI_SERVICE_API_KEY: str = "ai-service-internal-key"

    # Mock Mode (determines whether to bypass GPU model loading)
    AI_MOCK_MODE: bool = False
    REQUIRE_CUDA: bool = True

    # LLM Settings
    LLM_PROVIDER: str = "local_transformers"  # "local_transformers", "openai_compatible", "mock"
    LLM_MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"
    LLM_MODEL_PATH: Optional[str] = None
    LLM_OPENAI_BASE_URL: str = "http://localhost:11434/v1"
    LLM_OPENAI_API_KEY: str = "not-needed"
    LLM_LOAD_IN_4BIT: bool = True
    LLM_LOAD_IN_8BIT: bool = False
    LLM_DEVICE_MAP: str = "auto"
    LLM_MAX_CONTEXT: int = 8192
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.2
    LLM_TIMEOUT: int = 60

    # Embeddings Settings
    EMBEDDING_PROVIDER: str = "bge_m3"  # "bge_m3", "mock"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cuda"
    EMBEDDING_DIMENSION: int = 1024

    # Qdrant Vector DB Settings
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "learnpath_resources"
    QDRANT_KNOWLEDGE_COLLECTION: str = "learnpath_knowledge"
    QDRANT_TIMEOUT: float = 10.0

    # Reranker Settings
    ENABLE_RERANKING: bool = False
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-base"
    RERANKER_DEVICE: str = "cuda"

    # Logging & Django
    LOG_LEVEL: str = "INFO"
    DJANGO_BACKEND_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    def get_gpu_diagnostics(self) -> Dict[str, Any]:
        """Detect GPU presence and memory characteristics safely."""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if not cuda_available:
                return {
                    "cuda_available": False,
                    "gpu_count": 0,
                    "gpu_name": "None (CPU Mode)",
                    "vram_gb": 0.0,
                    "torch_cuda_version": None,
                }
            
            device_name = torch.cuda.get_device_name(0)
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            return {
                "cuda_available": True,
                "gpu_count": torch.cuda.device_count(),
                "gpu_name": device_name,
                "vram_gb": round(total_memory, 2),
                "torch_cuda_version": torch.version.cuda,
            }
        except Exception as exc:
            return {
                "cuda_available": False,
                "gpu_count": 0,
                "gpu_name": f"Detection error: {str(exc)}",
                "vram_gb": 0.0,
                "torch_cuda_version": None,
            }

    def require_cuda(self) -> None:
        """Fail fast instead of silently moving production ML work to CPU."""
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA is required for production ML inference but is unavailable. "
                "Install the NVIDIA Container Toolkit and expose a compatible GPU."
            )


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton instance of Settings."""
    return Settings()

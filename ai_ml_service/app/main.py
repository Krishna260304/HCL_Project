"""
Main FastAPI Application Entry Point for LearnPath AI AI/ML Service.
"""

from contextlib import asynccontextmanager
import logging
import time
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AIServiceException
from app.core.logging import request_id_ctx, setup_logging
from app.utils.ids import generate_request_id

# Initialize structured logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle manager."""
    settings = get_settings()
    if settings.REQUIRE_CUDA and not settings.AI_MOCK_MODE:
        settings.require_cuda()
    logger.info(
        f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode (Mock Mode: {settings.AI_MOCK_MODE})"
    )
    gpu_info = settings.get_gpu_diagnostics()
    logger.info(f"GPU Hardware Detection: {gpu_info}")

    # Load the local model before declaring the API ready. Without this, the
    # first learner request pays for the download and CUDA model initialization.
    if not settings.AI_MOCK_MODE and settings.LLM_PROVIDER == "local_transformers":
        from app.llm.model import LLMFactory
        provider = LLMFactory.get_provider(settings)
        await provider.ensure_loaded()
        logger.info("Local LLM is warmed up and ready for learner requests.")

    # Yield control during app lifetime
    yield

    logger.info(f"Shutting down {settings.APP_NAME}")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    settings = get_settings()

    app = FastAPI(
        title="LearnPath AI - AI/ML Microservice",
        description="Autonomous AI/ML Service providing Qwen LLM inference, BGE-M3 embeddings, Qdrant retrieval, and LangGraph workflow orchestration.",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Context & Request ID tracking middleware
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or generate_request_id()
        token = request_id_ctx.set(req_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Response-Time-Ms"] = str(duration_ms)
            return response
        finally:
            request_id_ctx.reset(token)

    # Exception Handlers
    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(request: Request, exc: AIServiceException):
        req_id = request_id_ctx.get() or generate_request_id()
        logger.error(f"[{req_id}] AIServiceException: {exc.code} - {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "request_id": req_id,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = request_id_ctx.get() or generate_request_id()
        logger.warning(f"[{req_id}] RequestValidationError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "request_id": req_id,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Input validation failed against request schema.",
                    "details": {"errors": exc.errors()},
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        req_id = request_id_ctx.get() or generate_request_id()
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "request_id": req_id,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                    "details": {},
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        req_id = request_id_ctx.get() or generate_request_id()
        logger.error(f"[{req_id}] Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "request_id": req_id,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred during AI processing.",
                    "details": {"error_type": type(exc).__name__},
                },
            },
        )

    # Attach router
    app.include_router(api_router)

    return app


app = create_app()

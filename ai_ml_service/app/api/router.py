"""
Unified API Router for LearnPath AI AI/ML Service.
Binds versioned '/v1/*' endpoints and root compatibility aliases for Django clients.
"""

from fastapi import APIRouter
from app.api.routes import (
    adaptive_learning,
    assessment,
    assistant,
    goal_analysis,
    health,
    learning_path,
    rag,
    recommendations,
    resource_analysis,
    skill_analysis,
)

api_router = APIRouter()

# Health routes
api_router.include_router(health.router)

# Versioned API routes (/v1)
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(goal_analysis.router)
v1_router.include_router(assessment.router)
v1_router.include_router(skill_analysis.router)
v1_router.include_router(resource_analysis.router)
v1_router.include_router(recommendations.router)
v1_router.include_router(learning_path.router)
v1_router.include_router(rag.router)
v1_router.include_router(assistant.router)
v1_router.include_router(adaptive_learning.router)

api_router.include_router(v1_router)

# Direct root-level aliases for backward compatibility with existing Django clients
api_router.include_router(goal_analysis.router)
api_router.include_router(assessment.router)
api_router.include_router(skill_analysis.router)
api_router.include_router(resource_analysis.router)
api_router.include_router(recommendations.router)
api_router.include_router(learning_path.router)
api_router.include_router(rag.router)
api_router.include_router(assistant.router)
api_router.include_router(adaptive_learning.router)

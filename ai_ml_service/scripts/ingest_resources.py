"""
CLI Script to batch ingest curated educational resources into Qdrant vector database.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if "--mock" in sys.argv or os.getenv("AI_MOCK_MODE", "false").lower() == "true":
    os.environ["AI_MOCK_MODE"] = "true"
    os.environ["EMBEDDING_PROVIDER"] = "mock"

from app.core.config import get_settings
from app.embeddings.service import get_embedding_service
from app.retrieval.qdrant import get_qdrant_manager
from app.schemas.resource import ResourcePayload

get_settings.cache_clear()

SAMPLE_RESOURCES = [
    ResourcePayload(
        resource_id="res_py_01",
        source="youtube",
        title="Python Full Course for Beginners: Variables, Data Structures, OOP",
        description="Comprehensive beginner-to-intermediate Python walkthrough covering core data structures, memory management, and OOP.",
        skills=["Python", "Object-Oriented Programming", "Data Structures"],
        topics=["Data Types", "Generators", "OOP", "File I/O"],
        difficulty="beginner",
        resource_type="video",
        duration_minutes=180,
        language="en",
        url="https://youtube.com/watch?v=sample_python_01",
        quality_score=0.92,
        prerequisites=[],
    ),
    ResourcePayload(
        resource_id="res_ml_01",
        source="coursera",
        title="Machine Learning Foundations: Linear Regression, Logistic Regression, Loss Functions",
        description="Foundational machine learning concepts including gradient descent, cost functions, regularization, and classification metrics.",
        skills=["Machine Learning", "Linear Algebra", "Python"],
        topics=["Gradient Descent", "Loss Functions", "L2 Regularization", "Cross-Entropy"],
        difficulty="intermediate",
        resource_type="course",
        duration_minutes=300,
        language="en",
        url="https://coursera.org/learn/sample_ml_01",
        quality_score=0.95,
        prerequisites=["Python", "Linear Algebra"],
    ),
    ResourcePayload(
        resource_id="res_dl_01",
        source="youtube",
        title="Deep Learning with PyTorch: Neural Networks, Backpropagation, CNNs",
        description="Hands-on neural network implementation from scratch in PyTorch. Covers autograd, loss computation, and vision models.",
        skills=["Deep Learning", "PyTorch", "Python"],
        topics=["Backpropagation", "Autograd", "Convolutional Neural Networks", "Optimization"],
        difficulty="intermediate",
        resource_type="video",
        duration_minutes=240,
        language="en",
        url="https://youtube.com/watch?v=sample_pytorch_dl",
        quality_score=0.94,
        prerequisites=["Python", "Machine Learning"],
    ),
    ResourcePayload(
        resource_id="res_mlops_01",
        source="documentation",
        title="Production MLOps: Dockerizing PyTorch Models and Deploying FastAPI Microservices",
        description="End-to-end guide on containerizing AI/ML workloads, creating REST endpoints with FastAPI, and monitoring model latency.",
        skills=["MLOps", "Docker", "FastAPI", "Python"],
        topics=["Docker Containerization", "Model Serving", "Inference Latency", "API Design"],
        difficulty="advanced",
        resource_type="documentation",
        duration_minutes=120,
        language="en",
        url="https://docs.learnpath.ai/mlops/serving",
        quality_score=0.90,
        prerequisites=["Python", "Deep Learning"],
    ),
]


async def main():
    print("Initializing Embedding Service & Qdrant Manager...")
    emb_svc = get_embedding_service()
    qdrant = get_qdrant_manager()

    texts = [f"{r.title}. {r.description or ''}" for r in SAMPLE_RESOURCES]
    print(f"Generating embeddings for {len(texts)} sample resources...")
    embeddings = await emb_svc.embed_documents(texts)

    print("Upserting vectors into Qdrant collection...")
    count = await qdrant.upsert_resources(SAMPLE_RESOURCES, embeddings)
    print(f"Successfully ingested {count} resources into Qdrant collection '{qdrant.settings.QDRANT_COLLECTION}'.")


if __name__ == "__main__":
    asyncio.run(main())

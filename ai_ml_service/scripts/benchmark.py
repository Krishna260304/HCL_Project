"""
Benchmark script to measure latency and throughput of the AI/ML service components.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Allow running benchmark in mock mode for instant local testing
if "--mock" in sys.argv or os.getenv("AI_MOCK_MODE", "false").lower() == "true":
    os.environ["AI_MOCK_MODE"] = "true"
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    os.environ["LLM_PROVIDER"] = "mock"

from app.core.config import get_settings
from app.embeddings.service import get_embedding_service
from app.llm.generation import get_generation_service
from app.schemas.goal import GoalAnalysisData

get_settings.cache_clear()


async def run_benchmark():
    settings = get_settings()
    print("============================================================")
    print(f" Starting AI/ML Service Component Benchmarking (Mock={settings.AI_MOCK_MODE})")
    print("============================================================")

    # 1. Embedding Benchmark
    emb_svc = get_embedding_service()
    test_texts = ["Python data science and machine learning foundations"] * 16

    t0 = time.perf_counter()
    embeddings = await emb_svc.embed_documents(test_texts)
    emb_time = (time.perf_counter() - t0) * 1000
    print(f"Embeddings (Batch of {len(test_texts)}): {emb_time:.2f}ms ({emb_time / len(test_texts):.2f}ms/doc, dim={len(embeddings[0])})")

    # 2. LLM Structured Generation Benchmark
    gen_svc = get_generation_service()
    t0 = time.perf_counter()
    goal_res = await gen_svc.generate_structured(
        schema_cls=GoalAnalysisData,
        prompt_name="goal_analysis_v1",
        prompt_vars={
            "goal": "Senior Machine Learning Engineer",
            "experience_level": "intermediate",
            "knowledge_areas": ["Python", "PyTorch", "Data Structures"],
            "learning_history": [],
            "target_outcome": "Lead ML Engineer",
            "timeline": "6 months",
        },
    )
    llm_time = (time.perf_counter() - t0) * 1000
    print(f"LLM Goal Analysis Structured Generation: {llm_time:.2f}ms (Result: '{goal_res.goal}')")
    print("============================================================")


if __name__ == "__main__":
    asyncio.run(run_benchmark())

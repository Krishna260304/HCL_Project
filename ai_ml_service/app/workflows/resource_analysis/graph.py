"""
Resource Analysis LangGraph Workflow Graph.
Extracts semantic topics, difficulty, prerequisites, and quality signals, and indexes vectors into Qdrant.
"""

import logging
from typing import Any, Dict, Optional
from langgraph.graph import END, StateGraph
from app.embeddings.service import EmbeddingService, get_embedding_service
from app.llm.generation import LLMGenerationService, get_generation_service
from app.retrieval.qdrant import QdrantManager, get_qdrant_manager
from app.schemas.resource import ResourceAnalysisData, ResourcePayload
from app.utils.ids import generate_id
from app.workflows.resource_analysis.state import ResourceAnalysisWorkflowState

logger = logging.getLogger(__name__)


def create_resource_analysis_nodes(
    generation_service: LLMGenerationService,
    embedding_service: EmbeddingService,
    qdrant_manager: QdrantManager,
):
    async def extract_metadata_node(state: ResourceAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 1: Extract basic attributes from title and description."""
        logger.info(f"[{state.request_id}] Resource Analysis: Processing '{state.title}'")
        return {"status": "metadata_extracted"}

    async def enrich_with_llm_node(state: ResourceAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 2: Extract skills, difficulty, prerequisites, and quality metrics."""
        try:
            enriched = await generation_service.generate_structured(
                schema_cls=ResourceAnalysisData,
                prompt_name="resource_analysis_v1",
                prompt_vars={
                    "title": state.title,
                    "description": state.description,
                    "source": state.source,
                    "url": state.url or "N/A",
                },
                system_prompt="You are a curriculum cataloguer. Extract precise skill metadata and difficulty tiers.",
            )
            # Merge explicit skills if supplied
            if state.explicit_skills:
                for s in state.explicit_skills:
                    if s not in enriched.skills:
                        enriched.skills.append(s)
            return {"final_output": enriched, "status": "enriched"}
        except Exception as exc:
            logger.warning(f"[{state.request_id}] LLM resource enrichment fallback: {exc}")
            skills = state.explicit_skills or [state.title.split()[0] if state.title.split() else "General"]
            fallback = ResourceAnalysisData(
                skills=skills,
                topics=[state.title],
                difficulty="intermediate",
                prerequisites=["Foundations"],
                quality_score=0.85,
                estimated_duration=30,
                learning_format="article" if "doc" in state.title.lower() else "video",
                quality_signals={"heuristic": True},
                summary=state.description or state.title,
                semantic_text=f"{state.title}. {state.description}",
                confidence=0.8,
            )
            return {"final_output": fallback, "status": "fallback_enriched"}

    async def generate_embedding_node(state: ResourceAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 3: Compute dense BGE-M3 embedding vector."""
        text_to_embed = f"{state.title}. {state.final_output.summary if state.final_output else state.description}"
        vec = await embedding_service.embed_query(text_to_embed)
        return {"embedding_vector": vec, "status": "embedded"}

    async def index_vector_node(state: ResourceAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 4: Store resource payload and vector into Qdrant."""
        if not state.embedding_vector or not state.final_output:
            return {"status": "skipped_indexing"}

        res_id = state.metadata.get("resource_id") or generate_id("res")
        payload = ResourcePayload(
            resource_id=res_id,
            source=state.source,
            title=state.title,
            description=state.description,
            skills=state.final_output.skills,
            topics=state.final_output.topics,
            difficulty=state.final_output.difficulty,
            resource_type=state.final_output.learning_format,
            duration_minutes=state.final_output.estimated_duration,
            language="en",
            url=state.url,
            quality_score=state.final_output.quality_score,
            prerequisites=state.final_output.prerequisites,
        )

        try:
            await qdrant_manager.upsert_resources(
                resources=[payload],
                embeddings=[state.embedding_vector],
            )
            return {"normalized_payload": payload, "status": "indexed"}
        except Exception as e:
            logger.warning(f"[{state.request_id}] Failed to index in Qdrant: {e}")
            return {"normalized_payload": payload, "status": "indexing_failed"}

    return extract_metadata_node, enrich_with_llm_node, generate_embedding_node, index_vector_node


def build_resource_analysis_graph(
    generation_service: Optional[LLMGenerationService] = None,
    embedding_service: Optional[EmbeddingService] = None,
    qdrant_manager: Optional[QdrantManager] = None,
):
    gen_svc = generation_service or get_generation_service()
    emb_svc = embedding_service or get_embedding_service()
    qdrant = qdrant_manager or get_qdrant_manager()

    extract_meta, enrich, gen_emb, index_vec = create_resource_analysis_nodes(gen_svc, emb_svc, qdrant)

    workflow = StateGraph(ResourceAnalysisWorkflowState)
    workflow.add_node("extract_metadata", extract_meta)
    workflow.add_node("enrich_with_llm", enrich)
    workflow.add_node("generate_embedding", gen_emb)
    workflow.add_node("index_vector", index_vec)

    workflow.set_entry_point("extract_metadata")
    workflow.add_edge("extract_metadata", "enrich_with_llm")
    workflow.add_edge("enrich_with_llm", "generate_embedding")
    workflow.add_edge("generate_embedding", "index_vector")
    workflow.add_edge("index_vector", END)

    return workflow.compile()

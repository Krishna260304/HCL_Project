"""
RAG LangGraph Workflow Graph.
Orchestrates vector retrieval, source attribution, grounded Qwen synthesis, and action recommendations.
"""

import logging
from typing import Any, Dict, List, Optional
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.retrieval.hybrid import HybridSearchService
from app.schemas.rag import RAGQueryData, RAGSource
from app.workflows.rag.state import RAGWorkflowState

logger = logging.getLogger(__name__)


def create_rag_nodes(
    generation_service: LLMGenerationService,
    hybrid_search: HybridSearchService,
):
    async def retrieve_documents_node(state: RAGWorkflowState) -> Dict[str, Any]:
        """Node 1: Retrieve relevant documents from Qdrant."""
        logger.info(f"[{state.request_id}] RAG Graph: Retrieving documents for '{state.query}'")
        try:
            hits = await hybrid_search.search(
                query=state.query,
                top_k=state.top_k,
            )
            return {"retrieved_documents": hits, "status": "documents_retrieved"}
        except Exception as e:
            logger.warning(f"[{state.request_id}] Document retrieval error: {e}")
            return {"retrieved_documents": [], "status": "retrieval_failed"}

    async def assemble_sources_node(state: RAGWorkflowState) -> Dict[str, Any]:
        """Node 2: Extract structured RAGSource objects with attribution."""
        sources: List[RAGSource] = []
        for hit in state.retrieved_documents:
            payload = hit.get("payload", {})
            title = payload.get("title", f"Knowledge Item {hit.get('id')}")
            snippet = payload.get("description") or payload.get("summary") or title
            url = payload.get("url")
            res_id = payload.get("resource_id") or str(hit.get("id"))
            score = float(hit.get("score", 0.85))

            sources.append(
                RAGSource(
                    title=title,
                    url=url,
                    source_type=payload.get("resource_type", "documentation"),
                    snippet=snippet[:300],
                    relevance_score=round(score, 2),
                    resource_id=res_id,
                )
            )
        return {"sources": sources, "status": "sources_assembled"}

    async def generate_grounded_answer_node(state: RAGWorkflowState) -> Dict[str, Any]:
        """Node 3: Generate grounded natural-language answer with citation constraints."""
        doc_payloads = [s.model_dump() for s in state.sources]
        try:
            raw_answer = await generation_service.generate_text(
                prompt_name="rag_v1",
                prompt_vars={
                    "query": state.query,
                    "learner_context": state.learner_context,
                    "documents": doc_payloads,
                },
                system_prompt="You are LearnPath AI Tutor. Answer accurately based strictly on supplied documents. Suggest concrete next actions.",
                max_tokens=600,
            )
            actions = [
                "Review the referenced core documentation modules",
                "Practice with an interactive coding exercise",
                "Take a quick 3-question formative check",
            ]
            output = RAGQueryData(
                answer=raw_answer.strip(),
                sources=state.sources,
                recommended_actions=actions,
                context_metadata={"sources_count": len(state.sources)},
                confidence=0.92 if len(state.sources) > 0 else 0.70,
            )
            return {"final_output": output, "status": "completed"}
        except Exception as exc:
            logger.error(f"[{state.request_id}] Grounded answer generation error: {exc}")
            fallback = RAGQueryData(
                answer=f"Here is pedagogical guidance regarding '{state.query}': Focus on core foundations first, followed by applied implementation.",
                sources=state.sources,
                recommended_actions=["Review learning path roadmap", "Take diagnostic assessment"],
                context_metadata={"mode": "fallback"},
                confidence=0.65,
            )
            return {"final_output": fallback, "status": "fallback_completed"}

    return retrieve_documents_node, assemble_sources_node, generate_grounded_answer_node


def build_rag_graph(
    generation_service: Optional[LLMGenerationService] = None,
    hybrid_search: Optional[HybridSearchService] = None,
):
    gen_svc = generation_service or get_generation_service()
    h_search = hybrid_search or HybridSearchService()

    retrieve, assemble, gen_answer = create_rag_nodes(gen_svc, h_search)

    workflow = StateGraph(RAGWorkflowState)
    workflow.add_node("retrieve_documents", retrieve)
    workflow.add_node("assemble_sources", assemble)
    workflow.add_node("generate_answer", gen_answer)

    workflow.set_entry_point("retrieve_documents")
    workflow.add_edge("retrieve_documents", "assemble_sources")
    workflow.add_edge("assemble_sources", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()

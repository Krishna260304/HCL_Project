"""
Recommendation LangGraph Workflow Graph.
Orchestrates candidate retrieval, multi-factor ranking, evidence extraction, and grounded LLM explanation generation.
"""

import logging
from typing import Any, Dict, List, Optional
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.retrieval.hybrid import HybridSearchService
from app.retrieval.reranker import ResourceRanker, get_resource_ranker
from app.schemas.recommendation import RecommendationData, RecommendationItem
from app.workflows.recommendation.state import RecommendationWorkflowState

logger = logging.getLogger(__name__)


def create_recommendation_nodes(
    generation_service: LLMGenerationService,
    hybrid_search: HybridSearchService,
    resource_ranker: ResourceRanker,
):
    async def retrieve_candidates_node(state: RecommendationWorkflowState) -> Dict[str, Any]:
        """Node 1: Retrieve candidate learning resources via semantic search if not provided."""
        logger.info(f"[{state.request_id}] Recommendation Graph: Retrieving candidate resources")
        all_candidates = list(state.candidate_resources)

        # If candidates were not explicitly supplied, perform semantic search using goal & skill gaps
        if len(all_candidates) < state.limit:
            goal_str = state.goal if isinstance(state.goal, str) else (state.goal.get("goal") if isinstance(state.goal, dict) else "Technology")
            gap_skills = [
                g["skill"] if isinstance(g, dict) else str(g) for g in state.skill_gaps
            ]
            search_query = f"{goal_str} {' '.join(gap_skills)}"
            retrieved = await hybrid_search.search(
                query=search_query,
                top_k=state.limit * 2,
            )
            # Merge and deduplicate by resource_id
            seen_ids = {str(c.get("resource_id", c.get("id", ""))) for c in all_candidates}
            for hit in retrieved:
                h_id = str(hit.get("payload", {}).get("resource_id", hit.get("id", "")))
                if h_id not in seen_ids:
                    seen_ids.add(h_id)
                    all_candidates.append(hit)

        return {"retrieved_candidates": all_candidates, "status": "candidates_retrieved"}

    async def rank_candidates_node(state: RecommendationWorkflowState) -> Dict[str, Any]:
        """Node 2: Multi-factor ranking with deterministic baseline or neural reranker."""
        logger.info(f"[{state.request_id}] Recommendation Graph: Ranking {len(state.retrieved_candidates)} candidates")
        goal_str = str(state.goal) if state.goal else "Skill Acceleration"
        ranked = await resource_ranker.rank(
            query=goal_str,
            candidates=state.retrieved_candidates,
            learner_context=state.learner_profile,
            verified_skills=state.verified_skills,
            skill_gaps=state.skill_gaps,
            preferences=state.preferences,
            top_k=state.limit,
        )
        return {"ranked_items": ranked, "status": "ranked"}

    async def explain_recommendations_node(state: RecommendationWorkflowState) -> Dict[str, Any]:
        """Node 3: Grounded LLM explanation generation based ONLY on calculated evidence."""
        if not state.ranked_items:
            return {"status": "no_items_to_explain"}

        goal_str = str(state.goal) if state.goal else "Skill Growth"
        top_items: List[RecommendationItem] = []

        # Explain top 3 items with LLM, keep deterministic reasons for the rest
        for idx, item in enumerate(state.ranked_items):
            if idx < 3 and item.evidence:
                try:
                    reason = await generation_service.generate_text(
                        prompt_name="recommendation_explanation_v1",
                        prompt_vars={
                            "resource": {
                                "title": item.title,
                                "skills": item.matched_skills or [item.skill_id or "Core"],
                                "difficulty": item.difficulty_match,
                            },
                            "goal": goal_str,
                            "evidence": item.evidence.model_dump(),
                        },
                        system_prompt="You are an empathetic learning coach. Generate concise, grounded 1-2 sentence recommendation justifications.",
                        max_tokens=150,
                    )
                    item.reason = reason.strip()
                except Exception as e:
                    logger.debug(f"LLM explanation fallback: {e}")
            top_items.append(item)

        output = RecommendationData(
            recommendations=top_items,
            metadata={
                "total_candidates": len(state.retrieved_candidates),
                "ranked_count": len(top_items),
                "ranker_used": top_items[0].source if top_items else "none",
            },
        )
        return {"final_output": output, "status": "completed"}

    return retrieve_candidates_node, rank_candidates_node, explain_recommendations_node


def build_recommendation_graph(
    generation_service: Optional[LLMGenerationService] = None,
    hybrid_search: Optional[HybridSearchService] = None,
    resource_ranker: Optional[ResourceRanker] = None,
):
    gen_svc = generation_service or get_generation_service()
    h_search = hybrid_search or HybridSearchService()
    ranker = resource_ranker or get_resource_ranker()

    retrieve, rank_node, explain_node = create_recommendation_nodes(gen_svc, h_search, ranker)

    workflow = StateGraph(RecommendationWorkflowState)
    workflow.add_node("retrieve_candidates", retrieve)
    workflow.add_node("rank_candidates", rank_node)
    workflow.add_node("explain_recommendations", explain_node)

    workflow.set_entry_point("retrieve_candidates")
    workflow.add_edge("retrieve_candidates", "rank_candidates")
    workflow.add_edge("rank_candidates", "explain_recommendations")
    workflow.add_edge("explain_recommendations", END)

    return workflow.compile()

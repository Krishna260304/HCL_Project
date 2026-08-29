"""
Resource Analysis and Batch Ingestion Service.
"""

from typing import List, Optional
from app.embeddings.service import get_embedding_service
from app.retrieval.qdrant import get_qdrant_manager
from app.schemas.resource import (
    ResourceAnalysisData,
    ResourceAnalysisRequest,
    ResourceBatchIngestRequest,
    ResourceIngestResponse,
    ResourcePayload,
)
from app.utils.ids import generate_request_id
from app.workflows.resource_analysis.graph import build_resource_analysis_graph
from app.workflows.resource_analysis.state import ResourceAnalysisWorkflowState


class ResourceService:
    def __init__(self):
        self.graph = build_resource_analysis_graph()
        self.embedding_service = get_embedding_service()
        self.qdrant_manager = get_qdrant_manager()

    async def analyze(self, request: ResourceAnalysisRequest) -> ResourceAnalysisData:
        req_id = request.request_id or generate_request_id()
        initial_state = ResourceAnalysisWorkflowState(
            request_id=req_id,
            title=request.title,
            description=request.description or "",
            source=request.source or "web",
            url=request.url,
            explicit_skills=request.skills or [],
            metadata=request.metadata or {},
        )
        final_state = await self.graph.ainvoke(initial_state)
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, ResourceAnalysisData):
            return out
        elif isinstance(out, dict):
            return ResourceAnalysisData.model_validate(out)
        raise RuntimeError("Resource analysis workflow did not return valid output.")

    async def batch_ingest(self, request: ResourceBatchIngestRequest) -> ResourceIngestResponse:
        """Batch vectorize and ingest resources directly into Qdrant."""
        resources = request.resources
        texts = [f"{r.title}. {r.description or ''}" for r in resources]
        embeddings = await self.embedding_service.embed_documents(texts)
        count = await self.qdrant_manager.upsert_resources(resources=resources, embeddings=embeddings)
        return ResourceIngestResponse(
            ingested_count=count,
            failed_count=len(resources) - count,
            collection=self.qdrant_manager.settings.QDRANT_COLLECTION,
        )


_resource_service: Optional[ResourceService] = None


def get_resource_service() -> ResourceService:
    global _resource_service
    if _resource_service is None:
        _resource_service = ResourceService()
    return _resource_service

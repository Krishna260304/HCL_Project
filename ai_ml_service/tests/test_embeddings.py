"""
Tests for Embedding Provider and Batch Processing.
"""

import pytest
from app.embeddings.batching import chunk_list, process_in_batches
from app.embeddings.service import get_embedding_service


@pytest.mark.asyncio
async def test_embedding_service_dimension_and_consistency():
    emb_svc = get_embedding_service()
    assert emb_svc.get_dimension() == 1024

    vec = await emb_svc.embed_query("Python programming language")
    assert len(vec) == 1024

    # Batch test
    docs = ["Doc 1", "Doc 2", "Doc 3"]
    vectors = await emb_svc.embed_documents(docs)
    assert len(vectors) == 3
    for v in vectors:
        assert len(v) == 1024


def test_chunking_utility():
    items = list(range(10))
    chunks = chunk_list(items, chunk_size=3)
    assert len(chunks) == 4
    assert chunks[0] == [0, 1, 2]
    assert chunks[-1] == [9]

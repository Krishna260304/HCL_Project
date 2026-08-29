"""
Batch processing utilities for large volume embedding ingestion.
Prevents GPU out-of-memory errors by slicing inputs into configurable chunk sizes.
"""

from typing import Any, Callable, Coroutine, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of at most chunk_size."""
    if chunk_size <= 0:
        chunk_size = 32
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


async def process_in_batches(
    items: List[T],
    batch_size: int,
    async_processor: Callable[[List[T]], Coroutine[Any, Any, List[R]]],
) -> List[R]:
    """Execute an asynchronous batch processor sequentially across all chunks."""
    results: List[R] = []
    chunks = chunk_list(items, batch_size)
    for chunk in chunks:
        batch_res = await async_processor(chunk)
        results.extend(batch_res)
    return results

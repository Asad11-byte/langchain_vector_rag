"""
Reranking: takes the hybrid retriever's top-k candidates and re-scores them
with a more accurate (but slower) cross-encoder model, then keeps only the
best few for generation.

Two options included:
  - rerank_local()  -> free, runs on your own machine (sentence-transformers)
  - rerank_cohere() -> paid API, generally higher quality, less setup

Use whichever fits your budget; compare both for your reranking experiment.
"""

from functools import lru_cache
from app.config import settings


@lru_cache
def _get_local_cross_encoder():
    from sentence_transformers import CrossEncoder
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_local(query: str, candidates: list[dict], top_n: int | None = None) -> list[dict]:
    """Reranks candidates using a local cross-encoder model (no API cost)."""
    top_n = top_n or settings.top_k_rerank
    if not candidates:
        return []

    model = _get_local_cross_encoder()
    pairs = [(query, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    ranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:top_n]


def rerank_cohere(query: str, candidates: list[dict], top_n: int | None = None) -> list[dict]:
    """Reranks candidates using Cohere's hosted rerank API."""
    import cohere

    top_n = top_n or settings.top_k_rerank
    if not candidates:
        return []

    co = cohere.Client(settings.cohere_api_key)
    docs = [c["text"] for c in candidates]

    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=docs,
        top_n=top_n,
    )

    reranked = []
    for result in response.results:
        candidate = candidates[result.index]
        candidate["rerank_score"] = result.relevance_score
        reranked.append(candidate)

    return reranked


def rerank(query: str, candidates: list[dict], method: str = "local", top_n: int | None = None) -> list[dict]:
    """Entry point used by the query chain. Swap `method` to experiment."""
    if method == "local":
        return rerank_local(query, candidates, top_n)
    elif method == "cohere":
        return rerank_cohere(query, candidates, top_n)
    else:
        raise ValueError(f"Unknown rerank method: {method}")

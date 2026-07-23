"""
Hybrid retrieval: queries Qdrant using BOTH dense and sparse vectors,
fused server-side via Qdrant's Query API (RRF - Reciprocal Rank Fusion).

This is the retrieval half of hybrid search — combines semantic similarity
(dense) with exact keyword matching (sparse/BM25), which tends to outperform
either alone, especially for queries with specific terms/names/numbers.
"""

from qdrant_client.models import (
    Prefetch,
    FusionQuery,
    Fusion,
    SparseVector,
)

from app.config import settings
from app.services.qdrant_client import get_qdrant_client
from app.core.embeddings import get_embedding_model
from app.core.sparse import embed_sparse

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


def hybrid_search(query: str, top_k: int | None = None) -> list[dict]:
    """
    Runs hybrid dense+sparse search against Qdrant and returns fused results.

    Returns a list of dicts: {text, source_filename, page, chunk_index, score}
    ordered by relevance (best first).
    """
    top_k = top_k or settings.top_k_retrieval

    client = get_qdrant_client()
    embedder = get_embedding_model()

    dense_query_vector = embedder.embed_query(query)
    sparse_query_vector = embed_sparse([query])[0]

    results = client.query_points(
        collection_name=settings.qdrant_collection_name,
        prefetch=[
            Prefetch(
                query=dense_query_vector,
                using=DENSE_VECTOR_NAME,
                limit=top_k * 2,  # over-fetch before fusion narrows it down
            ),
            Prefetch(
                query=SparseVector(
                    indices=sparse_query_vector.indices.tolist(),
                    values=sparse_query_vector.values.tolist(),
                ),
                using=SPARSE_VECTOR_NAME,
                limit=top_k * 2,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
    )

    return [
        {
            "text": point.payload.get("text", ""),
            "source_filename": point.payload.get("source_filename"),
            "page": point.payload.get("page"),
            "chunk_index": point.payload.get("chunk_index"),
            "score": point.score,
        }
        for point in results.points
    ]

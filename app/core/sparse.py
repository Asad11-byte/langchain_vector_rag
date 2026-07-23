"""
Sparse vector encoding (BM25-style) for hybrid search.
Uses FastEmbed's sparse model — works alongside dense embeddings so Qdrant
can fuse both signals (keyword match + semantic match) at query time.
"""

from functools import lru_cache
from fastembed import SparseTextEmbedding


@lru_cache
def get_sparse_model() -> SparseTextEmbedding:
    """
    Returns a cached sparse embedding model.
    'Qdrant/bm25' is a good default; 'prithivida/Splade_PP_en_v1' is a
    stronger (but slower) SPLADE alternative worth comparing in your
    hybrid-weighting experiments.
    """
    return SparseTextEmbedding(model_name="Qdrant/bm25")


def embed_sparse(texts: list[str]):
    """
    Encodes a list of texts into sparse vectors.
    Returns FastEmbed's SparseEmbedding objects (each has .indices and .values)
    which map directly onto Qdrant's SparseVector format.
    """
    model = get_sparse_model()
    return list(model.embed(texts))

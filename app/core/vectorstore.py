"""
Vector store operations: upserting chunks into Qdrant with BOTH dense and
sparse vectors attached to each point (this is what makes hybrid search work),
and a plain similarity search helper.

This module talks to Qdrant directly (rather than only through LangChain's
QdrantVectorStore wrapper) so we have full control over the hybrid schema
defined in scripts/setup_qdrant_collection.py.
"""

import uuid
from langchain_core.documents import Document
from qdrant_client.models import PointStruct, SparseVector

from app.config import settings
from app.services.qdrant_client import get_qdrant_client
from app.core.embeddings import get_embedding_model
from app.core.sparse import embed_sparse

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


def upsert_chunks(chunks: list[Document], document_id: str) -> int:
    """
    Embeds each chunk (dense + sparse) and upserts them into Qdrant.
    Returns the number of points written.

    `document_id` is stored in payload so we can later delete/filter by
    source document (e.g. if a user deletes an uploaded file).
    """
    if not chunks:
        return 0

    client = get_qdrant_client()
    embedder = get_embedding_model()

    texts = [chunk.page_content for chunk in chunks]

    dense_vectors = embedder.embed_documents(texts)
    sparse_vectors = embed_sparse(texts)

    points = []
    for chunk, dense_vec, sparse_vec in zip(chunks, dense_vectors, sparse_vectors):
        point_id = str(uuid.uuid4())

        points.append(
            PointStruct(
                id=point_id,
                vector={
                    DENSE_VECTOR_NAME: dense_vec,
                    SPARSE_VECTOR_NAME: SparseVector(
                        indices=sparse_vec.indices.tolist(),
                        values=sparse_vec.values.tolist(),
                    ),
                },
                payload={
                    "text": chunk.page_content,
                    "document_id": document_id,
                    "source_filename": chunk.metadata.get("source_filename"),
                    "chunk_index": chunk.metadata.get("chunk_index"),
                    "page": chunk.metadata.get("page"),
                },
            )
        )

    client.upsert(collection_name=settings.qdrant_collection_name, points=points)
    return len(points)


def delete_document_chunks(document_id: str) -> None:
    """Deletes all chunks belonging to a given document_id (e.g. on file delete)."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = get_qdrant_client()
    client.delete(
        collection_name=settings.qdrant_collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
    )

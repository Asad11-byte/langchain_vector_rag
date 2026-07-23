"""
Thin wrapper around the Qdrant client connection.
Other modules import `get_qdrant_client()` instead of creating their own connections.
"""

from functools import lru_cache
from qdrant_client import QdrantClient
from app.config import settings


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Returns a cached Qdrant client instance (one connection reused app-wide)."""
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

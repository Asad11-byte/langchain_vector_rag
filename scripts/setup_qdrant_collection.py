"""
One-time setup script: creates a Qdrant collection configured for
HYBRID search (dense + sparse vectors in the same collection).

Run this once before ingesting any documents:
    python scripts/setup_qdrant_collection.py
"""

import sys
import os

# Allow running this script directly from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
)
from app.config import settings


# ==============================================================================
# CONFIGURATION & HYPERPARAMETERS
# Change these values depending on your embedding models and setup
# ==============================================================================

# Common Dense Dimensions Reference:
# - OpenAI text-embedding-3-small / BGE-Large-EN-v1.5 -> 1024
# - OpenAI text-embedding-3-large                  -> 3072
# - Cohere embed-english-v3.0                      -> 1024
# - All-MiniLM-L6-v2                                -> 384

DENSE_VECTOR_SIZE = 1024
DENSE_DISTANCE_METRIC = Distance.COSINE  # Options: COSINE, DOT, EUCLID

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"

FORCE_RECREATE = True  # Set to True if you want to drop and recreate during dev


# ==============================================================================
# MAIN SETUP LOGIC
# ==============================================================================

def main():
    # Initialize Client
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    collection_name = settings.qdrant_collection_name

    # Check if collection exists
    if client.collection_exists(collection_name=collection_name):
        if FORCE_RECREATE:
            print(f"⚠️  FORCE_RECREATE is True. Deleting existing collection '{collection_name}'...")
            client.delete_collection(collection_name=collection_name)
        else:
            print(f"✅ Collection '{collection_name}' already exists. Skipping creation.")
            print("If you need to change the schema, set `FORCE_RECREATE = True` or run:")
            print(f'    client.delete_collection("{collection_name}")')
            return

    # Create Collection with Hybrid Search schema
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            DENSE_VECTOR_NAME: VectorParams(
                size=DENSE_VECTOR_SIZE,
                distance=DENSE_DISTANCE_METRIC,
            ),
        },
        sparse_vectors_config={
            SPARSE_VECTOR_NAME: SparseVectorParams(
                index=SparseIndexParams(
                    on_disk=False  # Set to True for very large sparse indexes
                ),
            ),
        },
    )

    print(f"🎉 Successfully created hybrid collection '{collection_name}'!")
    print(f"   - Dense Vector  : '{DENSE_VECTOR_NAME}' (size={DENSE_VECTOR_SIZE}, metric={DENSE_DISTANCE_METRIC.name})")
    print(f"   - Sparse Vector : '{SPARSE_VECTOR_NAME}' (BM25/SPLADE format)")


if __name__ == "__main__":
    main()
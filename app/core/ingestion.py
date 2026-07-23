"""
Ingestion orchestrator: the single function the /api/upload route calls.
Wires together load -> chunk -> embed+upsert -> Supabase metadata logging.
"""

import uuid

from app.core.loaders import load_document
from app.core.chunking import chunk_documents
from app.core.vectorstore import upsert_chunks
from app.services.supabase_client import upload_file_to_storage, insert_document_record


def ingest_file(file_bytes: bytes, filename: str, chunking_strategy: str = "recursive") -> dict:
    """
    Full ingestion pipeline for one uploaded file:
      1. Upload raw file to Supabase Storage (so it can be re-downloaded/viewed later)
      2. Parse into LangChain Documents (loaders.py)
      3. Split into chunks (chunking.py)
      4. Embed (dense + sparse) and upsert into Qdrant (vectorstore.py)
      5. Log a row in Supabase `documents` table

    Returns a dict with document_id, filename, and chunk_count.
    """
    document_id = str(uuid.uuid4())
    storage_path = f"{document_id}/{filename}"

    # 1. store raw file
    upload_file_to_storage(file_bytes, storage_path)

    # 2. parse
    documents = load_document(file_bytes, filename)

    # 3. chunk
    chunks = chunk_documents(documents, strategy=chunking_strategy)

    # 4. embed + upsert into Qdrant
    chunk_count = upsert_chunks(chunks, document_id=document_id)

    # 5. log metadata in Supabase
    insert_document_record(filename=filename, storage_path=storage_path, chunk_count=chunk_count)

    return {
        "document_id": document_id,
        "filename": filename,
        "chunk_count": chunk_count,
    }

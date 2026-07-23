"""
Thin wrapper around the Supabase client connection.
Handles both the Postgres metadata client and file storage helpers.
"""

from functools import lru_cache
from supabase import create_client, Client
from app.config import settings

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


@lru_cache
def get_supabase_client() -> Client:
    """Returns a cached Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_key)


def upload_file_to_storage(file_bytes: bytes, storage_path: str) -> str:
    """
    Uploads a raw file to Supabase Storage.
    Validates file size (10 MB limit) and uploads directly.
    Returns the storage path.
    """
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        raise ValueError(
            f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of 10 MB."
        )

    client = get_supabase_client()
    bucket = settings.supabase_storage_bucket

    try:
        # Pass file directly without file_options to avoid storage3 SDK header encoding bugs
        client.storage.from_(bucket).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
        return storage_path
    except Exception as e:
        raise RuntimeError(f"Supabase storage upload failed for '{storage_path}': {str(e)}")


def insert_document_record(filename: str, storage_path: str, chunk_count: int) -> dict:
    """
    Inserts a row into the `documents` table after successful ingestion.
    Returns the inserted row (includes the generated document id).
    """
    client = get_supabase_client()
    
    try:
        result = (
            client.table("documents")
            .insert(
                {
                    "filename": filename,
                    "storage_path": storage_path,
                    "chunk_count": chunk_count,
                }
            )
            .execute()
        )
        return result.data[0] if result.data else {}
    except Exception as e:
        raise RuntimeError(f"Failed to insert record into Supabase DB: {str(e)}")
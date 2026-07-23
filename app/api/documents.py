"""
Documents endpoint: list uploaded documents and allow deletion.
"""

from fastapi import APIRouter, HTTPException

from app.services.supabase_client import get_supabase_client
from app.core.vectorstore import delete_document_chunks

router = APIRouter()


@router.get("/documents")
async def list_documents():
    """Returns all uploaded documents with metadata."""
    client = get_supabase_client()
    result = client.table("documents").select("*").order("created_at", desc=True).execute()
    return {"documents": result.data}


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Deletes a document's chunks from Qdrant and its metadata row from Supabase."""
    client = get_supabase_client()

    existing = client.table("documents").select("id").eq("id", document_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Document not found.")

    delete_document_chunks(document_id)
    client.table("documents").delete().eq("id", document_id).execute()

    return {"status": "deleted", "document_id": document_id}

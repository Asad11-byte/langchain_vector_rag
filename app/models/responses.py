"""Pydantic response schemas."""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    status: str = "success"


class SourceChunk(BaseModel):
    text: str
    source_filename: str | None = None
    page: int | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []

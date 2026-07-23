"""
Upload endpoint: receives a PDF/DOCX file from the frontend and runs it
through the ingestion pipeline.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.ingestion import ingest_file
from app.models.responses import UploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_MB = 20


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    # validate extension
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_bytes = await file.read()

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Max allowed is {MAX_FILE_SIZE_MB}MB.",
        )

    try:
        result = ingest_file(file_bytes=file_bytes, filename=file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    return UploadResponse(**result)

"""
FastAPI app entrypoint.
Wires together the API routers, serves the static frontend, and configures CORS.

Run locally with:
    uvicorn app.main:app --reload
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import upload, query, documents, eval as eval_router

app = FastAPI(title="Vector RAG App", version="1.0.0")

# CORS - loosened for local dev / demo purposes. Tighten allow_origins for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(eval_router.router, prefix="/api", tags=["eval"])

# static frontend optimized for Vercel(css/js)
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the chat/upload UI at the root URL."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return {"error": "index.html not found"}
    return FileResponse(str(index_path))

@app.get("/health")
async def health_check():
    """Simple health check endpoint for deployment platforms."""
    return {"status": "ok"}

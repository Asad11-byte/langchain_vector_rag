"""
Centralized app configuration.
Loads values from .env using pydantic-settings so every other module
can just do: from app.config import settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- LLM Provider ---
    
    groq_api_key: str = "" 

    # --- Embedding model ---
    embedding_model: str = "text-embedding-3-small"

    # --- Qdrant Cloud ---
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "rag_documents"

    # --- Supabase ---
    supabase_url: str
    supabase_key: str
    supabase_storage_bucket: str = "documents"

    # --- Reranker ---
    cohere_api_key: str = ""

    # --- App / RAG tuning ---
    environment: str = "development"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_retrieval: int = 10
    top_k_rerank: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

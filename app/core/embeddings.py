import os
from langchain_community.embeddings import JinaEmbeddings

def get_embedding_model():
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        raise ValueError("JINA_API_KEY environment variable is not set.")

    return JinaEmbeddings(
        jina_api_key=api_key,
        model_name="jina-embeddings-v3"
    )
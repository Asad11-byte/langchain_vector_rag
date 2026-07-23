"""
Chunking strategies.

Start with `recursive_chunk` (the standard baseline). `semantic_chunk` is
included as an alternative you can A/B test against it for your
"optimize & measure" deliverable — swap which one `chunk_documents` uses
and log the retrieval quality difference in eval/experiment_log.md.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings


def recursive_chunk(documents: list[Document]) -> list[Document]:
    """
    Baseline chunking strategy: splits on paragraph/sentence boundaries
    recursively, falling back to smaller separators as needed.
    Size/overlap are read from settings so they're easy to tune per experiment.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # add a stable chunk index per document (useful for citations + debugging)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    return chunks


def semantic_chunk(documents: list[Document]) -> list[Document]:
    """
    Alternative strategy: groups sentences by embedding similarity instead
    of fixed character counts. Requires langchain_experimental.

    Uncomment and `pip install langchain-experimental` to try this variant
    against recursive_chunk() for your chunking experiment comparison.
    """
    raise NotImplementedError(
        "Install langchain-experimental and implement SemanticChunker here "
        "if you want to A/B test semantic vs recursive chunking."
    )
    # from langchain_experimental.text_splitter import SemanticChunker
    # from app.core.embeddings import get_embedding_model
    # splitter = SemanticChunker(get_embedding_model())
    # return splitter.split_documents(documents)


def chunk_documents(documents: list[Document], strategy: str = "recursive") -> list[Document]:
    """Entry point used by the ingestion pipeline. Swap `strategy` to experiment."""
    if strategy == "recursive":
        return recursive_chunk(documents)
    elif strategy == "semantic":
        return semantic_chunk(documents)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

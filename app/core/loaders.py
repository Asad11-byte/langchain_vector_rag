"""
Document loaders: turn an uploaded PDF/DOCX file (bytes on disk) into
LangChain Document objects with page_content + metadata.
"""

import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document


def load_document(file_bytes: bytes, filename: str) -> list[Document]:
    """
    Dispatches to the right loader based on file extension.
    Writes the bytes to a temp file because LangChain's loaders expect a file path.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext not in (".pdf", ".docx", ".doc"):
        raise ValueError(f"Unsupported file type: {ext}. Only PDF/DOC/DOCX are supported.")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:  # .docx / .doc
            loader = Docx2txtLoader(tmp_path)

        documents = loader.load()

        # attach original filename to every chunk's metadata (useful for citations later)
        for doc in documents:
            doc.metadata["source_filename"] = filename

        return documents
    finally:
        os.remove(tmp_path)

"""
The main RAG chain: retrieve -> rerank -> generate.

This is the function the /api/query route calls. Query rewriting is
optional (toggle with use_query_rewrite) so you can A/B test its impact
for your optimization write-up.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.core.retriever import hybrid_search

from app.core.query_rewrite import rewrite_query

ANSWER_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant answering questions based only on the
provided context. If the context doesn't contain the answer, say you don't
know rather than guessing.

Context:
{context}

Question: {question}

Answer:"""
)


def _get_llm():
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.groq_api_key, temperature=0.2)


def _format_context(chunks: list[dict]) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {c.get('source_filename', 'unknown')}]\n{c['text']}" for c in chunks
    )


def answer_question(
    question: str,
    use_query_rewrite: bool = False,
) -> dict:
    """
    Full RAG pipeline for a single question.
    Returns {answer: str, sources: list[dict]}
    """
    search_query = rewrite_query(question) if use_query_rewrite else question

    # 1. retrieve (hybrid dense + sparse)
    candidates = hybrid_search(search_query)

    if not candidates:
        return {
            "answer": "I couldn't find anything relevant in the uploaded documents to answer that.",
            "sources": [],
        }

    # 2. skip reranking — just take the top-N from retrieval directly
    top_chunks = candidates[: settings.top_k_rerank]

    # 3. generate
    context = _format_context(top_chunks)
    chain = ANSWER_PROMPT | _get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    sources = [
        {
            "text": c["text"],
            "source_filename": c.get("source_filename"),
            "page": c.get("page"),
        }
        for c in top_chunks
    ]

    return {"answer": answer, "sources": sources}
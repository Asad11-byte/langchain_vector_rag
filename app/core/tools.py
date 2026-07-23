"""
LangChain tool definitions for the tool-calling agent.

Each tool wraps a piece of functionality already built elsewhere in the app
(retrieval, summarization) so the agent can decide WHEN to use them based on
the user's question, rather than always running the same fixed RAG chain.
"""

from langchain_core.tools import tool
from app.core.retriever import hybrid_search
from app.core.reranker import rerank


@tool
def search_documents(query: str) -> str:
    """
    Searches the uploaded documents for information relevant to the query.
    Use this whenever the user asks a question that might be answered by
    the content of their uploaded PDF/DOCX files.
    """
    candidates = hybrid_search(query)
    if not candidates:
        return "No relevant information found in the uploaded documents."

    top_chunks = rerank(query, candidates)

    formatted = "\n\n---\n\n".join(
        f"[Source: {c.get('source_filename', 'unknown')}]\n{c['text']}" for c in top_chunks
    )
    return formatted


@tool
def summarize_document(filename: str) -> str:
    """
    Retrieves and summarizes the content of a specific uploaded document by
    filename. Use this when the user asks for a summary or overview of a
    particular document rather than a specific fact.
    """
    # broad query to pull a representative sample of chunks from that doc
    candidates = hybrid_search(f"main topics and key points of {filename}", top_k=15)
    doc_chunks = [c for c in candidates if c.get("source_filename") == filename]

    if not doc_chunks:
        return f"Could not find a document named '{filename}'. Check the exact filename."

    combined_text = "\n\n".join(c["text"] for c in doc_chunks[:8])
    return f"Content excerpts from {filename}:\n\n{combined_text}"


@tool
def calculator(expression: str) -> str:
    """
    Evaluates a basic arithmetic expression (e.g. '12 * 4 + 7').
    Use this for any math the user asks about, instead of computing it yourself.
    """
    import ast
    import operator

    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](eval_node(node.operand))
        raise ValueError("Unsupported expression")

    try:
        tree = ast.parse(expression, mode="eval")
        result = eval_node(tree.body)
        return str(result)
    except Exception:
        return "Could not evaluate that expression. Please provide valid arithmetic."


# List of all tools available to the agent
ALL_TOOLS = [search_documents, summarize_document, calculator]

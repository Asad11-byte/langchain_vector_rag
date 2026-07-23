"""
Query endpoint: receives a question from the frontend, runs the RAG chain,
returns the answer with cited sources.
"""

import traceback

from fastapi import APIRouter, HTTPException

from app.core.chain import answer_question
from app.core.agent import answer_with_agent
from app.models.requests import QueryRequest
from app.models.responses import QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Plain RAG chain: retrieve -> rerank -> generate. Always searches documents."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = answer_question(question=request.question)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return QueryResponse(answer=result["answer"], sources=result["sources"])


@router.post("/query/agent")
async def query_documents_with_agent(request: QueryRequest):
    """
    Tool-calling agent: the LLM decides whether to search documents,
    summarize a file, use the calculator, or answer directly.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = answer_with_agent(question=request.question)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent query failed: {str(e)}")

    return result
"""
Query rewriting techniques to improve retrieval recall before hitting the
vector store. Two common approaches included:

  - rewrite_query()  -> LLM rephrases the user's question to be clearer/more
                          specific (fixes vague or poorly-worded queries)
  - multi_query()    -> LLM generates several variations of the question,
                          each retrieves separately, results are merged/deduped
                          (increases recall by approaching the question from
                          multiple angles)

Try both (and neither, as a baseline) for your query-rewriting experiment.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings


def _get_llm():
    return ChatGroq(model="llama3-70b-8192", api_key=settings.groq_api_key, temperature=0)


REWRITE_PROMPT = ChatPromptTemplate.from_template(
    "Rewrite the following user question to be clearer and more specific for "
    "a document search system. Keep it concise. Only return the rewritten "
    "question, nothing else.\n\nQuestion: {question}"
)

MULTI_QUERY_PROMPT = ChatPromptTemplate.from_template(
    "Generate {n} different versions of the following question to help "
    "retrieve relevant documents from a vector database. Each version should "
    "approach the question from a different angle or use different phrasing. "
    "Return ONLY the questions, one per line, no numbering.\n\nQuestion: {question}"
)


def rewrite_query(question: str) -> str:
    """Single LLM-rephrased version of the question."""
    chain = REWRITE_PROMPT | _get_llm() | StrOutputParser()
    return chain.invoke({"question": question}).strip()


def multi_query(question: str, n: int = 3) -> list[str]:
    """Generates n alternative phrasings of the question (includes the original)."""
    chain = MULTI_QUERY_PROMPT | _get_llm() | StrOutputParser()
    raw = chain.invoke({"question": question, "n": n})
    variations = [line.strip() for line in raw.split("\n") if line.strip()]
    return [question] + variations

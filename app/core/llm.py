"""
Single LLM factory used by chain.py, agent.py, and query_rewrite.py.
Reads `llm_provider` from settings so switching providers (Groq/OpenAI/
Anthropic) is a one-line .env change instead of editing every file.
"""

from functools import lru_cache
from app.config import settings


@lru_cache
def get_llm(temperature: float = 0.2):
    """Returns a chat model instance based on settings.llm_provider."""
    provider = settings.llm_provider.lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.llm_model,
            api_key=settings.groq_api_key,
            temperature=temperature,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.llm_model or "gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=temperature,
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.llm_model or "claude-3-5-sonnet-20241022",
            api_key=settings.anthropic_api_key,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown llm_provider: {provider}")
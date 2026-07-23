"""
Tool-calling agent: gives the LLM access to multiple tools (document search,
summarization, calculator) and lets it decide which to call based on the
user's question.

IMPLEMENTATION NOTE: this uses a manual tool-calling loop built on
`llm.bind_tools()` instead of `langchain.agents.create_tool_calling_agent` /
`AgentExecutor`. Those higher-level helpers have shifted their exact import
path across recent LangChain versions (and Groq's tool-calling support
plugs in more predictably at the bind_tools level), so this approach is
more stable and easier to debug -- you can see exactly what's happening at
each step instead of it being hidden inside a black-box executor.

Satisfies the "Extend: implement tool calling using LangChain" requirement.
"""

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.core.llm import get_llm
from app.core.tools import ALL_TOOLS

AGENT_SYSTEM_PROMPT = """You are a helpful assistant with access to the
user's uploaded documents and a calculator.

- Use `search_documents` for questions about specific facts in the documents.
- Use `summarize_document` when the user asks for an overview/summary of a
  particular file.
- Use `calculator` for any arithmetic.
- If none of the tools are relevant, answer directly from your own knowledge,
  but be clear when you're not using the documents.

Always cite which document a fact came from when you use search_documents."""

TOOLS_BY_NAME = {t.name: t for t in ALL_TOOLS}


def answer_with_agent(question: str, max_iterations: int = 5) -> dict:
    """
    Runs the question through a manual tool-calling loop:
      1. Send the conversation to the LLM with tools bound.
      2. If it responds with tool call(s), execute them and feed results back.
      3. Repeat until the LLM responds with a plain answer (no more tool calls)
         or max_iterations is hit.

    Returns {answer: str, tool_calls: list[str]}.
    """
    llm = get_llm(temperature=0.2)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    messages = [
        SystemMessage(content=AGENT_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    tool_calls_made = []

    for _ in range(max_iterations):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        tool_calls = getattr(response, "tool_calls", None)
        if not tool_calls:
            # no more tools requested -> this is the final answer
            return {"answer": response.content, "tool_calls": tool_calls_made}

        for call in tool_calls:
            tool_name = call["name"]
            tool_args = call["args"]
            tool_calls_made.append(tool_name)

            tool_fn = TOOLS_BY_NAME.get(tool_name)
            if tool_fn is None:
                result = f"Unknown tool: {tool_name}"
            else:
                try:
                    result = tool_fn.invoke(tool_args)
                except Exception as e:
                    result = f"Tool '{tool_name}' failed: {str(e)}"

            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )

    # hit max_iterations without a final answer
    return {
        "answer": "I wasn't able to fully resolve this after several tool calls. "
                  "Please try rephrasing your question.",
        "tool_calls": tool_calls_made,
    }
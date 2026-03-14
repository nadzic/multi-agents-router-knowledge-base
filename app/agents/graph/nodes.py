"""Graph node implementations."""

from typing import Any, Dict

from pydantic import BaseModel, Field

from .state import AgentInput, Classification, RouterState

CLASSIFY_SYSTEM_PROMPT = """Analyze this query and determine which knowledge bases to consult.
For each relevant source, generate a targeted sub-question optimized for that source.

Available sources:
- github: Code, API references, implementation details, issues, pull requests
- notion: Internal documentation, processes, policies, team wikis
- slack: Team discussions, informal knowledge sharing, recent conversations

Return ONLY the sources that are relevant to the query. Each source should have
a targeted sub-question optimized for that specific knowledge domain.

Example for "How do I authenticate API requests?":
- github: "What authentication code exists? Search for auth middleware, JWT handling"
- notion: "What authentication documentation exists? Look for API auth guides"
(slack omitted because it's not relevant for this technical question)"""


def synthesis_system_prompt(original_query: str) -> str:
  """Build synthesis instructions for final answer node."""
  return f"""Synthesize these search results to answer the original question: "{original_query}"

- Combine information from multiple sources without redundancy
- Highlight the most relevant and actionable information
- Note any discrepancies between sources
- Keep the response concise and well-organized"""


class ClassificationResult(BaseModel):
  """Structured output schema for classifier node."""

  classifications: list[Classification] = Field(
    description="List of sources to invoke with their targeted sub-questions."
  )


def _invoke_source_agent(agent: Any, source: str, query: str) -> dict:
  result = agent.invoke({"messages": [{"role": "user", "content": query}]})
  return {"results": [{"source": source, "result": result["messages"][-1].content}]}


def create_nodes(router_llm: Any, source_agents: Dict[str, Any]) -> Dict[str, Any]:
  """Create node callables with injected dependencies."""

  def classify_query(state: RouterState) -> dict:
    structured_llm = router_llm.with_structured_output(ClassificationResult)
    result = structured_llm.invoke(
      [
        {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
        {"role": "user", "content": state["query"]},
      ]
    )
    return {"classifications": result.classifications}

  def query_github(state: AgentInput) -> dict:
    return _invoke_source_agent(source_agents["github"], "github", state["query"])

  def query_notion(state: AgentInput) -> dict:
    return _invoke_source_agent(source_agents["notion"], "notion", state["query"])

  def query_slack(state: AgentInput) -> dict:
    return _invoke_source_agent(source_agents["slack"], "slack", state["query"])

  def synthesize_results(state: RouterState) -> dict:
    results = state.get("results", [])
    if not results:
      return {"final_answer": "No results found from any source."}

    formatted = [f"**From {item['source'].title()}:**\n{item['result']}" for item in results]
    synthesis_response = router_llm.invoke(
      [
        {"role": "system", "content": synthesis_system_prompt(state["query"])},
        {"role": "user", "content": "\n\n".join(formatted)},
      ]
    )
    return {"final_answer": synthesis_response.content}

  return {
    "classify_query": classify_query,
    "query_github": query_github,
    "query_notion": query_notion,
    "query_slack": query_slack,
    "synthesize_results": synthesize_results,
  }

"""LangGraph node functions for the router workflow.

This module contains the core runtime logic:
- classify the incoming query into source-specific sub-queries
- fan out to source nodes
- normalize source results
- synthesize a final answer
"""

from typing import Any

from langchain.chat_models import init_chat_model
from langgraph.types import Send

try:
  # Package-relative imports for API/runtime usage.
  from .agents import github_agent, notion_agent, slack_agent
  from .router_prompts import CLASSIFY_SYSTEM_PROMPT, synthesis_system_prompt
  from .router_schemas import ClassificationResult
  from .state import AgentInput, RouterState
except ImportError:
  # Script-style fallback for direct module execution.
  from agents import github_agent, notion_agent, slack_agent
  from router_prompts import CLASSIFY_SYSTEM_PROMPT, synthesis_system_prompt
  from router_schemas import ClassificationResult
  from state import AgentInput, RouterState

# LLM used for classification and final synthesis.
router_llm = init_chat_model("openai:gpt-4.1-mini")


def classify_query(state: RouterState) -> dict:
  """Classify the original query into source-specific sub-questions.

  Args:
    state: Current router graph state containing the original query.

  Returns:
    A state patch with a `classifications` list.
  """

  structured_llm = router_llm.with_structured_output(ClassificationResult)

  result = structured_llm.invoke(
    [
      {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
      {"role": "user", "content": state["query"]},
    ]
  )

  return {"classifications": result.classifications}


def route_to_agents(state: RouterState) -> list[Send]:
  """Convert classification decisions into LangGraph fan-out sends.

  Args:
    state: Router state that includes `classifications`.

  Returns:
    A list of `Send` objects targeting source nodes with `AgentInput` payloads.
  """

  return [
    Send(classification["source"], {"query": classification["query"]})
    for classification in state["classifications"]
  ]


def _invoke_domain_agent(agent: Any, source: str, query: str) -> dict:
  """Invoke one source-specific agent and normalize response shape.

  Args:
    agent: Compiled LangGraph/LangChain runnable for the source.
    source: Source identifier (`github`, `notion`, or `slack`).
    query: Source-targeted sub-question.

  Returns:
    A state patch containing one `results` entry.
  """

  result = agent.invoke({"messages": [{"role": "user", "content": query}]})
  return {"results": [{"source": source, "result": result["messages"][-1].content}]}


def query_github(state: AgentInput) -> dict:
  """Run the GitHub agent node."""
  return _invoke_domain_agent(github_agent, "github", state["query"])


def query_notion(state: AgentInput) -> dict:
  """Run the Notion agent node."""
  return _invoke_domain_agent(notion_agent, "notion", state["query"])


def query_slack(state: AgentInput) -> dict:
  """Run the Slack agent node."""
  return _invoke_domain_agent(slack_agent, "slack", state["query"])


def synthesize_results(state: RouterState) -> dict:
  """Synthesize source outputs into one final user-facing answer.

  Args:
    state: Router graph state containing original query and source results.

  Returns:
    A state patch containing `final_answer`.
  """

  results = state.get("results", [])
  if not results:
    return {"final_answer": "No results found from any source."}

  formatted = [
    f"**From {item['source'].title()}:**\n{item['result']}" for item in results
  ]
  synthesis_response = router_llm.invoke(
    [
      {"role": "system", "content": synthesis_system_prompt(state["query"])},
      {"role": "user", "content": "\n\n".join(formatted)},
    ]
  )

  return {"final_answer": synthesis_response.content}

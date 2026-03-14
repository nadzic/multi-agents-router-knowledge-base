"""Model and source-agent factory helpers."""

from typing import Any, Dict

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from ..tools import (
  get_page,
  get_thread,
  search_code,
  search_issues,
  search_notion,
  search_prs,
  search_slack,
)


def init_router_model():
  """Create the router/synthesis LLM instance."""
  return init_chat_model("openai:gpt-4.1-mini")


def init_source_model():
  """Create the shared LLM for source-specific agents."""
  return init_chat_model("openai:gpt-4.1")


def create_source_agents(model: Any) -> Dict[str, Any]:
  """Create source-specific react agents keyed by source name."""
  github_agent = create_react_agent(
    model=model,
    tools=[search_code, search_issues, search_prs],
    prompt=(
      "You are a GitHub expert. Answer questions about code, API references, "
      "and implementation details by searching repositories, issues, and pull requests."
    ),
  )
  notion_agent = create_react_agent(
    model=model,
    tools=[search_notion, get_page],
    prompt=(
      "You are a Notion expert. Answer questions about internal processes, "
      "policies, and team documentation by searching the organization's workspace."
    ),
  )
  slack_agent = create_react_agent(
    model=model,
    tools=[search_slack, get_thread],
    prompt=(
      "You are a Slack expert. Answer questions by searching relevant threads "
      "and discussions where team members shared practical solutions."
    ),
  )
  return {"github": github_agent, "notion": notion_agent, "slack": slack_agent}

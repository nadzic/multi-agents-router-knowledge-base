"""Agent construction for each knowledge source.

This module centralizes:
- environment loading
- model initialization
- source-specific react-agent creation
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

try:
  from .tools import (
    search_code,
    search_issues,
    search_prs,
    search_notion,
    get_page,
    search_slack,
    get_thread,
  )
except ImportError:
  from tools import (
    search_code,
    search_issues,
    search_prs,
    search_notion,
    get_page,
    search_slack,
    get_thread,
  )

# Load project .env and support OPEN_API_KEY alias.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
if not os.getenv("OPENAI_API_KEY") and os.getenv("OPEN_API_KEY"):
  os.environ["OPENAI_API_KEY"] = os.environ["OPEN_API_KEY"]

# Shared chat model used by all source agents.
model = init_chat_model("openai:gpt-4.1")

# Agent focused on source-code and repository history.
github_agent = create_react_agent(
  model=model, 
  tools=[search_code, search_issues, search_prs],
  prompt=("You are a GitHub expert. Answer questions about code, "
  "API references, and implementation details by searching "
  "repositories, issues, and pull requests."
  ),
)

# Agent focused on process/documentation knowledge.
notion_agent = create_react_agent(
  model=model,
  tools=[search_notion, get_page],
  prompt=(
      "You are a Notion expert. Answer questions about internal "
      "processes, policies, and team documentation by searching "
      "the organization's Notion workspace."
    ),
)

# Agent focused on conversational/internal team context.
slack_agent = create_react_agent(
  model=model,
  tools=[search_slack, get_thread],
  prompt=(
      "You are a Slack expert. Answer questions by searching "
      "relevant threads and discussions where team members have "
      "shared knowledge and solutions."
  ),

)

"""Top-level agent entrypoints.

This module exposes public functions used by API routes and scripts.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.run_helpers import traceable, tracing_context

from .graph import build_workflow
from .llm.model import create_source_agents, init_router_model, init_source_model

# Load project .env and support OPEN_API_KEY alias.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
if not os.getenv("OPENAI_API_KEY") and os.getenv("OPEN_API_KEY"):
  os.environ["OPENAI_API_KEY"] = os.environ["OPEN_API_KEY"]


def _resolve_langsmith_project() -> str:
  return (
    os.getenv("LANGSMITH_PROJECT")
    or os.getenv("LANGCHAIN_PROJECT")
    or "multi-agents-router-knowledge-base"
  )


def initialize_workflow():
  """Initialize and compile workflow to validate runtime readiness."""
  router_llm = init_router_model()
  source_model = init_source_model()
  source_agents = create_source_agents(source_model)
  return build_workflow(router_llm, source_agents)


@traceable(name="agents.run_query", run_type="chain")
def run_query(query: str) -> dict:
  """Run query against compiled router workflow."""
  workflow = initialize_workflow()
  return workflow.invoke({"query": query})


def run_query_with_tracing(query: str) -> dict:
  """Run query with explicit LangSmith tracing context."""
  client = Client()
  with tracing_context(
    enabled=True,
    client=client,
    project_name=_resolve_langsmith_project(),
  ):
    return run_query(query)

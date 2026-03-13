"""Runnable entrypoint for the router workflow demo.

Use this module for local execution, quick smoke tests, and as a simple
template when converting the workflow into a reusable script/CLI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.run_helpers import traceable, tracing_context

try:
  # Package import path (used by FastAPI and tests).
  from .router_graph import build_router_workflow
except ImportError:
  # Script-style fallback (used when running `python my_agent/router_workflow.py`).
  from router_graph import build_router_workflow

# Ensure env vars are available for LangSmith/OpenAI initialization.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def _resolve_langsmith_project() -> str:
  """Resolve LangSmith project name from env with safe fallback."""
  return (
    os.getenv("LANGSMITH_PROJECT")
    or os.getenv("LANGCHAIN_PROJECT")
    or "multi-agents-router-knowledge-base"
  )


@traceable(name="router_workflow.run_demo", run_type="chain")
def run_demo(query: str) -> dict:
  """Execute the compiled router workflow for a single query.

  Args:
    query: The top-level user question to route and answer.

  Returns:
    Final graph state including routing decisions and `final_answer`.
  """
  # Build fresh workflow instance per request for clear isolation in demos.
  workflow = build_router_workflow()
  return workflow.invoke({"query": query})


def run_demo_with_tracing(query: str) -> dict:
  """Execute workflow with explicit LangSmith tracing context.

  Args:
    query: The top-level user question to process.

  Returns:
    Final graph state.
  """

  client = Client()
  # Explicit tracing context ensures runs appear under selected project name.
  with tracing_context(
    enabled=True,
    client=client,
    project_name=_resolve_langsmith_project(),
  ):
    return run_demo(query)


if __name__ == "__main__":
  # Local demonstration query; replace with any query while iterating.
  result = run_demo_with_tracing("How do I authenticate API requests?")

  print("Original Query:", result["query"])
  print()
  print("Classifications:")
  for classification in result.get("classifications", []):
    print(f"  - {classification['source']}: {classification['query']}")
  print("\n" + "=" * 60 + "\n")
  print("Final answer:")
  print(result.get("final_answer", "No final answer generated."))
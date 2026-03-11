"""Graph assembly for the multi-source router workflow."""

from langgraph.graph import END, START, StateGraph

from router_nodes import (
  classify_query,
  query_github,
  query_notion,
  query_slack,
  route_to_agents,
  synthesize_results,
)
from state import RouterState


def build_router_workflow():
  """Build and compile the router workflow graph.

  Graph layout:
    START -> classify -> (github | notion | slack in parallel) -> synthesize -> END

  Returns:
    A compiled LangGraph runnable workflow.
  """

  return (
    StateGraph(RouterState)
    .add_node("classify", classify_query)
    .add_node("github", query_github)
    .add_node("notion", query_notion)
    .add_node("slack", query_slack)
    .add_node("synthesize", synthesize_results)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_agents, ["github", "notion", "slack"])
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
  )

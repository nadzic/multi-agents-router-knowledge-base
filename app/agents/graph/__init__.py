"""Graph builder package."""

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from .edges import route_to_agents
from .nodes import create_nodes
from .state import RouterState


def build_workflow(router_llm: Any, source_agents: Dict[str, Any]):
  """Build and compile router workflow graph."""
  nodes = create_nodes(router_llm, source_agents)
  return (
    StateGraph(RouterState)
    .add_node("classify", nodes["classify_query"])
    .add_node("github", nodes["query_github"])
    .add_node("notion", nodes["query_notion"])
    .add_node("slack", nodes["query_slack"])
    .add_node("synthesize", nodes["synthesize_results"])
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_agents, ["github", "notion", "slack"])
    .add_edge("github", "synthesize")
    .add_edge("notion", "synthesize")
    .add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile()
  )

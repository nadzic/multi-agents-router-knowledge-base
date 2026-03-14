"""Graph edge helpers (routing/fanout)."""

from langgraph.types import Send

from agent.graph.state import RouterState


def route_to_agents(state: RouterState) -> list[Send]:
  """Fan out classifier decisions to source nodes."""
  return [
    Send(classification["source"], {"query": classification["query"]})
    for classification in state["classifications"]
  ]

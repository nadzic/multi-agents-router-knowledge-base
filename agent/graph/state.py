"""State contracts used by the router graph."""

from typing import Annotated, Literal
import operator
from typing_extensions import NotRequired, TypedDict


class AgentInput(TypedDict):
  """Input payload for a source node."""

  query: str


class AgentOutput(TypedDict):
  """Output payload from a source node."""

  source: str
  result: str


class Classification(TypedDict):
  """One routing decision emitted by classifier."""

  source: Literal["github", "notion", "slack"]
  query: str


class RouterState(TypedDict):
  """Global graph state."""

  query: str
  classifications: NotRequired[list[Classification]]
  results: NotRequired[Annotated[list[AgentOutput], operator.add]]
  final_answer: NotRequired[str]

"""Shared typed state definitions for the router workflow.

This module defines the TypedDict contracts passed between LangGraph nodes.
Keeping these types in one place makes it easier to reuse the workflow in
scripts, tests, and future APIs.
"""

from typing import Annotated, Literal
import operator
from typing_extensions import NotRequired, TypedDict


class AgentInput(TypedDict):
  """Input payload delivered to a source-specific agent node.

  Attributes:
    query: A targeted sub-question produced by the classifier node.
  """

  query: str


class AgentOutput(TypedDict):
  """Normalized output produced by any source-specific agent node.

  Attributes:
    source: The source label that produced the answer (`github`, `notion`, `slack`).
    result: The textual answer returned by that source-specific agent.
  """

  source: str
  result: str


class Classficiation(TypedDict):
  """A single routing decision returned by the classifier node.

  Attributes:
    source: Target source node to call.
    query: Source-optimized sub-question.
  """

  source: Literal["github", "notion", "slack"]
  query: str


class RouterState(TypedDict):
  """Global graph state that flows through all nodes.

  Attributes:
    query: The original user question.
    classifications: Optional list of routing decisions produced by classification.
    results: Optional reducer-backed list that aggregates source outputs.
    final_answer: Optional final synthesized answer for the original query.
  """

  query: str
  classifications: NotRequired[list[Classficiation]]
  # Reducer collects parallel node outputs into a single list.
  results: NotRequired[Annotated[list[AgentOutput], operator.add]]
  final_answer: NotRequired[str]
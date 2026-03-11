"""Pydantic schemas used by router LLM structured outputs."""

from pydantic import BaseModel, Field

from state import Classficiation


class ClassificationResult(BaseModel):
  """Structured router output produced by the classifier LLM.

  Attributes:
    classifications: Source-specific routing decisions (source + targeted query).
  """

  classifications: list[Classficiation] = Field(
    description="List of agents to invoke with their targeted sub-questions."
  )

"""Slack source tools."""

from langchain.tools import tool


@tool
def search_slack(query: str) -> str:
  """Search Slack messages and threads for team knowledge."""
  return "Found discussion in #engineering: 'Use Bearer tokens for API auth, see docs for refresh flow'"


@tool
def get_thread(thread_id: str) -> str:
  """Retrieve a specific Slack thread by ID."""
  return f"Thread {thread_id} discusses best practices for API key rotation"

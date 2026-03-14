"""Notion source tools."""

from langchain.tools import tool


@tool
def search_notion(query: str) -> str:
  """Search Notion workspace for documentation."""
  return "Found documentation: 'API Authentication Guide' - covers OAuth2 flow, API keys, and JWT tokens"


@tool
def get_page(page_id: str) -> str:
  """Retrieve a specific Notion page by ID."""
  return f"Page content for {page_id}: Step-by-step authentication setup instructions"

"""GitHub source tools."""

from langchain.tools import tool


@tool
def search_code(query: str, repo: str = "main") -> str:
  """Search repository code for implementation details."""
  return f"Found code matching '{query}' in {repo}: authentication middleware in src/auth.py"


@tool
def search_issues(query: str) -> str:
  """Search GitHub issues related to the query."""
  return f"Found 3 issues matching '{query}': #142 (API auth docs), #89 (OAuth flow), #203 (token refresh)"


@tool
def search_prs(query: str) -> str:
  """Search pull requests for implementation history."""
  return f"PR #156 added JWT authentication, PR #178 updated OAuth scopes"

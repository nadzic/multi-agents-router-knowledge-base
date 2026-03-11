"""Tool definitions used by source-specific agents.

These are currently lightweight mock implementations intended for local demos.
Swap each function body with real API integrations when moving to production.
"""

from langchain.tools import tool


@tool
def search_code(query: str, repo: str = "main") -> str:
  """Search repository code for relevant implementation details.

  Args:
    query: Search terms derived from the routed sub-question.
    repo: Repository identifier or alias.

  Returns:
    A short summary of matching code findings.
  """

  return f"Found code matching '{query}' in {repo}: authentication middleware in src/auth.py"


@tool
def search_issues(query: str) -> str:
  """Search GitHub issues for discussions related to a query.

  Args:
    query: Search terms derived from the routed sub-question.

  Returns:
    A summary of issue matches.
  """

  return f"Found 3 issues matching '{query}': #142 (API auth docs), #89 (OAuth flow), #203 (token refresh)"


@tool
def search_prs(query: str) -> str:
  """Search pull requests for implementation context.

  Args:
    query: Search terms derived from the routed sub-question.

  Returns:
    A summary of relevant pull requests.
  """

  return f"PR #156 added JWT authentication, PR #178 updated OAuth scopes"


@tool
def search_notion(query: str) -> str:
  """Search Notion workspace for related documentation.

  Args:
    query: Search terms derived from the routed sub-question.

  Returns:
    A short summary of relevant documentation.
  """

  return f"Found documentation: 'API Authentication Guide' - covers OAuth2 flow, API keys, and JWT tokens"


@tool
def get_page(page_id: str) -> str:
  """Retrieve a specific Notion page by ID.

  Args:
    page_id: Notion page identifier.

  Returns:
    A short page content summary.
  """

  return f"Page content: Step-by-step authentication setup instructions"


@tool
def search_slack(query: str) -> str:
  """Search Slack conversations for relevant team knowledge.

  Args:
    query: Search terms derived from the routed sub-question.

  Returns:
    A summary of matching Slack discussion(s).
  """

  return f"Found discussion in #engineering: 'Use Bearer tokens for API auth, see docs for refresh flow'"


@tool
def get_thread(thread_id: str) -> str:
  """Retrieve a specific Slack thread by ID.

  Args:
    thread_id: Slack thread identifier.

  Returns:
    A short summary of thread content.
  """

  return f"Thread discusses best practices for API key rotation"
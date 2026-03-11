"""Prompt templates used by router nodes."""

CLASSIFY_SYSTEM_PROMPT = """Analyze this query and determine which knowledge bases to consult.
For each relevant source, generate a targeted sub-question optimized for that source.

Available sources:
- github: Code, API references, implementation details, issues, pull requests
- notion: Internal documentation, processes, policies, team wikis
- slack: Team discussions, informal knowledge sharing, recent conversations

Return ONLY the sources that are relevant to the query. Each source should have
a targeted sub-question optimized for that specific knowledge domain.

Example for "How do I authenticate API requests?":
- github: "What authentication code exists? Search for auth middleware, JWT handling"
- notion: "What authentication documentation exists? Look for API auth guides"
(slack omitted because it's not relevant for this technical question)"""


def synthesis_system_prompt(original_query: str) -> str:
  """Build synthesis instructions for the final answer node.

  Args:
    original_query: The top-level user query from graph state.

  Returns:
    Prompt text guiding the synthesis model behavior.
  """

  return f"""Synthesize these search results to answer the original question: "{original_query}"

- Combine information from multiple sources without redundancy
- Highlight the most relevant and actionable information
- Note any discrepancies between sources
- Keep the response concise and well-organized"""

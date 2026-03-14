"""Unit tests for router node behavior."""

from types import SimpleNamespace

from agent.graph.edges import route_to_agents
from agent.graph.nodes import create_nodes


def test_classify_query_returns_classifications(monkeypatch):
  """Classifier node should return structured classifications patch."""

  expected = [
    {"source": "github", "query": "search code auth middleware"},
    {"source": "notion", "query": "find auth policy docs"},
  ]

  class FakeStructuredLLM:
    def invoke(self, _messages):
      return SimpleNamespace(classifications=expected)

  class FakeLLM:
    def with_structured_output(self, _schema):
      return FakeStructuredLLM()

  nodes = create_nodes(FakeLLM(), {"github": object(), "notion": object(), "slack": object()})

  patch = nodes["classify_query"]({"query": "How do we authenticate API requests?"})
  assert patch == {"classifications": expected}


def test_route_to_agents_builds_send_payloads():
  """Router should emit one Send per classification with AgentInput payload."""

  sends = route_to_agents(
    {
      "query": "q",
      "classifications": [
        {"source": "github", "query": "q1"},
        {"source": "slack", "query": "q2"},
      ],
    }
  )

  assert [send.node for send in sends] == ["github", "slack"]
  assert [send.arg for send in sends] == [{"query": "q1"}, {"query": "q2"}]


def test_invoke_domain_agent_normalizes_output():
  """Domain agent wrapper should normalize message output into results list."""

  class FakeAgent:
    def invoke(self, _payload):
      return {"messages": [SimpleNamespace(content="result from source")]}

  nodes = create_nodes(object(), {"github": FakeAgent(), "notion": FakeAgent(), "slack": FakeAgent()})
  patch = nodes["query_github"]({"query": "sub-query"})
  assert patch == {
    "results": [{"source": "github", "result": "result from source"}]
  }


def test_synthesize_results_returns_default_when_empty():
  """Synthesis node should return a default answer when no results exist."""

  nodes = create_nodes(object(), {"github": object(), "notion": object(), "slack": object()})
  patch = nodes["synthesize_results"]({"query": "q", "results": []})
  assert patch == {"final_answer": "No results found from any source."}


def test_synthesize_results_formats_and_invokes_llm():
  """Synthesis node should send formatted source results to the LLM."""
  captured_messages = {}

  class FakeLLM:
    def invoke(self, messages):
      captured_messages["value"] = messages
      return SimpleNamespace(content="Combined final answer")

  nodes = create_nodes(FakeLLM(), {"github": object(), "notion": object(), "slack": object()})

  patch = nodes["synthesize_results"](
    {
      "query": "How do I authenticate API requests?",
      "results": [
        {"source": "github", "result": "Use JWT middleware."},
        {"source": "notion", "result": "Follow OAuth2 guide."},
      ],
    }
  )

  assert patch == {"final_answer": "Combined final answer"}
  assert captured_messages["value"][0]["role"] == "system"
  assert "How do I authenticate API requests?" in captured_messages["value"][0]["content"]
  assert "**From Github:**" in captured_messages["value"][1]["content"]
  assert "**From Notion:**" in captured_messages["value"][1]["content"]

"""Unit tests for workflow entrypoint helpers."""

from contextlib import contextmanager

from my_agent import router_workflow


def _unwrap(func):
  """Return undecorated function when available."""
  return getattr(func, "__wrapped__", func)


def test_run_demo_invokes_compiled_workflow(monkeypatch):
  """run_demo should build the graph and invoke with query payload."""
  captured_payload = {}

  class FakeWorkflow:
    def invoke(self, payload):
      captured_payload["value"] = payload
      return {"query": payload["query"], "final_answer": "ok"}

  monkeypatch.setattr(router_workflow, "build_router_workflow", lambda: FakeWorkflow())

  result = _unwrap(router_workflow.run_demo)("test query")
  assert captured_payload["value"] == {"query": "test query"}
  assert result["final_answer"] == "ok"


def test_run_demo_with_tracing_uses_context(monkeypatch):
  """run_demo_with_tracing should enable tracing context and call run_demo."""
  captured = {"enabled": None, "client": None, "called_query": None, "project_name": None}

  class FakeClient:
    pass

  @contextmanager
  def fake_tracing_context(enabled, client, project_name):
    captured["enabled"] = enabled
    captured["client"] = client
    captured["project_name"] = project_name
    yield

  def fake_run_demo(query):
    captured["called_query"] = query
    return {"query": query, "final_answer": "from run_demo"}

  monkeypatch.setattr(router_workflow, "Client", FakeClient)
  monkeypatch.setattr(router_workflow, "tracing_context", fake_tracing_context)
  monkeypatch.setattr(router_workflow, "run_demo", fake_run_demo)

  result = router_workflow.run_demo_with_tracing("trace me")
  assert captured["enabled"] is True
  assert isinstance(captured["client"], FakeClient)
  assert isinstance(captured["project_name"], str)
  assert captured["called_query"] == "trace me"
  assert result["final_answer"] == "from run_demo"

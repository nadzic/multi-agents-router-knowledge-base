"""API route tests for health/readiness and query execution."""

from fastapi.testclient import TestClient

from app.api.main import app
from app.api import routes_query
from app.agents import agent as app_agent


client = TestClient(app)


def test_healthz_returns_ok():
  """Liveness endpoint should always return OK."""
  response = client.get("/api/healthz")
  assert response.status_code == 200
  assert response.json() == {"status": "ok"}


def test_query_route_success(monkeypatch):
  """Query endpoint should return workflow response payload."""

  def fake_run_query_with_tracing(query: str):
    return {
      "query": query,
      "classifications": [{"source": "github", "query": "check auth code"}],
      "final_answer": "Use middleware + JWT.",
    }

  monkeypatch.setattr(routes_query, "run_query_with_tracing", fake_run_query_with_tracing)

  response = client.post("/api/query", json={"query": "How do I authenticate API requests?"})
  assert response.status_code == 200
  assert response.json()["query"] == "How do I authenticate API requests?"
  assert response.json()["final_answer"] == "Use middleware + JWT."
  assert response.json()["classifications"][0]["source"] == "github"


def test_query_route_failure_returns_500(monkeypatch):
  """Query endpoint should map internal exceptions to HTTP 500."""

  def fake_run_query_with_tracing(_query: str):
    raise RuntimeError("workflow exploded")

  monkeypatch.setattr(routes_query, "run_query_with_tracing", fake_run_query_with_tracing)

  response = client.post("/api/query", json={"query": "test"})
  assert response.status_code == 500
  assert "Failed to process query" in response.json()["detail"]


def test_readyz_returns_ready_when_checks_pass(monkeypatch):
  """Readiness endpoint should return ready when env and workflow init are healthy."""
  monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
  monkeypatch.setenv("LANGSMITH_TRACING", "false")
  monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
  monkeypatch.setattr(app_agent, "initialize_workflow", lambda: object())

  response = client.get("/api/readyz")
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "ready"
  assert payload["checks"]["env"] == "ok"
  assert payload["checks"]["workflow"] == "ok"


def test_readyz_returns_503_when_openai_key_missing(monkeypatch):
  """Readiness endpoint should return not_ready when OPENAI_API_KEY is missing."""
  monkeypatch.delenv("OPENAI_API_KEY", raising=False)
  monkeypatch.setenv("LANGSMITH_TRACING", "false")
  monkeypatch.setattr(app_agent, "initialize_workflow", lambda: object())

  response = client.get("/api/readyz")
  assert response.status_code == 503
  payload = response.json()
  assert payload["status"] == "not_ready"
  assert "OPENAI_API_KEY" in payload["checks"]["env"]

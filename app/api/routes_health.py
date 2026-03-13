"""Health and readiness routes.

`healthz` is a liveness check (process is up).
`readyz` is a readiness check (dependencies/config are usable).
"""

import os

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router: APIRouter = APIRouter()

@router.get("/healthz")
async def healthz() -> dict:
  """Liveness probe endpoint.

  Returns:
    Static OK payload while API process is responsive.
  """

  return {"status": "ok"}

@router.get("/readyz")
async def readyz() -> dict:
  """Readiness probe endpoint with config/workflow checks.

  Readiness conditions:
  - `OPENAI_API_KEY` must be set.
  - If tracing is enabled, `LANGSMITH_API_KEY` must be set.
  - Router workflow must initialize successfully.

  Returns:
    - 200 with detailed check results when ready.
    - 503 with detailed check results when not ready.
  """

  checks: dict[str, str] = {}
  is_ready = True

  # Validate required environment variables.
  missing_vars: list[str] = []
  if not os.getenv("OPENAI_API_KEY"):
    missing_vars.append("OPENAI_API_KEY")

  tracing_enabled = os.getenv("LANGSMITH_TRACING", "").lower() == "true"
  if tracing_enabled and not os.getenv("LANGSMITH_API_KEY"):
    missing_vars.append("LANGSMITH_API_KEY")

  if missing_vars:
    is_ready = False
    checks["env"] = f"missing: {', '.join(missing_vars)}"
  else:
    checks["env"] = "ok"

  try:
    # Import lazily so readiness can report import/init failures clearly
    # and to avoid doing heavy startup work in module import time.
    from my_agent.router_graph import build_router_workflow

    build_router_workflow()
    checks["workflow"] = "ok"
  except Exception as exc:
    is_ready = False
    checks["workflow"] = f"error: {type(exc).__name__}: {exc}"

  payload = {
    "status": "ready" if is_ready else "not_ready",
    "checks": checks,
  }
  if is_ready:
    return payload

  # 503 indicates the instance should not receive production traffic yet.
  return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload)
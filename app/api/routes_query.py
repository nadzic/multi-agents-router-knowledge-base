"""Query route for executing the LangGraph workflow via HTTP."""

from fastapi import APIRouter, HTTPException

from app.schemas.query import QueryRequest, QueryResponse
from my_agent.router_workflow import run_demo_with_tracing

router: APIRouter = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
  """Execute one query against the multi-source router workflow.

  Args:
    request: API input containing the user query string.

  Returns:
    `QueryResponse` with routed classifications and final synthesized answer.

  Raises:
    HTTPException: Wrapped internal errors as status code 500.
  """

  try:
    result = run_demo_with_tracing(request.query)
    # Map workflow state shape into API response schema.
    return QueryResponse(
      query=result["query"],
      classifications=result.get("classifications", []),
      final_answer=result.get("final_answer", ""),
    )
  except Exception as exc:
    # Keep an explicit API-safe error while preserving root cause server-side.
    raise HTTPException(status_code=500, detail=f"Failed to process query: {exc}") from exc

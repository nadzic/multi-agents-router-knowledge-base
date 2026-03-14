"""FastAPI application entrypoint.

This module wires API route groups into a single app instance used by local
development (`uvicorn`) and production deployments.
"""

from fastapi import FastAPI, APIRouter

from app.api.routes_health import router as router_health
from app.api.routes_query import router as router_query

# Root ASGI application.
app: FastAPI = FastAPI()

# Group all version-less API routes under `/api`.
api_router: APIRouter = APIRouter(prefix="/api")

api_router.include_router(router_health)
api_router.include_router(router_query)

app.include_router(api_router)

@app.get("/")
async def read_root() -> dict:
  """Simple root endpoint useful for quick local smoke tests."""
  return {"message": "Hello, World!"}

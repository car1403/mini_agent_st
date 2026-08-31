"""MEMORY 도메인의 API Endpoint를 제공합니다."""

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.providers.registry import (
    provider_status,
    run_with_optional_fallback,
)
from app.rag.policies import search as search_policies
from app.repositories.store import store
from app.schemas import (
    AgentDecisionRequest,
    AgentRunRequest,
    ApiResponse,
    EvaluationRunRequest,
    KnowledgeSearchRequest,
    MemoryCreateRequest,
    ProviderGenerateRequest,
    ToolRunRequest,
    ToolSelectRequest,
    TravelExtractRequest,
    TravelPlan,
)
from app.services.evaluation_service import run_evaluation
from app.services.travel_service import (
    add_memory,
    extract_travel_request,
    new_trace_id,
)
from app.agents.mock_selector import select_tool
from app.tools.executor import run_tool
from app.workflows.langgraph_travel_workflow import (
    resume_langgraph_run,
    start_langgraph_run,
)
from app.routers.common import ok

memory_router = APIRouter(tags=["05 · Memory"])


@memory_router.get("/api/users/{user_id}/memories", response_model=ApiResponse)
def list_memories(user_id: str) -> ApiResponse:
    return ok(store.list_memories(user_id))


@memory_router.post("/api/users/{user_id}/memories", response_model=ApiResponse)
def create_memory(user_id: str, payload: MemoryCreateRequest) -> ApiResponse:
    try:
        return ok(add_memory(user_id, payload.key, payload.value))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@memory_router.delete("/api/users/{user_id}/memories/{memory_id}", response_model=ApiResponse)
def delete_memory(user_id: str, memory_id: str) -> ApiResponse:
    if not store.delete_memory(user_id, memory_id):
        raise HTTPException(status_code=404, detail="Memory를 찾을 수 없습니다.")
    return ok({"deleted": True})

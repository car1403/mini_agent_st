"""AGENT 도메인의 API Endpoint를 제공합니다."""

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

agent_router = APIRouter(tags=["Agent"])


@agent_router.post("/api/agent/runs", response_model=ApiResponse)
def create_run(payload: AgentRunRequest) -> ApiResponse:
    return ok(start_langgraph_run(payload.model_dump()))


@agent_router.get("/api/agent/runs/{run_id}", response_model=ApiResponse)
def get_run(run_id: str) -> ApiResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return ok(run)


@agent_router.post("/api/agent/runs/{run_id}/approve", response_model=ApiResponse)
def approve_run(run_id: str, payload: AgentDecisionRequest) -> ApiResponse:
    try:
        result = resume_langgraph_run(
            run_id, "approve", payload.actor, payload.note
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if result is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return ok(result)


@agent_router.post("/api/agent/runs/{run_id}/reject", response_model=ApiResponse)
def reject_run(run_id: str, payload: AgentDecisionRequest) -> ApiResponse:
    try:
        result = resume_langgraph_run(
            run_id, "reject", payload.actor, payload.note
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if result is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return ok(result)

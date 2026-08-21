"""TOOL 도메인의 API Endpoint를 제공합니다."""

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
    KnowledgeSearchRequest,
    MemoryCreateRequest,
    ProviderGenerateRequest,
    ToolRunRequest,
    ToolSelectRequest,
    TravelExtractRequest,
    TravelPlan,
)
from app.services.travel_service import (
    add_memory,
    create_agent_run,
    decide_run,
    extract_travel_request,
    new_trace_id,
)
from app.agents.mock_selector import select_tool
from app.tools.executor import run_tool
from app.routers.common import ok

tool_router = APIRouter(tags=["03 · Tool"])


@tool_router.post("/api/tools/select", response_model=ApiResponse)
def choose_tool(payload: ToolSelectRequest) -> ApiResponse:
    return ok(select_tool(payload.message))


@tool_router.post("/api/tools/run", response_model=ApiResponse)
def execute_tool(payload: ToolRunRequest) -> ApiResponse:
    try:
        return ok(run_tool(payload.tool_name, payload.arguments))
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

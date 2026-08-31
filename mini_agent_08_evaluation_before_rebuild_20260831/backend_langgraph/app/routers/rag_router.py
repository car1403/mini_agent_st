"""RAG 도메인의 API Endpoint를 제공합니다."""

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

rag_router = APIRouter(tags=["04 · RAG"])


@rag_router.post("/api/knowledge/search", response_model=ApiResponse)
def knowledge(payload: KnowledgeSearchRequest) -> ApiResponse:
    results = search_policies(payload.query, payload.limit)
    return ok({"grounded": bool(results), "documents": results})

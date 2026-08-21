"""EVALUATION 도메인의 API Endpoint를 제공합니다."""

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
    create_agent_run,
    decide_run,
    extract_travel_request,
    new_trace_id,
)
from app.agents.mock_selector import select_tool
from app.tools.executor import run_tool
from app.routers.common import ok

evaluation_router = APIRouter(tags=["08 · Evaluation"])


@evaluation_router.post("/api/evaluations/run", response_model=ApiResponse)
def evaluate_agent(payload: EvaluationRunRequest) -> ApiResponse:
    scenarios = [item.model_dump() for item in payload.scenarios]
    return ok(run_evaluation(scenarios or None))

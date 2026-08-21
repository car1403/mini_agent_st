"""PROVIDER 도메인의 API Endpoint를 제공합니다."""

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

provider_router = APIRouter(tags=["01 · Provider"])


@provider_router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "agent_type": "python",
        "llm_provider": settings.llm_provider,
        "storage_mode": settings.storage_mode,
    }


@provider_router.get("/api/providers/status", response_model=ApiResponse)
def providers() -> ApiResponse:
    return ok(
        {
            "active": settings.llm_provider,
            "fallback_enabled": settings.llm_fallback_enabled,
            "providers": provider_status(),
        }
    )


@provider_router.post("/api/providers/generate", response_model=ApiResponse)
def generate(payload: ProviderGenerateRequest) -> ApiResponse:
    try:
        result = run_with_optional_fallback(
            lambda provider: provider.generate(payload.system_prompt, payload.message),
            payload.provider,
        )
        return ok(result.to_dict())
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {error}") from error


@provider_router.post("/api/providers/travel-plan", response_model=ApiResponse)
def generate_travel_plan(payload: ProviderGenerateRequest) -> ApiResponse:
    try:
        result = run_with_optional_fallback(
            lambda provider: provider.generate_structured(
                payload.system_prompt,
                payload.message,
                TravelPlan,
            ),
            payload.provider,
        )
        return ok(result.to_dict())
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {error}") from error


@provider_router.post("/api/travel/extract", response_model=ApiResponse)
def extract(payload: TravelExtractRequest) -> ApiResponse:
    return ok(extract_travel_request(payload.message, payload.reference_date))

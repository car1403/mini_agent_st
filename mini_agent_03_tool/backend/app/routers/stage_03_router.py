"""Mini Agent 03의 Tool 선택·안전 실행·단일 Agent Cycle API를 제공합니다.

`app.main`이 등록하며 Swagger의 `03 · Tool과 Agent` 그룹에 표시됩니다.
"""

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.agents.travel_agent import run_travel_agent, select_travel_tool
from app.core.config import settings
from app.schemas.stage_03 import (
    ToolCompareRequest, ToolCompareResult, ToolComparisonItem,
    ToolCompleteRequest, ToolCompleteResult, ToolRunRequest, ToolRunResult,
    ToolSelectRequest, ToolSelectionResult,
)
from app.tools.executor import execute_tool_safely
from app.tools.registry import get_tool_definitions


stage_03_router = APIRouter(tags=["03 · Tool과 Agent"])


@stage_03_router.get("/api/tools")
def tools() -> dict:
    """[목록 조회] Agent나 Tool을 실행하지 않고 허용된 Tool 명세만 반환합니다."""
    return {"tools": get_tool_definitions(), "note": "모든 Tool은 Allowlist를 통해 실행됩니다."}


@stage_03_router.post("/api/tools/select", response_model=ToolSelectionResult)
def choose_tool(payload: ToolSelectRequest) -> ToolSelectionResult:
    """[Agent 사용] Travel Agent가 LLM을 이용해 Tool과 arguments만 선택하며 Tool은 실행하지 않습니다."""
    selected = payload.provider or settings.llm_provider
    try:
        return ToolSelectionResult.model_validate(asdict(select_travel_tool(selected, payload.message, payload.tool_choice)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} Tool 선택에 실패했습니다: {error}") from error


@stage_03_router.post("/api/tools/compare", response_model=ToolCompareResult)
def compare_tool_selection(payload: ToolCompareRequest) -> ToolCompareResult:
    """[Agent 사용] Provider별로 Travel Agent의 Tool 선택 결과만 비교하며 Tool은 실행하지 않습니다."""
    items = []
    for selected in payload.providers:
        try:
            decision = ToolSelectionResult.model_validate(asdict(select_travel_tool(selected, payload.message, payload.tool_choice)))
            items.append(ToolComparisonItem(provider=selected, status="success", decision=decision))
        except Exception as error:
            items.append(ToolComparisonItem(provider=selected, status="error", error=str(error)))
    return ToolCompareResult(request_count=len(payload.providers), results=items)


@stage_03_router.post("/api/tools/run", response_model=ToolRunResult)
def execute_tool(payload: ToolRunRequest) -> ToolRunResult:
    """[Tool 직접 사용] Agent나 LLM의 판단 없이 요청에 지정된 Tool을 Backend가 바로 실행합니다."""
    return execute_tool_safely(payload.tool_name, payload.arguments)


@stage_03_router.post("/api/tools/complete", response_model=ToolCompleteResult)
def complete_tool_loop(payload: ToolCompleteRequest) -> ToolCompleteResult:
    """[Agent 사용] Travel Agent가 Tool 선택·실행·최종 답변 생성의 전체 Cycle을 수행합니다."""
    selected = payload.provider or settings.llm_provider
    try:
        return run_travel_agent(selected, payload.message, payload.tool_choice)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} Agent Cycle 실패: {error}") from error

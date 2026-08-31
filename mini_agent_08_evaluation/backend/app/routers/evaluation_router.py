import requests
from fastapi import APIRouter, HTTPException

from ..evaluation.loader import load_suite
from ..evaluation.live_adapter import evaluate_live_waiting
from ..evaluation.runner import run_suite
from ..schemas.evaluation import EvaluationRequest, LiveEvaluationRequest


router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.get("/scenarios")
def scenarios() -> dict[str, object]:
    suite, _ = load_suite()
    return {"total": len(suite), "scenarios": suite}


@router.post("/run")
def evaluate_all(request: EvaluationRequest) -> dict[str, object]:
    return run_suite(inject_regression=request.inject_regression)


@router.post("/live")
def evaluate_live(request: LiveEvaluationRequest) -> dict[str, object]:
    try:
        return evaluate_live_waiting(request.api_base_url, request.actor_id, request.question)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except requests.RequestException as error:
        raise HTTPException(status_code=503, detail=f"Mini Agent 07 연결 실패: {error}") from error

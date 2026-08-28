from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.workflows.learning_graphs import (
    compare_workflows, graph_components, run_branch, run_checkpoint, run_loop,
)
from app.workflows.advanced_learning_graphs import run_advanced_graph, run_llm_node, stream_graph


learning_router = APIRouter(prefix="/api/learning/graph", tags=["Beginner Graph"])


class BranchRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class LoopRequest(BaseModel):
    budget: int = Field(gt=0)
    max_iterations: int = Field(default=1, ge=0, le=5)


class ThreadRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=100)


class LlmNodeRequest(BranchRequest):
    provider: str = "mock"


class AdvancedGraphRequest(LlmNodeRequest):
    user_id: str = Field(default="demo-user", min_length=1, max_length=100)


@learning_router.get("/components")
def components() -> dict:
    return graph_components()


@learning_router.post("/branch")
def branch(payload: BranchRequest) -> dict:
    return run_branch(payload.message)


@learning_router.post("/loop")
def loop(payload: LoopRequest) -> dict:
    return run_loop(payload.budget, payload.max_iterations)


@learning_router.post("/checkpoint")
def checkpoint(payload: ThreadRequest) -> dict:
    return run_checkpoint(payload.thread_id)


@learning_router.post("/compare")
def compare(payload: BranchRequest) -> dict:
    return compare_workflows(payload.message)


@learning_router.post("/stream")
def stream(payload: BranchRequest) -> dict:
    return stream_graph(payload.message)


@learning_router.post("/llm-node")
def llm_node(payload: LlmNodeRequest) -> dict:
    try:
        return run_llm_node(payload.message, payload.provider)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"LLM Node 실패: {error}") from error


@learning_router.post("/advanced")
def advanced(payload: AdvancedGraphRequest) -> dict:
    try:
        return run_advanced_graph(payload.user_id, payload.message, payload.provider)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Advanced Graph 실패: {error}") from error

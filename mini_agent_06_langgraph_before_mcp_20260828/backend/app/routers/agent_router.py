from fastapi import APIRouter

from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_service import run_agent


router = APIRouter(prefix="/api/agent", tags=["LangGraph AI Agent"])


@router.get("/status")
def status() -> dict[str, str]:
    return {"status": "ready", "agent": "openai-travel-agent", "orchestrator": "langgraph"}


@router.post("/run", response_model=AgentResponse)
def execute_agent(request: AgentRequest) -> AgentResponse:
    return run_agent(request)

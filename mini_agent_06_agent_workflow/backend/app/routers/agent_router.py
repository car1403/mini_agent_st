from fastapi import APIRouter, HTTPException

from app.mcp.client import connection_status
from app.schemas.agent import AgentRequest, AgentResponse, AgentSummary
from app.services.agent_service import execute_single_agent, list_agents


router = APIRouter(prefix="/api/agents", tags=["Independent Single Agents"])


@router.get("", response_model=list[AgentSummary])
def agents() -> list[AgentSummary]:
    return list_agents()


@router.get("/mcp-status")
async def mcp_status():
    try:
        return await connection_status()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"MCP Server 연결 실패: {error}") from error


@router.post("/run", response_model=AgentResponse)
async def run(request: AgentRequest) -> AgentResponse:
    try:
        return await execute_single_agent(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Agent 실행 실패: {error}") from error

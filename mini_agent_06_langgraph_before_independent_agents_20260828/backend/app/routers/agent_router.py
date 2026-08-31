from fastapi import APIRouter, HTTPException

from app.mcp.client import connection_status
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_service import run_agent


router = APIRouter(prefix="/api/agent", tags=["LangGraph AI Agent"])


@router.get("/mcp-status")
async def mcp_status():
    try:
        return await connection_status()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Travel MCP Server 연결 실패: {error}") from error


@router.post("/run", response_model=AgentResponse)
async def execute_agent(request: AgentRequest) -> AgentResponse:
    try:
        return await run_agent(request)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Agent 실행 실패: {error}") from error

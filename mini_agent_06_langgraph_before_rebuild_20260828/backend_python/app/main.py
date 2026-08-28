from fastapi import FastAPI

from app.routers.provider_router import provider_router
from app.routers.tool_router import tool_router
from app.routers.rag_router import rag_router
from app.routers.memory_router import memory_router
from app.routers.agent_router import agent_router


app = FastAPI(
    title="Mini Agent 06 · LangGraph",
    description="여행 Agent 교육용 Mock First API",
    version="1.0.0",
)
app.include_router(provider_router)
app.include_router(tool_router)
app.include_router(rag_router)
app.include_router(memory_router)
app.include_router(agent_router)

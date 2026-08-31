from fastapi import FastAPI

from app.routers.agent_router import router


app = FastAPI(
    title="Mini Agent 06 · LangGraph AI Agent",
    description="OpenAI AI Agent의 Tool Loop를 LangGraph로 관리하는 입문 프로젝트",
    version="1.0.0",
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Mini Agent 06 API", "docs": "/docs"}

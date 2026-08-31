from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.evaluation_router import router as evaluation_router


app = FastAPI(title="Mini Agent 08 · Evaluation")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(evaluation_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

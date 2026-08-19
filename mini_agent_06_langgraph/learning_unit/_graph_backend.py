"""실제 LangGraph 예제가 공유하는 Mini Agent 06 학습 API Client입니다."""

import os
from typing import Any
import httpx

BASE_URL = os.getenv("LANGGRAPH_API_URL", "http://127.0.0.1:8001").rstrip("/")
PROVIDER = os.getenv("GRAPH_EXAMPLE_PROVIDER", "mock")

def post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = httpx.post(f"{BASE_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()

def print_help(error: httpx.HTTPError) -> None:
    print("Mini Agent 06 호출 실패:", error)
    print("LangGraph Backend와 Provider 설정을 확인하세요.")

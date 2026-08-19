"""실제 Memory 예제가 공유하는 Mini Agent 05 API Client입니다."""

import os
from typing import Any
import httpx

BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
PROVIDER = os.getenv("MEMORY_EXAMPLE_PROVIDER", "mock")

def request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = httpx.request(method, f"{BASE_URL}{path}", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()

def print_help(error: httpx.HTTPError) -> None:
    print("Mini Agent 05 호출 실패:", error)
    print("Backend·Redis·PostgreSQL과 환경 변수를 확인하세요.")

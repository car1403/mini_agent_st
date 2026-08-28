"""Conditional Edge의 Tool 경로와 안전 실행 결과를 확인합니다."""

import httpx
from _graph_backend import PROVIDER, post, print_help

if __name__ == "__main__":
    try:
        result = post("/api/learning/graph/advanced", {"user_id": "demo-user", "message": "부산 날씨를 알려줘", "provider": PROVIDER})
        print("경로:", result["route"])
        print("Tool Call:", result["tool_call"])
        print("Tool Result:", result["tool_result"])
        print("Trace:", result["trace"])
    except httpx.HTTPError as error:
        print_help(error)

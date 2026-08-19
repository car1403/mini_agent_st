"""Mini Agent Backend에서 Provider별 Tool 선택과 안전 실행을 확인합니다."""

import os

import httpx


BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")
QUESTION = "오늘 부산 날씨를 알려줘"


def post(path: str, payload: dict) -> dict:
    # 4xx/5xx 응답은 즉시 예외로 바꿔 실패를 정상 결과와 구분합니다.
    response = httpx.post(f"{BACKEND_API_URL}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # 동일 질문을 보내 Provider별 Tool 선택 차이와 개별 실패를 관찰합니다.
    comparison = post(
        "/api/tools/compare",
        {"providers": ["mock", "gemini", "openai", "ollama"], "message": QUESTION},
    )
    print("1. Provider별 Tool 선택")
    for item in comparison["results"]:
        print(item)

    # 비교 다음에는 재현 가능한 Mock 하나로 안전 실행 단계를 확인합니다.
    decision = post("/api/tools/select", {"provider": "mock", "message": QUESTION})
    print("\n2. Mock Tool Call", decision)

    if decision.get("needs_clarification"):
        # 필수 입력이 빠졌다면 Tool을 실행하지 않고 사용자에게 되묻습니다.
        print("추가 질문:", decision["follow_up_question"])
    elif decision["tool_name"]:
        # 제안된 이름과 arguments를 Backend 검증 API에 전달해 실행합니다.
        result = post(
            "/api/tools/run",
            {"tool_name": decision["tool_name"], "arguments": decision["arguments"]},
        )
        print("\n3. Backend 검증과 Tool Result", result)

"""실제 Provider의 구조화 여행 계획을 결정적 규칙으로 평가합니다."""

import argparse
import json
import os
from urllib.request import Request, urlopen


def call_provider(api_url: str, provider: str) -> dict:
    """API Key를 노출하지 않고 Mini Agent Backend를 통해 LLM을 호출합니다."""
    payload = {"provider": provider, "message": "부산의 대표 장소를 포함한 2박 3일 여행 계획을 만들어 주세요."}
    request = Request(f"{api_url.rstrip('/')}/api/providers/travel-plan", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))["data"]


def evaluate(result: dict) -> dict:
    """가변적인 문장 대신 구조·목적지·일수·활동을 검사합니다."""
    plan = result.get("content", {})
    checks = {
        "structured_output": isinstance(plan, dict),
        "destination_grounded": "부산" in str(plan.get("destination", "")),
        "days_in_range": isinstance(plan.get("recommended_days"), int) and 1 <= plan["recommended_days"] <= 30,
        "has_activities": bool(plan.get("activities")),
    }
    return {"provider": result.get("provider"), "model": result.get("model"), "latency_ms": result.get("latency_ms"), "passed": all(checks.values()), "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["mock", "openai", "gemini", "ollama"], default="openai")
    parser.add_argument("--api-url", default=os.getenv("MINI_AGENT_API_URL", "http://localhost:8000"))
    args = parser.parse_args()
    print(json.dumps(evaluate(call_provider(args.api_url, args.provider)), ensure_ascii=False, indent=2))

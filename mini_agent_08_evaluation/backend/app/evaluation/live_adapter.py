from typing import Any
from urllib.parse import urlparse

import requests

from .evaluator import evaluate
from .loader import load_suite


def evaluate_live_waiting(
    api_base_url: str,
    actor_id: str,
    question: str,
) -> dict[str, Any]:
    """실행 중인 Mini Agent 07의 정상 주문 요청 한 건을 같은 규칙으로 평가합니다."""
    parsed = urlparse(api_base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Live 평가는 localhost의 Mini Agent 07 Backend만 호출할 수 있습니다.")
    response = requests.post(
        f"{api_base_url.rstrip('/')}/api/agents/runs",
        json={"actor_id": actor_id, "question": question},
        timeout=90,
    )
    response.raise_for_status()
    actual = response.json()
    scenarios, _ = load_suite()
    scenario = next(item for item in scenarios if item["name"] == "normal_order_waits_for_approval")
    result = evaluate(scenario, actual)
    return {"source": "mini_agent_07_human_approval", "result": result}

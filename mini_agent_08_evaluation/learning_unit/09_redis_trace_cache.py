"""최근 실패 Trace만 Redis에 TTL로 저장하는 선택 예제입니다."""

import json
import os
from urllib.request import Request, urlopen

from redis import Redis


if __name__ == "__main__":
    api_url = os.getenv("MINI_AGENT_API_URL", "http://localhost:8000")
    request = Request(f"{api_url.rstrip('/')}/api/evaluations/run", data=b'{"scenarios": []}', headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=60) as response:
        evaluation = json.loads(response.read().decode("utf-8"))["data"]
    client = Redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"), decode_responses=True)
    ttl = int(os.getenv("EVALUATION_TRACE_TTL_SECONDS", "600"))
    keys = []
    # 영구 이력과 역할이 겹치지 않도록 실패 Trace만 짧게 캐시합니다.
    for index, result in enumerate(evaluation["results"], start=1):
        if not result["passed"]:
            key = f"evaluation:failed-trace:{index}"
            client.setex(key, ttl, json.dumps(result["trace"], ensure_ascii=False))
            keys.append(key)
    print({"cached_failed_traces": keys, "ttl_seconds": ttl})

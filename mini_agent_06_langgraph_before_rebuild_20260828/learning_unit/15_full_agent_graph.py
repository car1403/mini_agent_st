"""LLM·Tool·RAG·Memory를 하나의 Graph Trace로 확인합니다."""

import httpx
from _graph_backend import PROVIDER, post, print_help

if __name__ == "__main__":
    try:
        result = post("/api/learning/graph/advanced", {"user_id": "demo-user", "message": "부산 관광지를 추천해줘", "provider": PROVIDER})
        for index, event in enumerate(result["trace"], start=1):
            print(f"{index}. {event['node']} · {event['latency_ms']}ms · {event}")
        print("최종 답변:", result["answer"])
    except httpx.HTTPError as error:
        print_help(error)

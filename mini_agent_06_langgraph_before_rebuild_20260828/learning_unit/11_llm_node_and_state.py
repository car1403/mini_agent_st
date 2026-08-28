"""실제 LLM Node의 응답과 Provider Trace를 확인합니다."""

import httpx
from _graph_backend import PROVIDER, post, print_help

if __name__ == "__main__":
    try:
        result = post("/api/learning/graph/llm-node", {"message": "제주 여행의 장점을 한 문장으로 알려줘", "provider": PROVIDER})
        print("Provider:", result["provider"], result["model"])
        print("응답:", result["content"])
        print("Trace:", result["trace"])
    except httpx.HTTPError as error:
        print_help(error)

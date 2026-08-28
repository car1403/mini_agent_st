"""Provider Node 오류와 명시적 Fallback 정책을 관찰합니다."""

import httpx
from _graph_backend import post, print_help

if __name__ == "__main__":
    try:
        print(post("/api/learning/graph/llm-node", {"message": "테스트", "provider": "openai"}))
    except httpx.HTTPStatusError as error:
        print("예상한 Provider 오류:", error.response.status_code, error.response.text)
        print("Fallback은 LLM_FALLBACK_ENABLED를 켠 경우에만 사용합니다.")
    except httpx.HTTPError as error:
        print_help(error)

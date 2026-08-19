"""관련 장기 Memory만 사용해 실제 LLM 개인화 답변을 생성합니다."""

import httpx
from _memory_backend import PROVIDER, print_help, request

if __name__ == "__main__":
    try:
        result = request("POST", "/api/memory/personalize", {"user_id": "user-a", "question": "호텔을 추천해 줘", "storage": "postgres", "provider": PROVIDER})
        print("사용 Memory:", result["used_memories"])
        print("답변:", result["answer"])
        print("Trace:", result["trace"])
    except httpx.HTTPError as error:
        print_help(error)

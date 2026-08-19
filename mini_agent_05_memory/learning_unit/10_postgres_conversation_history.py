"""PostgreSQL 대화 이력을 사용자·Session별로 복원합니다."""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        for role, content in (("user", "부산 여행을 준비 중이야."), ("assistant", "기간을 알려주세요."), ("user", "2박 3일이야.")):
            result = request("POST", "/api/memory/conversations", {"user_id": "user-a", "session_id": "trip-01", "role": role, "content": content})
        print("최근 대화:", result["messages"])
        print("다른 사용자:", request("GET", "/api/memory/conversations/user-b/trip-01"))
    except httpx.HTTPError as error:
        print_help(error)

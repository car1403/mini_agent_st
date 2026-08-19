"""Redis Session의 사용자 격리와 Sliding TTL을 확인합니다."""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        for user, city in (("user-a", "부산"), ("user-b", "제주")):
            request("POST", "/api/memory/sessions", {"user_id": user, "session_id": "trip", "state": {"city": city}})
        # 같은 session_id도 user_id가 다르면 별도 Redis Key로 저장됩니다.
        print("A:", request("GET", "/api/memory/sessions/trip?user_id=user-a"))
        print("B:", request("GET", "/api/memory/sessions/trip?user_id=user-b"))
        print("TTL 연장:", request("GET", "/api/memory/sessions/trip?user_id=user-a&refresh_ttl=true"))
    except httpx.HTTPError as error:
        print_help(error)

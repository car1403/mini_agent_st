"""Redis WATCH/MULTI와 version으로 덮어쓰기 충돌을 방지합니다."""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        request("POST", "/api/memory/sessions", {"user_id": "user-a", "session_id": "atomic", "state": {"city": "부산"}})
        print(request("PATCH", "/api/memory/sessions", {"user_id": "user-a", "session_id": "atomic", "changes": {"guests": 2}, "expected_version": 0}))
        # 이미 소비된 version 0을 다시 쓰면 HTTP 409가 발생합니다.
        request("PATCH", "/api/memory/sessions", {"user_id": "user-a", "session_id": "atomic", "changes": {"guests": 4}, "expected_version": 0})
    except httpx.HTTPStatusError as error:
        print("예상한 충돌:", error.response.status_code, error.response.text)
    except httpx.HTTPError as error:
        print_help(error)

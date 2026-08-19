"""Redis 단기 상태와 PostgreSQL 장기 정보를 함께 복원합니다."""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        request("POST", "/api/memory/sessions", {"user_id": "user-a", "session_id": "hybrid", "state": {"step": "hotel_search"}})
        request("POST", "/api/memory/items", {"user_id": "user-a", "key": "transportation", "value": "대중교통", "storage": "postgres"})
        print(request("GET", "/api/memory/restore/user-a/hybrid"))
    except httpx.HTTPError as error:
        print_help(error)

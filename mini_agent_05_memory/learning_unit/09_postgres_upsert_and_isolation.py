"""PostgreSQL 장기 Memory의 upsert와 사용자 격리를 확인합니다."""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        base = {"user_id": "user-a", "key": "hotel_preference", "storage": "postgres"}
        first = request("POST", "/api/memory/items", {**base, "value": "조용한 호텔"})
        second = request("POST", "/api/memory/items", {**base, "value": "조용하고 금연인 호텔"})
        print("같은 ID:", first["id"] == second["id"])
        print("user-a:", request("GET", "/api/memory/items/user-a?storage=postgres"))
        print("user-b:", request("GET", "/api/memory/items/user-b?storage=postgres"))
    except httpx.HTTPError as error:
        print_help(error)

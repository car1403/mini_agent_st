"""사용자 장기 Memory의 내보내기와 전체 삭제를 확인합니다."""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("삭제 전:", request("GET", "/api/memory/export/user-a"))
        print("삭제 결과:", request("DELETE", "/api/memory/users/user-a"))
        print("삭제 후:", request("GET", "/api/memory/export/user-a"))
    except httpx.HTTPError as error:
        print_help(error)

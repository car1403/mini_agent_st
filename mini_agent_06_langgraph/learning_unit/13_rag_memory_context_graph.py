"""RAG와 Memory를 별도 Context Node에서 불러옵니다."""

import httpx
from _graph_backend import PROVIDER, post, print_help

if __name__ == "__main__":
    try:
        result = post("/api/learning/graph/advanced", {"user_id": "demo-user", "message": "숙소 취소 정책을 설명해줘", "provider": PROVIDER})
        # Context Node를 분리하면 검색 문서와 Memory 사용 여부를 독립적으로 검사할 수 있습니다.
        print("Memory:", result["memories"])
        print("RAG:", result["documents"])
        print("답변:", result["answer"])
    except httpx.HTTPError as error:
        print_help(error)

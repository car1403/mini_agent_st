"""graph.stream()의 Node별 State update를 관찰합니다."""

import httpx
from _graph_backend import post, print_help

if __name__ == "__main__":
    try:
        result = post("/api/learning/graph/stream", {"message": "부산 날씨를 알려줘"})
        # invoke와 달리 실행 중 각 Node가 반환한 부분 변경값을 순서대로 확인합니다.
        for index, event in enumerate(result["events"], start=1):
            print(f"{index}. {event['node']} → {event['update']}")
    except httpx.HTTPError as error:
        print_help(error)

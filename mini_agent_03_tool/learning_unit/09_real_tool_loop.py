"""선택부터 Tool Result 기반 최종 답변까지 실제 Agent Trace를 출력합니다."""

import httpx
from _tool_backend import complete_loop, print_help

if __name__ == "__main__":
    try:
        # complete API는 각 단계를 trace 배열에 순서대로 기록합니다.
        result = complete_loop("오늘 부산 날씨와 기온을 알려줘.")
        # Provider마다 내부 응답 형식이 달라도 동일한 Trace 구조로 확인할 수 있습니다.
        for index, item in enumerate(result["trace"], start=1):
            print(f"\n{index}. {item['stage']}")
            print(item["data"])
        print("\n최종 답변:", result["final_answer"])
    except httpx.HTTPError as error:
        print_help(error)

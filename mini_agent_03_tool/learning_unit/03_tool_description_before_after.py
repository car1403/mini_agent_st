"""모호한 Tool 설명과 명확한 설명이 LLM 선택에 미치는 영향을 비교합니다."""

import httpx
from _tool_backend import print_help, print_result, select_tool

QUESTION = "내일 부산에서 비가 오는지 확인해 줘."

if __name__ == "__main__":
    try:
        # Tool 이름과 입력 Schema는 유지하고 description의 구체성만 바꿉니다.
        print_result("Before · 모호한 설명", select_tool(QUESTION, description_variant="vague"))
        print_result("After · 명확한 설명", select_tool(QUESTION, description_variant="clear"))
    except httpx.HTTPError as error:
        print_help(error)

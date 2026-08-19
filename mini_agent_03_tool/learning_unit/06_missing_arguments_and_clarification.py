"""필수 arguments가 부족하면 추측하지 않고 추가 질문을 반환합니다."""

import httpx
from _tool_backend import print_help, print_result, select_tool

# 도시·날짜·인원 등 제공 정보의 양이 다른 요청을 비교합니다.
QUESTIONS = ["숙소를 찾아줘.", "부산 숙소를 찾아줘.", "서울 관광지를 추천해 줘."]

if __name__ == "__main__":
    try:
        for question in QUESTIONS:
            # Backend는 빠진 값을 임의로 만들지 않고 missing_arguments와 추가 질문을 반환합니다.
            print_result(question, select_tool(question))
    except httpx.HTTPError as error:
        print_help(error)

"""auto, none, required Tool Choice를 같은 질문으로 비교합니다."""

import httpx
from _tool_backend import print_help, print_result, select_tool

QUESTION = "여행이 주는 장점을 설명해 줘."

if __name__ == "__main__":
    try:
        # auto는 모델 판단, none은 호출 금지, required는 반드시 하나를 선택하게 합니다.
        for mode in ("auto", "none", "required"):
            print_result(mode, select_tool(QUESTION, tool_choice=mode))
    except httpx.HTTPError as error:
        print_help(error)

"""Provider가 반환한 원본 Tool Call과 정규화 결과를 관찰합니다."""

import httpx
from _tool_backend import print_help, select_tool

if __name__ == "__main__":
    try:
        # Provider 응답은 Backend에서 공통 ToolSelectionResult 형태로 정규화됩니다.
        decision = select_tool("내일 제주 날씨와 기온을 알려줘.")
        print("1. Provider:", decision["provider"], decision["model"])
        print("2. 원본 Tool Call:", decision["raw_tool_call"])
        print("3. 정규화 Tool 이름:", decision["tool_name"])
        print("4. 정규화 arguments:", decision["arguments"])
        # 정규화 후에도 필수값 누락 여부를 별도로 검사해야 안전하게 실행할 수 있습니다.
        print("5. 누락 arguments:", decision["missing_arguments"])
        print("중요: 아직 Tool 함수는 실행되지 않았습니다.")
    except httpx.HTTPError as error:
        print_help(error)

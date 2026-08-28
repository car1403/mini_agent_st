# 06 LangGraph Workflow 과제

교육 상담 요청을 처리하는 작은 Graph를 설계합니다.

필수 Node:

- `inspect_request`: 과목과 학습 수준 확인
- `ask_user`: 정보가 부족하면 추가 질문
- `create_plan`: Mock 학습 계획 생성
- `validate_plan`: 주당 학습 시간 검증
- `revise`: 검증 실패 시 한 번 수정
- `finish`, `fail`: 정상 또는 실패 종료

필수 조건:

- Node는 변경값만 반환합니다.
- Routing 함수는 다음 Node 이름만 반환합니다.
- 반복 횟수를 State에서 확인할 수 있습니다.
- 최대 반복 횟수 후 `fail`로 종료합니다.
- `Annotated`와 Reducer를 사용해 실행된 Node 순서를 `trace`에 누적합니다.
- 같은 입력의 일반 Python Workflow와 결과를 비교합니다.
- 완성한 Graph의 Mermaid 텍스트를 출력하고 실행 흐름을 설명합니다.

기본 과제에는 실제 LLM·Tool·RAG를 넣지 않아도 됩니다. 선택 확장에서는 LLM 생성
Node, 조회 Tool Node, Context Node 중 하나를 추가하고 실행 Trace를 제출합니다.
승인 `interrupt()`와 상태 변경 Tool은 이번 과제에 넣지 않습니다.

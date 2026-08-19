# Mini Agent 08 · Evaluation과 Tracing

완성한 여행 Agent를 작은 시나리오로 반복 검사하고, 실패하면 Trace에서 원인을 찾습니다.

## 학습 순서

| 메뉴 | 주제 | 핵심 실습 |
|---|---|---|
| 8-1 | 평가가 필요한 이유 | 실행 성공과 올바른 행동 구분 |
| 8-2 | 시나리오 하나 | 입력·기대·실제 결과 비교 |
| 8-3 | 여러 시나리오 | 실제 평가 API와 통과율 |
| 8-4 | Trace 실패 찾기 | 처음 실패한 검사 확인 |
| 8-5 | 회귀 테스트 | 기준 결과와 현재 결과 비교 |
| 8-6 | Provider 비교 | GPT·Gemini·Ollama 선택 확장 |
| 8-7 | 실제 LLM 평가 | 구조화 응답의 안정적인 필드 검사 |
| 8-8 | PostgreSQL 평가 이력 | 실행별 결과 저장과 회귀 조회 |
| 8-9 | Redis Trace 캐시 | 최근 실패 Trace의 TTL 저장 |

8-1~8-5는 Mock 기반이며 외부 API Key 없이 반복할 수 있습니다. 8-6~8-7은 실제 Provider 설정과 비용을 확인합니다. 8-8은 `DATABASE_URL`, 8-9는 `REDIS_URL`을 사용합니다.

## 폴더 역할

- `learning_unit`: 강의 예제·실습·과제
- `steps`: 메뉴 8-1~8-9와 같은 순서의 실행 예제
- `backend_python`: 일반 Python Agent와 평가 API
- `backend_langgraph`: LangGraph Agent와 같은 평가 API
- `frontend`: 평가 결과·Trace·회귀 비교 화면

평가 보고서에는 API Key, 전체 시스템 Prompt, 개인정보를 저장하지 않습니다.

# Mini Agent 08 · Evaluation

07에서 만든 **Safe Order Agent**를 Scenario로 평가하는 초보자용 미니 프로젝트입니다. 새로운 Agent를 하나 더 만드는 단계가 아니라, 이미 만든 Agent가 올바르고 안전하게 행동하는지 확인하는 단계입니다.

```text
저장된 Agent Result
  → Scenario별 Check
  → 실패 Trace 확인
  → 전체 Regression 재실행
```

## 화면에서 확인하는 것

- 전체 6개 Scenario의 통과·실패 수
- Safety Critical Scenario가 모두 통과했는지 나타내는 Safety Gate
- 기대 상태와 실제 상태
- 실제 실행된 Tool과 검사 결과
- 실패 지점을 찾기 위한 Trace

기본 평가는 모두 통과합니다. `학습용 회귀 오류 넣기`를 선택하면 정상 주문이 승인 대기를 건너뛰고 `place_order`를 실행한 결과를 만들어, Safety Gate가 실패하는 과정을 확인할 수 있습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_08_evaluation
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8008
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_08_evaluation
python -m streamlit run frontend\app.py
```

## 파일 구조

```text
backend/app/evaluation/   평가 규칙과 전체 실행
backend/app/routers/      평가 HTTP API
backend/app/schemas/      요청 Schema
data/scenarios.json       기대 행동 6개
data/results.json         저장된 07 Agent 실행 결과
frontend/app.py           한 화면 평가 Dashboard
```

`data/results.json`은 새로운 Mock Agent가 아니라 결정적인 회귀 평가를 위한 저장 Fixture입니다. 실제 07 API를 연결할 때는 응답을 같은 `status`, `termination_reason`, `trace` 형식으로 바꾼 뒤 동일한 평가 함수에 전달하면 됩니다. HTTP `409` 거절은 평가에서 `blocked` 상태로 정규화합니다.

OpenAI, PostgreSQL, Redis, LangGraph와 MCP Server는 이 단계의 필수 실행에 포함하지 않습니다. 08의 핵심은 기술을 더 붙이는 것이 아니라 **Scenario → Check → Trace → Regression**을 이해하는 것입니다.

## 선택 · 실행 중인 07 Agent 평가

Mini Agent 07의 OpenAI Agent, HTTP MCP Server와 Backend를 먼저 실행하면 화면 아래의 선택 영역에서 실제 주문 요청 한 건을 가져와 동일한 평가 규칙으로 검사할 수 있습니다. 기본 Fixture 평가는 외부 서비스 없이 그대로 사용할 수 있습니다.

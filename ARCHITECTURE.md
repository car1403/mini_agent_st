# Mini Agent Backend Architecture

Mini Agent 03~08 Backend는 다음 의존 방향을 공통 규칙으로 사용합니다.

```text
routers → services / agents → tools → external APIs
                    ↓
                providers → LLM APIs
```

## 책임

- `routers`: HTTP 입출력과 HTTP 오류 변환만 담당합니다.
- `services`: 일반 생성, 구조화 출력, 미디어처럼 Agent Loop가 아닌 Use Case를 담당합니다.
- `agents`: Tool 선택, argument 보완, 반복, 종료 판단과 최종 답변 조립을 담당합니다.
- `providers`: OpenAI, Gemini, Ollama, Mock의 호출·응답 차이를 공통 계약으로 변환합니다.
- `tools`: 날씨, 검색, 저장처럼 실제 기능을 수행하며 Agent나 Router를 import하지 않습니다.
- `schemas`: 계층 사이의 Pydantic 계약을 정의합니다.

## 금지하는 의존

```text
tools → agents
tools → routers
providers → 구체적인 Tool Registry
services → routers
```

Agent가 사용할 Tool 목록을 선택해 Provider에 전달합니다. Provider는 Tool을 실행하거나
Agent Loop를 소유하지 않습니다. 실제 실행은 Allowlist 기반 `tools/executor.py`만 담당합니다.

## Provider 경계

Provider는 외부 LLM을 위한 Adapter입니다. 상위 계층은 Provider를 통해 모델 SDK와 응답
형식의 차이를 알지 않고 일반 생성, 구조화 출력, Tool Call 요청을 수행합니다.

Provider가 수행합니다.

- 공통 메시지와 Tool Definition을 모델별 요청 형식으로 변환
- 외부 모델 API 한 번 호출
- 텍스트, 구조화 결과와 Tool Call을 공통 결과 모델로 변환
- 모델명, Provider명과 호출 시간 같은 통신 Metadata 반환

Provider가 수행하지 않습니다.

- Agent가 사용할 Tool 집합 결정
- Tool arguments의 업무 규칙 보완 또는 임의 추측
- Tool Allowlist 검증과 실제 함수 실행
- 반복 횟수, 승인, 재시도, 종료 같은 Agent Loop 정책

```text
Agent / Service
      ↓ 공통 요청
Provider Adapter
      ↓ 모델별 요청
OpenAI / Gemini / Ollama / Mock
      ↓ 모델별 응답
Provider Adapter
      ↓ 공통 결과
Agent / Service
```

## 단계별 적용

1. Mini Agent 03에서 Tool과 Agent 경계를 기준 구현으로 확정합니다.
2. Mini Agent 04는 RAG 검색을 읽기 전용 Tool로 제공합니다.
3. Mini Agent 05는 Memory 읽기·쓰기 Tool을 사용자 격리 규칙과 함께 제공합니다.
4. Mini Agent 06은 LangGraph Node가 Agent와 Tool을 조합하되 Tool 구현을 포함하지 않습니다.
5. Mini Agent 07은 위험 Tool 실행 전에 Approval Agent를 통과시킵니다.
6. Mini Agent 08은 Agent·Provider·Tool Trace와 평가를 공통 계약으로 기록합니다.

각 단계는 기존 API URL과 Response Schema를 유지한 상태에서 이동하고, 호환 import는 모든
호출부가 새 경로로 전환된 뒤 제거합니다.

# Mini Agent 06 · LangGraph AI Agent

`06_agent-workflow`에서 배운 OpenAI AI Agent Loop를 FastAPI, LangGraph와 Streamlit으로 확인하는 단일 화면 프로젝트입니다.

이 프로젝트는 LangGraph 기능 전체를 배우거나 이전 RAG·Memory·MCP 프로젝트를 다시 구현하지 않습니다. 다음 질문 하나에 집중합니다.

> OpenAI Model이 Tool Result를 보고 다음 행동을 선택하는 Agent Loop를 LangGraph가 어떻게 State와 Edge로 관리하는가?

## AI Agent, Workflow와 LangGraph의 책임

세 영역은 할 수 있는 기능으로 완전히 분리되지 않습니다. AI Agent는 작업 순서를 계획할 수 있고 Python `while` Loop로 자신의 실행을 반복할 수도 있습니다. 반대로 LangGraph Node 안에도 결정적인 Workflow를 넣을 수 있습니다.

중요한 것은 **누가 할 수 있는가가 아니라 누구에게 책임을 맡길 것인가**입니다.

| 영역 | 책임 | 맡기지 않는 책임 |
| --- | --- | --- |
| AI Agent | Goal과 Tool Result를 보고 다음 Tool 또는 최종 답변 선택 | Tool 권한을 스스로 확정하거나 검증을 우회하지 않음 |
| Workflow·Backend | Allowlist, arguments 검증, Tool 실행, 오류와 종료 기록 | 자연어 목표의 유연한 해결 순서를 모두 하드코딩하지 않음 |
| LangGraph | State, Node 실행, Edge 분기, 반복과 END 연결 | Model 대신 다음 Tool을 판단하지 않음 |

```text
AI Agent    = 무엇을 할지 판단
Workflow    = 어떤 규칙으로 안전하게 실행할지 통제
LangGraph   = 판단과 실행 단계를 State Graph로 연결
```

### AI Agent가 Workflow의 일을 할 수 있는가?

Model은 계획을 만들고 실행 순서를 제안할 수 있습니다. 하지만 입력 검증, Tool Allowlist, 권한과 반복 한도처럼 반드시 지켜야 하는 규칙까지 Model 판단에만 맡기면 결과가 비결정적이고 우회될 수 있습니다. 따라서 유연한 판단은 Agent에, 강제해야 하는 규칙은 Backend Workflow에 둡니다.

### AI Agent가 LangGraph의 일을 할 수 있는가?

LangGraph 없이도 AI Agent는 동작합니다. 순수 Python의 `while` 또는 `for`로 State, Tool Result 전달과 종료를 구현할 수 있습니다. 이때 그 일을 하는 주체는 정확히 말하면 AI Model 자체가 아니라 **Agent Runtime 코드**입니다.

LangGraph는 필수가 아닙니다. 반복·분기·State가 복잡해질 때 실행 구조를 Node와 Edge로 명시하기 위해 사용합니다.

```text
같은 AI Agent
├─ Python Loop로 실행 가능
└─ LangGraph로 실행 가능 ← 이 프로젝트
```

## 실행 흐름

```text
사용자 질문
  ↓
START
  ↓
AI Agent Node: OpenAI가 다음 행동 판단
  ↓
Tool Call이 있는가?
  ├─ Yes → Workflow Tool Node: 검증·실행·Result 기록
  │              ↓
  │         AI Agent Node로 복귀
  └─ No  → 최종 답변 → END
```

Trace의 `owner`는 각 단계의 주 책임을 보여줍니다.

- `ai_agent`: Model의 Tool 선택 또는 최종 답변
- `workflow`: Tool 검증·실행 또는 오류 처리
- `langgraph`: Graph 시작과 실행 중단

## 프로젝트 구조

```text
backend/app/
├─ agents/travel_agent.py      # AI Agent 판단 Node
├─ graphs/state.py             # 공유 State
├─ graphs/travel_graph.py      # Node, Edge, 반복과 종료
├─ tools/                      # Tool과 Allowlist
├─ providers/openai.py         # OpenAI Responses API
├─ services/agent_service.py   # Use Case 진입점
├─ routers/agent_router.py     # HTTP API
└─ main.py

frontend/app.py                # 질문·답변·Trace 단일 화면
```

`starter`, `solution`, 별도 Python Backend, RAG, Memory, Database, Multi-Agent와 Human Approval은 포함하지 않습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_06_langgraph
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`에 실제 `OPENAI_API_KEY`를 설정합니다.

Backend:

```powershell
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

Frontend:

```powershell
streamlit run frontend\app.py --server.port 8501
```

브라우저에서 `http://127.0.0.1:8501`을 열고 실행합니다. API 문서는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

## 학습 범위

포함:

- OpenAI 기반 Tool-using AI Agent
- Tool Result 이후 Model 재판단
- State, Agent Node, Tool Node와 Conditional Edge
- 반복, END와 최대 단계 제한
- Allowlist와 arguments 검증
- Trace, LLM·Tool 호출 횟수와 종료 이유

제외:

- MCP, RAG와 장기 Memory 재구현
- Checkpoint와 승인 후 재개
- Multi-Agent, Supervisor와 Handoff
- PostgreSQL, Redis와 사용자 인증
- 여러 Model Provider 비교

다음 과정에서는 이 구조에 Human Approval과 Safety를 연결하고, 이후 Multi-Agent Orchestration에서 독립적인 Agent의 역할과 권한을 나눕니다.

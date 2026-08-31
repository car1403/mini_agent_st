# Mini Agent 06 · Agent Workflow

OpenAI AI Agent가 Tool을 선택하고, LangGraph가 반복을 관리하며, Backend가 실제 Streamable HTTP MCP Server를 통해 Tool을 실행하는 단일 화면 프로젝트입니다.

이 프로젝트는 `06_agent-workflow`에서 학습한 내용을 중심으로 앞에서 배운 HTTP MCP 연결을 재사용합니다.

## 핵심 구조

```text
사용자 질문
  ↓
Streamlit
  ↓ HTTP
FastAPI Backend :8000
  ↓
LangGraph AI Agent Loop
  ├─ OpenAI AI Agent Node
  └─ HTTP MCP Tool Node
          ↓ Streamable HTTP
Travel MCP Server :8010/mcp
  ├─ get_weather
  ├─ search_indoor_places
  └─ search_outdoor_places
```

Backend는 MCP Server의 Tool 함수를 직접 import하지 않습니다. MCP의 `tools/list`로 Tool Schema를 발견하고 `tools/call`로 실행합니다.

## 책임을 나누는 이유

세 영역은 할 수 있는 기능으로 완전히 분리되지 않습니다. 중요한 것은 **누가 할 수 있는가가 아니라 누구에게 책임을 맡길 것인가**입니다.

| 영역 | 책임 | 맡기지 않는 책임 |
| --- | --- | --- |
| AI Agent | Goal과 Tool Result를 보고 다음 Tool 또는 최종 답변 선택 | Tool 권한과 입력 검증을 스스로 확정하지 않음 |
| Workflow·Backend | Model 제안 검증, MCP 호출, 오류와 종료 기록 | 유연한 해결 순서를 모두 하드코딩하지 않음 |
| LangGraph | State, Node 실행, Edge 분기, 반복과 END 연결 | Model 대신 다음 Tool을 선택하지 않음 |
| MCP Server | Backend 밖에서 Tool Schema와 실제 실행 제공 | Agent의 전체 목표와 Graph 흐름을 결정하지 않음 |

### AI Agent가 Workflow의 일을 할 수 있는가?

AI Agent는 계획과 실행 순서를 제안할 수 있습니다. 그러나 Allowlist, arguments, 권한과 반복 한도처럼 반드시 지켜야 하는 규칙을 Model 판단에만 맡기면 안 됩니다. 유연한 판단은 Agent에 두고, 강제할 규칙은 Backend Workflow에 둡니다.

### AI Agent가 LangGraph의 일을 할 수 있는가?

LangGraph 없이도 AI Agent는 동작합니다. 순수 Python의 `while` 또는 `for`로 State, Tool Result 전달과 종료를 구현할 수 있습니다. 이 실행을 관리하는 것은 정확히 말하면 AI Model 자체가 아니라 Agent Runtime 코드입니다.

```text
같은 OpenAI AI Agent
├─ 순수 Python Loop로 실행 가능
└─ LangGraph로 실행 가능 ← 이 프로젝트
```

LangGraph는 복잡한 반복과 분기를 State·Node·Edge로 명시하는 구현 프레임워크입니다.

## Agent 실행 흐름

```text
1. Backend가 MCP Server의 tools/list 호출
2. 발견한 Tool Schema를 OpenAI에 전달
3. AI Agent가 get_weather 선택
4. LangGraph가 HTTP MCP Tool Node로 이동
5. Backend가 tools/call로 get_weather 실행
6. MCP Result를 OpenAI에 전달
7. AI Agent가 search_indoor_places 선택
8. MCP Tool을 다시 실행하고 Result 전달
9. AI Agent가 최종 답변 생성
10. LangGraph가 END로 종료
```

Trace의 `owner`는 각 단계의 주 책임을 보여줍니다.

- `ai_agent`: Model의 MCP Tool 선택 또는 최종 답변
- `workflow`: Tool Call 검증과 오류 처리
- `langgraph`: Graph 시작, 반복 제한과 종료
- `mcp`: Tool 발견과 실제 HTTP MCP 호출

## 프로젝트 구조

```text
backend/app/
├─ agents/travel_agent.py       # AI Agent 판단 Node
├─ graphs/state.py              # 공유 State
├─ graphs/travel_graph.py       # Node, Edge, Loop와 END
├─ mcp/client.py                # tools/list와 tools/call
├─ providers/openai.py          # OpenAI Responses API
├─ services/agent_service.py
├─ routers/agent_router.py
└─ main.py

mcp_server/travel_server.py     # 독립 HTTP MCP Server
frontend/app.py                 # 질문·답변·연결 상태·Trace 한 화면
```

## 실행 준비

```powershell
cd C:\mini_agent_st\mini_agent_06_langgraph
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`에 실제 `OPENAI_API_KEY`를 설정합니다.

## 실행 순서

터미널 1 · HTTP MCP Server:

```powershell
python .\mcp_server\travel_server.py
```

터미널 2 · FastAPI Backend:

```powershell
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

MCP 연결 확인:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/agent/mcp-status
```

터미널 3 · Frontend:

```powershell
streamlit run frontend\app.py --server.port 8501
```

브라우저에서 `http://127.0.0.1:8501`을 엽니다. 사용자는 MCP를 선택하지 않고 질문만 입력합니다. AI Agent가 발견된 MCP Tool 중 다음 행동을 선택합니다.

## 학습 범위

포함:

- 실제 OpenAI 기반 Tool-using AI Agent
- 실제 Streamable HTTP MCP 통신
- MCP Tool 자동 발견과 호출
- Tool Result 이후 Model 재판단
- LangGraph State, Node, Conditional Edge, Loop와 END
- Trace, LLM·MCP Tool 호출 횟수와 종료 이유

제외:

- stdio MCP, Resource와 Prompt
- RAG와 장기 Memory
- Checkpoint와 Human Approval
- Multi-Agent, Supervisor와 Handoff
- Database, 사용자 인증과 여러 Model Provider

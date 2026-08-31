# Mini Agent 07 · Human Approval and Safety

`mini_agent_06_agent_workflow`의 세 독립 Single Agent에 **변경 Tool 실행 전 사용자 승인과 Backend 안전 정책**을 추가합니다.

```text
06: Agent 선택 → 읽기 MCP Tool → Result → 최종 답변
07: Agent 선택 → 읽기 MCP Tool → 변경 Tool 제안 → 승인 대기 → 승인·거절 → 실행
```

## 핵심 원칙

OpenAI Model은 Tool을 제안할 뿐 실행 권한을 갖지 않습니다.

```text
Model Tool Call
  ↓
Backend Policy
  ├─ read      → 자동 실행
  ├─ change    → waiting_approval
  └─ forbidden → blocked
```

승인 후에도 소유자, Agent Tool Allowlist, 위험도, 승인 대상 Snapshot과 중복 실행 여부를 다시 검사합니다.

## 세 Agent의 변경 경계

| Agent | 자동 실행 | 승인 후 실행 |
| --- | --- | --- |
| Travel Agent | 날씨·실내·야외 장소 조회 | `save_itinerary` |
| Customer Support Agent | 주문 상태·반품 정책 조회 | `create_return_request` |
| Order Assistant Agent | 상품·재고·예상 금액 조회 | `place_order` |

Agent끼리는 연결되지 않습니다. 사용자가 실행할 Agent를 직접 선택하므로 아직 Multi-Agent Orchestration이 아닙니다.

## 전체 실행 흐름

```text
사용자와 Agent 선택
  ↓
OpenAI Single Agent
  ↓ 읽기 Tool 제안
Backend Allowlist·arguments·risk 검사
  ↓
HTTP MCP 읽기 Tool 자동 실행
  ↓
OpenAI 재판단
  ↓ 변경 Tool 제안
Backend가 실행하지 않고 State와 승인 Snapshot 저장
  ↓
waiting_approval 응답
  ↓
사용자 승인 또는 거절
  ↓
actor·상태·Snapshot·Allowlist·risk·중복 실행 재검사
  ↓ approve
HTTP MCP 변경 Tool 한 번 실행
  ↓
OpenAI 최종 답변 + Audit Log
```

## 승인 Snapshot

사용자는 모호한 “허용” 버튼이 아니라 구체적인 실행 대상을 승인합니다.

```json
{
  "agent_id": "order",
  "tool": "place_order",
  "arguments": {
    "product_id": "P-KEYBOARD",
    "quantity": 2
  }
}
```

승인 API가 받은 Snapshot과 저장된 Snapshot이 다르면 실행을 차단합니다. 승인자는 최초 실행의 `actor_id`와 같아야 합니다.

> 예제의 `actor_id` 입력은 학습용입니다. 운영 환경에서는 로그인 Session이나 검증된 Token에서 사용자 ID를 가져와야 합니다.

## 프로젝트 구조

```text
backend/app/
├─ agents/
│  ├─ runtime.py             # OpenAI Loop, pause와 resume
│  ├─ travel_agent.py
│  ├─ support_agent.py
│  └─ order_agent.py
├─ approval/
│  ├─ policies.py            # read·change·forbidden
│  └─ store.py               # 학습용 Run State·멱등성·Audit
├─ mcp/client.py             # 실제 HTTP MCP Tool 발견·호출
├─ routers/agent_router.py   # 시작·조회·승인·거절 API
├─ schemas/agent.py
└─ main.py

mcp_server/business_tools_server.py
frontend/app.py
10_optional_langgraph/approval_interrupt.py
```

`approval/store.py`는 개념을 쉽게 보기 위한 Process Memory 저장소입니다. 운영 환경에서는 사용자 격리와 원자적 상태 전이를 보장하는 Database로 교체해야 합니다.

## API

| Method | Endpoint | 역할 |
| --- | --- | --- |
| GET | `/api/agents` | 독립 Single Agent 목록 |
| GET | `/api/agents/mcp-status` | HTTP MCP 연결과 Tool 확인 |
| POST | `/api/agents/runs` | Agent 실행 또는 승인 대기까지 진행 |
| GET | `/api/agents/runs/{run_id}` | 저장된 실행 State 조회 |
| POST | `/api/agents/runs/{run_id}/decision` | 승인·거절 후 재개 |
| GET | `/api/agents/runs/{run_id}/audit` | 승인과 변경 실행 Audit 조회 |

## 실행 준비

```powershell
cd C:\mini_agent_st\mini_agent_07_human_approval
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`의 `OPENAI_API_KEY`를 설정합니다.

## 실행 순서

터미널 1 · HTTP MCP Server:

```powershell
python .\mcp_server\business_tools_server.py
```

터미널 2 · FastAPI Backend:

```powershell
uvicorn app.main:app --reload --port 8000 --app-dir backend
```

터미널 3 · 단일 화면 Frontend:

```powershell
streamlit run frontend\app.py --server.port 8501
```

## 선택 LangGraph 비교

메인은 일반 Python State Store와 API로 중단·재개합니다. 다음 예제는 같은 개념을 LangGraph `interrupt()`와 `Command(resume=...)`로 비교합니다.

```powershell
python .\10_optional_langgraph\approval_interrupt.py
```

LangGraph는 실행 중단과 재개를 표현하지만 인증·인가·승인 대상·Tool 정책과 멱등성을 대신 보장하지 않습니다.

## 다음 Multi-Agent 과정과 연결

다음 과정에서 Coordinator가 Agent를 선택하고 Handoff를 수행하더라도 안전 정책은 사라지지 않습니다.

```text
Coordinator 요청
→ Worker Agent 판단
→ Backend Policy
→ 필요한 경우 사용자 승인
→ Tool 실행
```

다른 Agent와 Coordinator의 메시지도 권한을 부여하는 신뢰 정보로 취급하지 않습니다.

## 포함하지 않는 범위

- 실제 결제·예약·외부 메시지 전송
- 운영용 인증 Provider와 Database
- 여러 승인자의 공동 승인
- Multi-Agent Coordinator와 Handoff
- 운영용 LangGraph Checkpointer

# Mini Agent 05 · Memory

Mini Agent 04의 RAG 화면을 유지하면서 대화 Window, Redis 단기 상태, PostgreSQL 장기 사용자 Memory와 Hybrid 복원을 추가한 누적형 완성본입니다.

## Backend 공통 구조

Mini Agent 03의 `core`, `providers`, `routers`, `schemas`, `services`, `agents`, `tools` 구조를 유지하고 `rag/`, `memory/`를 과정 전용 계층으로 추가합니다. Swagger는 Stage 01~05로 구분하며 Schema도 `common`, Stage 01~03, `rag`, `memory`로 분리합니다.

```text
질문
→ 사용자별 Memory 조회
→ 질문과 관련된 Memory만 선택
→ Prompt에 추가
→ 개인화 답변
→ 사용한 Memory 표시
```

## 새로 추가된 메뉴

1. Memory 종류
2. 대화 Window
3. 사용자 Memory CRUD
4. Memory 기반 개인화 답변
5. Redis·PostgreSQL
6. Hybrid Memory 복원·Trace

처음 네 메뉴는 `mock` 저장소와 `mock` Provider로 Docker 없이 실행할 수 있습니다. 저장소 및 Hybrid 복원 메뉴에서는 Redis와 PostgreSQL을 연결합니다.

## 실행 1: Mock Memory

```powershell
cd C:\mini_agent_st\mini_agent_05_memory
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_05_memory
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

## 실행 2: Redis와 PostgreSQL

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
```

기존 PostgreSQL Volume을 유지하고 있다면 [공용 인프라 안내](../infra/README.md)에 따라 수정된 `init.sql`을 적용합니다.

## Memory 안전 원칙

- 허용한 key만 저장합니다.
- 비밀번호·카드번호·여권번호·API Key는 저장하지 않습니다.
- 조회·수정·삭제에 항상 `user_id`를 포함합니다.
- 질문에 관련된 Memory만 LLM에 전달합니다.
- 사용자가 자신의 Memory를 확인하고 삭제할 수 있게 합니다.

> 화면의 `user_id`는 수업용 시뮬레이션입니다. 운영 환경에서는 Backend가 인증 토큰에서 사용자 ID를 가져와야 하며, 클라이언트가 전달한 ID를 소유권 근거로 신뢰하면 안 됩니다.

## 학생용과 완성본

- `starter`: 핵심 함수를 학생이 작성합니다.
- `learning_unit`: 6개 단위 예제를 순서대로 실행합니다.
- `backend`, `frontend`: 시간이 부족할 때 바로 시연합니다.
- `solution`: 정답 코드 위치를 안내합니다.
Redis Session은 사용자별 Key·TTL·version으로 관리하며 PostgreSQL은 장기 선호와 대화 이력을 보관합니다. `Hybrid Memory 복원` 화면에서 두 저장소 결과와 Trace를 함께 확인할 수 있습니다.

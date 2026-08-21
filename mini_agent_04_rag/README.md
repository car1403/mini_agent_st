# Mini Agent 04 · RAG

Mini Agent 03의 메뉴와 구조를 그대로 유지하면서 문서 검색과 근거 기반 답변을 추가한 누적형 완성본입니다.

## Backend 공통 구조

`core`, `providers`, `routers`, `schemas`, `services`, `agents`, `tools`는 Mini Agent 03과 같은 책임을 유지합니다. 04에서는 `rag/`만 과정 전용 계층으로 추가됩니다. Router와 Schema는 Stage 01~03 및 `rag`로 분리되고, Tool은 `registry.py`와 `executor.py`의 단일 등록·실행 경로를 사용합니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers
  → rag/service.py
  → keyword 또는 Ollama + pgvector
  → Redis TTL 답변 Cache
```

## 새로 추가된 메뉴

1. RAG 흐름
2. 문서와 Chunk
3. 문서 검색
4. 근거 기반 답변
5. Ollama + pgvector + Redis
6. 직접 입력 문장과 PDF 색인
7. Metadata Filter와 Hybrid Search
8. RAG Agent 검색 Tool

`keyword + mock`은 Docker와 API Key 없이 실행됩니다. 실제 구성에서는 pgvector가 Chunk와 Embedding을 영구 저장하고 Redis가 동일 조건의 답변을 TTL 동안 Cache합니다.

## 실행 1: Mock RAG

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

## 실행 2: 실제 pgvector RAG

```powershell
cd C:\mini_agent_st\infra
Copy-Item .env.example .env
docker compose up -d
docker exec mini-agent-ollama ollama pull embeddinggemma
```

Streamlit의 `pgvector 실습` 메뉴에서 연결 상태를 확인하고 `교육용 문서 색인`을 누릅니다.

`근거 기반 답변`에서 Redis Cache를 켜고 같은 질문을 두 번 실행하면 MISS→HIT와 남은 TTL, 전체 Trace를 확인할 수 있습니다. 문서를 재색인하면 Mini Agent RAG 전용 Cache가 무효화됩니다.

`텍스트·PDF 색인`에서는 직접 작성한 정책과 텍스트형 PDF를 등록합니다. PDF 검색 결과는
페이지 번호를 Metadata로 유지하며 스캔 PDF는 별도 OCR이 필요합니다. `Metadata·Hybrid`
메뉴는 활성 문서 Filter, 요청별 유사도 임계값, 키워드와 pgvector 순위를 결합한 RRF를
비교합니다. `RAG Agent Tool`은 DB나 임의 SQL 대신 제한된 `search_knowledge_base`
계약만 사용합니다.

> 기존 PostgreSQL Volume에는 새 `documents` 테이블이 자동 생성되지 않을 수 있습니다. 이 경우 [공용 인프라 안내](../infra/README.md)의 기존 Volume 주의를 확인합니다.

## 안전 범위

- 기존 여행 Tool은 조회용 Mock이며, RAG Agent에는 읽기 전용 지식검색 Tool만 제공합니다.
- Agent에 DB 연결 정보나 임의 SQL 실행 권한을 제공하지 않습니다.
- RAG 색인 초기화는 `mini_agent_travel` collection만 대상으로 합니다.
- 전체 DB나 다른 단계의 문서는 삭제하지 않습니다.
- 근거 문서가 없으면 Mock RAG는 답변하지 않습니다.

## 학생용과 완성본

- `starter`: 핵심 함수를 학생이 작성합니다.
- `learning_unit`: 작은 단위 예제를 순서대로 실행합니다.
- `backend`, `frontend`: 시간이 부족할 때 바로 시연하는 완성본입니다.
- `solution`: 정답 코드 위치와 해설 순서를 안내합니다.

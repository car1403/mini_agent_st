# Solution 안내

| 학습 항목 | 완성 코드 |
| --- | --- |
| 대화 Window | `backend/app/memory/conversation.py` |
| 저장 정책 | `backend/app/memory/policy.py` |
| Mock 사용자 Memory | `backend/app/memory/mock_store.py` |
| 관련 Memory 선택 | `backend/app/memory/relevance.py` |
| Redis 단기 상태 | `backend/app/memory/redis_store.py` |
| PostgreSQL 장기 Memory | `backend/app/memory/postgres_store.py` |
| PostgreSQL 대화 이력 | `backend/app/memory/conversation_store.py` |
| 관련 Memory와 개인화 | `backend/app/memory/service.py` |
| FastAPI | `backend/app/routers/memory_router.py` |
| Streamlit | `frontend/app_pages/19~25` |

Demo Track에서는 Mock 격리와 민감 key 차단 후 Redis version 충돌, PostgreSQL 최근 대화, Hybrid 복원 Trace, 실제 LLM 개인화를 순서대로 보여줍니다.

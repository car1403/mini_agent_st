# 선택 비교 · LangGraph interrupt와 resume

메인 프로젝트는 일반 Python State Store로 `waiting_approval`을 저장하고 승인 API에서 재개합니다. 이 예제는 같은 중단·재개 개념을 LangGraph의 `interrupt()`와 `Command(resume=...)`로 표현합니다.

```text
메인: State 저장 → API 응답 → 승인 API → Python Runtime 재개
선택: interrupt → Checkpointer → Command(resume) → Graph 재개
```

LangGraph는 승인자, 소유권, 승인 대상, Tool Allowlist와 멱등성을 대신 검증하지 않습니다.

```powershell
python .\10_optional_langgraph\approval_interrupt.py
```

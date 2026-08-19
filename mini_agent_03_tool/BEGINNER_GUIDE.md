# Mini Agent 03 초보자 진행 순서

## 단위 예제

1. `learning_unit/00_tool_use_concepts.py`
2. `learning_unit/01_tool_schema_validation.py`
3. `learning_unit/02_mock_tool_selection.py`
4. Backend 실행 후 `03_tool_description_before_after.py`부터 `06_missing_arguments_and_clarification.py`
5. `learning_unit/07_safe_tool_execution.py`
6. `learning_unit/08_tool_result_to_answer.py`
7. Backend 실행 후 `learning_unit/09_real_tool_loop.py`
8. Provider 비교는 `learning_unit/10_labs/01_multi_provider_tool_calling.py`

```text
함수 → Schema → Tool Call → Allowlist → Pydantic 검증
     → Tool Result → 최종 답변
```

## Streamlit 확인

1. `Tool 선택`에서 Schema와 선택 결과를 확인합니다.
2. `Tool 실행`에서 정상·날짜 오류·미등록 Tool을 실행합니다.
3. `Agent Loop`에서 Tool Result가 최종 답변에 사용되는지 확인합니다.
4. 마지막에만 Gemini·GPT·Ollama/Llama를 선택합니다.

## 완료 체크

- [ ] Tool Call은 실행 명령이 아니라 제안임을 설명할 수 있습니다.
- [ ] 선택 API만 호출했을 때 함수가 실행되지 않습니다.
- [ ] 잘못된 arguments가 Pydantic에서 차단됩니다.
- [ ] Allowlist에 없는 Tool이 차단됩니다.
- [ ] 최종 답변이 Tool Result 값을 사용합니다.
- [ ] 상태 변경 Tool에 승인이 필요한 이유를 설명할 수 있습니다.

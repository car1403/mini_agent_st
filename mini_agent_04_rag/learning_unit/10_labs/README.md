# 04 RAG 실습

## 실행 위치

실습 1~3은 Backend와 Docker 없이 실행합니다. 실습 4의
`06_pgvector_ollama_example.py`는 Mini Backend를 호출하지 않고 PostgreSQL·pgvector와
Ollama에 직접 연결합니다.

```powershell
cd C:\mini_agent_st\infra
docker compose up -d postgres ollama
docker compose exec ollama ollama pull embeddinggemma
```

완성 RAG 화면을 확인할 때만 별도 터미널에서 다음 Backend를 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_04_rag\backend
uvicorn app.main:app --reload --port 8000
```

## 실습 1. Chunk 크기 비교

`02_chunking_and_metadata.py`의 `sentences_per_chunk`를 1, 2, 4로 바꾸고 Chunk 개수와 내용을 비교합니다.

## 실습 2. 검색 결과 설명하기

`03_keyword_retrieval.py`에서 `top_k`를 1과 3으로 실행하고, 검색 결과가 늘어날 때 Context에 불필요한 내용이 섞일 수 있는 이유를 적습니다.

## 실습 3. 근거 없음 처리

등록되지 않은 여권 분실 질문을 입력하고 다음을 확인합니다.

- `grounded`가 `False`인가?
- `sources`가 비어 있는가?
- 문서에 없는 내용을 추측하지 않는가?

## 실습 4. 실제 pgvector 검색

Docker 환경을 실행한 후 `06_pgvector_ollama_example.py`의 질문을 세 가지로 바꿉니다.

- 호텔 예약을 취소하고 싶어요.
- 비행기에 가방을 몇 kg까지 실을 수 있나요?
- 박물관이 쉬는 날은 언제인가요?

각 질문에서 1위 문서와 점수를 기록합니다.

## 실습 5. 키워드와 pgvector 비교

`07_keyword_vs_pgvector.py`에서 두 검색 방식의 1위 문서와 점수를 기록하고 의미가
비슷하지만 단어가 다른 질문에서 결과가 달라지는 이유를 설명합니다.

## 실습 6. 실제 LLM 근거 답변

`08_real_rag_answer.py`를 준비된 Provider로 실행하고 답변이 출력된 Context와 출처로
뒷받침되는지 확인합니다.

## 실습 7. Redis Cache

`09_redis_rag_cache.py`로 MISS→HIT와 TTL을 확인합니다. `top_k`나 Provider를 바꾸면
새 Cache Key가 사용되는지 확인하고 재색인 후 다시 MISS가 되는지 관찰합니다.

## 실습 8. 직접 입력 문장 검색

`11_text_insert_and_search.py`에 의미는 비슷하지만 단어가 다른 문장과 질문을 각각
추가합니다. `top_k`와 `score_threshold`를 바꾸며 관련 없는 결과가 제거되는지 확인합니다.

## 실습 9. PDF 페이지 출처 검색

텍스트형 PDF를 준비하고 `12_pdf_index_and_search.py`로 색인합니다. 서로 다른 페이지의
내용을 묻는 질문 세 개를 실행하여 1위 Chunk의 파일명, 페이지 번호, 점수를 기록합니다.
같은 PDF를 다시 색인했을 때 Chunk 수가 중복 증가하지 않는지도 확인합니다.

> 이미지로 스캔된 PDF는 이 기본 실습의 대상이 아닙니다. 텍스트가 추출되지 않을 때
> OCR이 필요한 이유를 설명하는 것은 심화 실습으로 다룹니다.

## 실습 10. Agent와 pgvector Tool

`13_agent_pgvector_tool.py`를 먼저 기본 `mock` 모드로 실행하여 Tool Call과 Tool Result를
확인합니다. 이후 `RAG_AGENT_PROVIDER=ollama`로 실행하여 실제 Agent가 검색 Tool을
선택하는지, 최종 답변이 Tool Result와 출처로 뒷받침되는지 비교합니다.

## 실습 11. Metadata Filter와 임계값

`14_metadata_and_threshold.py`에서 `category`, `status`, `language` 조건을 하나씩 제거해
만료되었거나 다른 범주의 문서가 검색되는지 관찰합니다. `score_threshold`를 여러 값으로
바꾸고 관련 문서까지 사라지는 지점을 기록하여 임계값의 정밀도·재현율 trade-off를
설명합니다.

## 실습 12. Hybrid Search와 RRF

`15_hybrid_search.py`의 질문에서 정확한 객실 코드가 있는 경우와 없는 경우를 비교합니다.
키워드, pgvector, Hybrid 각각의 상위 문서를 기록하고 `rank_constant`를 바꿨을 때 RRF
순위가 어떻게 변하는지 확인합니다.

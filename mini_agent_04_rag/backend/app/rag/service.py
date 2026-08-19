from time import perf_counter

from app.config import settings
from app.providers import generate
from app.rag.documents import TRAVEL_DOCUMENTS
from app.rag.embedding import embed
from app.rag.keyword_store import all_chunks, keyword_search
from app.rag.pgvector_store import add_chunk, reset_collection, vector_search
from app.rag import redis_cache
from app.schemas import RagAnswerResult, RagIndexResult, RagSearchItem


def search(query: str, mode: str, top_k: int) -> list[RagSearchItem]:
    if mode == "keyword":
        return keyword_search(query, top_k)
    return vector_search(embed(query), top_k)


def index_documents(reset: bool = True) -> RagIndexResult:
    if reset:
        reset_collection()
    chunks = all_chunks()
    for chunk in chunks:
        add_chunk(chunk, embed(chunk.text))
    # 문서 변경 후에는 이전 Context로 만든 답변 Cache를 재사용하지 않습니다.
    try:
        redis_cache.invalidate_all()
    except Exception:
        # Redis가 없어도 영구 Vector 색인 자체는 완료할 수 있습니다.
        pass
    return RagIndexResult(
        collection=settings.rag_collection,
        indexed_count=len(chunks),
        embedding_model=settings.ollama_embedding_model,
    )


def answer(query: str, mode: str, top_k: int, provider: str, use_cache: bool = True) -> RagAnswerResult:
    cache_key = redis_cache.make_key(query, mode, top_k, provider)
    if use_cache:
        try:
            cached, ttl = redis_cache.get(cache_key)
            if cached:
                cached["cache_hit"] = True
                cached["cache_ttl_seconds"] = max(ttl, 0)
                cached["trace"] = [{"stage": "cache", "data": {"hit": True, "ttl": ttl}}]
                return RagAnswerResult.model_validate(cached)
        except Exception:
            # Cache 장애가 검색과 답변 생성까지 막아서는 안 됩니다.
            pass

    started = perf_counter()
    results = search(query, mode, top_k)
    retrieval_ms = round((perf_counter() - started) * 1000)
    trace = [
        {"stage": "cache", "data": {"hit": False, "enabled": use_cache}},
        {"stage": "retrieval", "data": {"mode": mode, "count": len(results), "latency_ms": retrieval_ms}},
    ]
    if not results:
        return RagAnswerResult(
            answer="제공된 여행 정책 문서에서 근거를 찾지 못했습니다.",
            grounded=False,
            provider=provider,
            search_mode=mode,
            trace=trace + [{"stage": "finish", "data": {"reason": "no_grounding"}}],
        )

    context = "\n".join(
        f"[{item.source}] {item.content}" for item in results
    )
    sources = sorted({item.source for item in results})
    if provider == "mock":
        answer_text = results[0].content
        generation_ms = 0
    else:
        prompt = f"질문: {query}\n\nContext:\n{context}"
        system_prompt = (
            "Context에 있는 내용만 사용해 한국어로 답하세요. "
            "Context에 근거가 없으면 모른다고 답하세요."
        )
        generation_started = perf_counter()
        answer_text = str(generate(provider, system_prompt, prompt).content)
        generation_ms = round((perf_counter() - generation_started) * 1000)

    result = RagAnswerResult(
        answer=answer_text,
        grounded=True,
        provider=provider,
        search_mode=mode,
        context=context,
        sources=sources,
        results=results,
        trace=trace + [
            {"stage": "context", "data": {"sources": sources, "characters": len(context)}},
            {"stage": "generation", "data": {"provider": provider, "latency_ms": generation_ms}},
        ],
    )
    if use_cache:
        try:
            result.cache_ttl_seconds = redis_cache.set(cache_key, result.model_dump(mode="json"))
            result.trace.append({"stage": "cache_write", "data": {"ttl": result.cache_ttl_seconds}})
        except Exception as error:
            result.trace.append({"stage": "cache_write", "data": {"error": str(error)}})
    return result

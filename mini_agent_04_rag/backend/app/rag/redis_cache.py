"""Redis에 RAG 답변을 짧게 보관하는 교육용 TTL Cache입니다."""

import hashlib
import json
from typing import Any

from redis import Redis

from app.config import settings


KEY_PREFIX = "mini-agent:rag-answer:"


def client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def make_key(query: str, mode: str, top_k: int, provider: str) -> str:
    # 검색 조건이나 모델이 달라지면 같은 질문도 별도 Cache 항목으로 취급합니다.
    payload = (
        f"{settings.rag_collection}|{settings.ollama_embedding_model}|"
        f"{settings.rag_min_score}|{query.strip()}|{mode}|{top_k}|{provider}"
    )
    return KEY_PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get(key: str) -> tuple[dict[str, Any] | None, int]:
    redis_client = client()
    value = redis_client.get(key)
    return (json.loads(value) if value else None, redis_client.ttl(key))


def set(key: str, value: dict[str, Any]) -> int:
    redis_client = client()
    redis_client.setex(key, settings.rag_cache_ttl_seconds, json.dumps(value, ensure_ascii=False))
    return settings.rag_cache_ttl_seconds


def invalidate_all() -> int:
    # KEYS 대신 SCAN을 사용해 Mini Agent RAG prefix만 점진적으로 찾습니다.
    redis_client = client()
    keys = list(redis_client.scan_iter(match=f"{KEY_PREFIX}*", count=100))
    return redis_client.delete(*keys) if keys else 0


def ping() -> bool:
    return bool(client().ping())

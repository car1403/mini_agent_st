from uuid import NAMESPACE_URL, uuid5

import psycopg
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb

from app.config import settings
from app.schemas import RagChunk, RagSearchItem


def connect():
    connection = psycopg.connect(settings.database_url)
    register_vector(connection)
    return connection


def reset_collection() -> None:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM documents WHERE collection_name = %s",
            (settings.rag_collection,),
        )


def add_chunk(chunk: RagChunk, vector: list[float]) -> None:
    # collection과 chunk_id로 결정적 UUID를 만들어 재색인해도 중복 행이 생기지 않습니다.
    document_id = uuid5(NAMESPACE_URL, f"{settings.rag_collection}:{chunk.chunk_id}")
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO documents
                (id, collection_name, title, content, source, chunk_index,
                 embedding_provider, embedding_model, embedding_dimension,
                 embedding, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, 'ollama', %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                source = EXCLUDED.source,
                chunk_index = EXCLUDED.chunk_index,
                embedding_provider = EXCLUDED.embedding_provider,
                embedding_model = EXCLUDED.embedding_model,
                embedding_dimension = EXCLUDED.embedding_dimension,
                embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata,
                created_at = NOW()
            """,
            (
                document_id, settings.rag_collection, chunk.title, chunk.text,
                chunk.source, chunk.chunk_index, settings.ollama_embedding_model,
                len(vector), vector, Jsonb({"chunk_id": chunk.chunk_id}),
            ),
        )


def vector_search(vector: list[float], top_k: int = 3) -> list[RagSearchItem]:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT title, content, source, chunk_index,
                   1 - (embedding <=> %s) AS score
            FROM documents
            WHERE collection_name = %s
              AND embedding_provider = 'ollama'
              AND embedding_model = %s
              AND embedding_dimension = %s
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                vector, settings.rag_collection, settings.ollama_embedding_model,
                len(vector), vector, top_k,
            ),
        )
        results = [
            RagSearchItem(
                title=row[0], content=row[1], source=row[2],
                chunk_index=row[3], score=round(float(row[4]), 3),
            )
            for row in cursor.fetchall()
        ]
        return [item for item in results if item.score >= settings.rag_min_score]

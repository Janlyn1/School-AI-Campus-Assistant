import os
import re
from typing import Any

from sqlalchemy import BigInteger, Column, Index, Integer, MetaData, String, Table, Text, select, text
from sqlalchemy.orm import Session

from ..database import database_backend
from ..models import KnowledgeDocument


EMBEDDING_DIMENSIONS = 768
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
VECTOR_METADATA = MetaData()
VECTOR_SCHEMA_READY = False

try:
    from pgvector.sqlalchemy import VECTOR

    KNOWLEDGE_CHUNKS = Table(
        "knowledge_chunks",
        VECTOR_METADATA,
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("document_id", Integer, nullable=False, index=True),
        Column("title", String(160), nullable=False),
        Column("source_type", String(40), nullable=False),
        Column("page", Integer, nullable=False, default=1),
        Column("content", Text, nullable=False),
        Column("embedding", VECTOR(EMBEDDING_DIMENSIONS), nullable=False),
        Index(
            "ix_knowledge_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
except ImportError:
    KNOWLEDGE_CHUNKS = None


def _chunk_document(content: str, chunk_size: int = 900, overlap: int = 120) -> list[tuple[int, str]]:
    normalized = re.sub(r"\s+", " ", content).strip()
    if not normalized:
        return []

    chunks: list[tuple[int, str]] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk = normalized[start:end].strip()
        page_match = re.search(r"\bPage\s+(\d+)\b", chunk, flags=re.IGNORECASE)
        chunks.append((int(page_match.group(1)) if page_match else 1, chunk))
        if end >= len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _embed(content: str, task: str) -> list[float]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    if EMBEDDING_MODEL == "gemini-embedding-2":
        prefixes = {
            "RETRIEVAL_QUERY": "task: search result | query: ",
            "QUESTION_ANSWERING": "task: question answering | query: ",
            "RETRIEVAL_DOCUMENT": "",
        }
        content = f"{prefixes.get(task, '')}{content}"
        config = types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS)
    else:
        config = types.EmbedContentConfig(
            task_type=task,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        )
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=content,
        config=config,
    )
    return list(response.embeddings[0].values)


def initialize_vector_store(db: Session) -> bool:
    global VECTOR_SCHEMA_READY
    if database_backend() != "postgresql" or KNOWLEDGE_CHUNKS is None:
        VECTOR_SCHEMA_READY = False
        return False
    try:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
        VECTOR_METADATA.create_all(bind=db.get_bind(), checkfirst=True)
        VECTOR_SCHEMA_READY = True
    except Exception:
        db.rollback()
        VECTOR_SCHEMA_READY = False
    return VECTOR_SCHEMA_READY


def index_document(db: Session, document: KnowledgeDocument) -> int:
    if not VECTOR_SCHEMA_READY and not initialize_vector_store(db):
        return 0

    chunks = _chunk_document(document.content)
    if not chunks:
        return 0

    try:
        db.execute(KNOWLEDGE_CHUNKS.delete().where(KNOWLEDGE_CHUNKS.c.document_id == document.id))
        rows = []
        for page, chunk in chunks:
            embedding = _embed(
                f"title: {document.title} | text: {chunk}",
                "RETRIEVAL_DOCUMENT",
            )
            rows.append(
                {
                    "document_id": document.id,
                    "title": document.title,
                    "source_type": document.source_type,
                    "page": page,
                    "content": chunk,
                    "embedding": embedding,
                }
            )
        db.execute(KNOWLEDGE_CHUNKS.insert(), rows)
        db.commit()
        return len(rows)
    except Exception:
        db.rollback()
        return 0


def index_missing_documents(db: Session) -> int:
    if not VECTOR_SCHEMA_READY and not initialize_vector_store(db):
        return 0
    indexed = 0
    existing_ids = set(db.execute(select(KNOWLEDGE_CHUNKS.c.document_id).distinct()).scalars())
    for document in db.query(KnowledgeDocument).all():
        if document.id not in existing_ids:
            count = index_document(db, document)
            if count == 0:
                break
            indexed += count
    return indexed


def vector_search(db: Session, question: str, limit: int = 3) -> list[dict[str, Any]]:
    if not VECTOR_SCHEMA_READY and not initialize_vector_store(db):
        return []
    try:
        query_embedding = _embed(question, "RETRIEVAL_QUERY")
        distance = KNOWLEDGE_CHUNKS.c.embedding.cosine_distance(query_embedding)
        rows = db.execute(
            select(
                KNOWLEDGE_CHUNKS.c.title,
                KNOWLEDGE_CHUNKS.c.source_type,
                KNOWLEDGE_CHUNKS.c.page,
                KNOWLEDGE_CHUNKS.c.content,
                distance.label("distance"),
            )
            .order_by(distance)
            .limit(limit)
        ).all()
        return [
            {
                "title": row.title,
                "source_type": row.source_type,
                "score": round(max(0.0, 1.0 - float(row.distance)), 3),
                "snippet": row.content[:280],
                "page": row.page,
                "retrieval_method": "pgvector cosine similarity",
            }
            for row in rows
        ]
    except Exception:
        db.rollback()
        return []


def vector_store_status() -> dict[str, Any]:
    return {
        "provider": "PostgreSQL pgvector" if VECTOR_SCHEMA_READY else "TF-IDF fallback",
        "schema_ready": VECTOR_SCHEMA_READY,
        "embedding_model": EMBEDDING_MODEL if VECTOR_SCHEMA_READY else None,
        "dimensions": EMBEDDING_DIMENSIONS if VECTOR_SCHEMA_READY else None,
    }

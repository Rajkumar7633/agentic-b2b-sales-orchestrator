"""
Knowledge ingestion and retrieval API.
Provides endpoints to:
- Ingest documents into the KnowledgeDocument/KnowledgeChunk DB tables
- Search the in-memory knowledge service (keyword-based, MVP)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import require_admin
from app.core.security import UserContext, get_current_user
from app.domain.models.models import KnowledgeChunk, KnowledgeDocument
from app.knowledge.rag_engine import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge & RAG"])


# ---- Request/Response schemas (inline, RAG-specific) ----

class KnowledgeIngestRequest(BaseModel):
    title: str
    document_type: str  # PLAYBOOK, PAST_DEAL, RFP, MESSAGING, OUTREACH_TEMPLATE
    content: str
    metadata: dict | None = None


class KnowledgeIngestResponse(BaseModel):
    document_id: str
    title: str
    document_type: str
    chunks_created: int


class KnowledgeSearchResult(BaseModel):
    id: str
    title: str
    category: str
    content: str
    keywords: list[str]


# ---- Endpoints ----

@router.post("/ingest", response_model=KnowledgeIngestResponse)
async def ingest_document(
    body: KnowledgeIngestRequest,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_admin)
):
    """
    Ingest a knowledge document into the DB and chunk it for future retrieval.
    Currently chunks by paragraph (double newline). In production, upgrade to
    semantic chunking + embedding generation.
    """
    doc = KnowledgeDocument(
        tenant_id=user.tenant_id,
        title=body.title,
        document_type=body.document_type,
        content=body.content,
        metadata_json=body.metadata or {}
    )
    db.add(doc)
    await db.flush()  # Get doc.id before adding chunks

    # Chunk by paragraph (MVP — no embeddings yet)
    paragraphs = [p.strip() for p in body.content.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [body.content]

    chunks = []
    for idx, para in enumerate(paragraphs):
        chunk = KnowledgeChunk(
            document_id=doc.id,
            chunk_index=idx,
            chunk_text=para,
            embedding_json=None  # FUTURE: generate vector embedding here
        )
        db.add(chunk)
        chunks.append(chunk)

    # Also add to in-memory knowledge service for immediate search availability
    knowledge_service._knowledge_base.append({
        "id": doc.id,
        "title": body.title,
        "category": body.document_type.lower(),
        "content": body.content,
        "keywords": list(set(body.content.lower().split()))[:20]
    })

    await db.commit()

    return KnowledgeIngestResponse(
        document_id=doc.id,
        title=doc.title,
        document_type=doc.document_type,
        chunks_created=len(chunks)
    )


@router.get("/search", response_model=list[KnowledgeSearchResult])
async def search_knowledge(
    q: str,
    top_k: int = 3,
    user: UserContext = Depends(get_current_user)
):
    """
    Search the knowledge base using keyword matching.
    MVP: TF-IDF style keyword scoring via KnowledgeService.
    FUTURE: Replace with vector similarity search (pgvector).
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

    results = knowledge_service.search(q.strip(), top_k=min(top_k, 10))
    return [
        KnowledgeSearchResult(
            id=r.get("id", "kb_unknown"),
            title=r.get("title", ""),
            category=r.get("category", ""),
            content=r.get("content", ""),
            keywords=r.get("keywords", [])
        )
        for r in results
    ]


@router.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    """List all knowledge documents for this tenant."""
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.tenant_id == user.tenant_id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "document_type": d.document_type,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]

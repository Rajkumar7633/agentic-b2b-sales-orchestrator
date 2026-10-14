import pytest
from httpx import AsyncClient

from app.knowledge.rag_engine import knowledge_service


@pytest.mark.asyncio
async def test_knowledge_service_search():
    results = knowledge_service.search("expansion software")
    assert len(results) > 0
    assert any("expansion" in r["content"].lower() or "playbook" in r["title"].lower() for r in results)


@pytest.mark.asyncio
async def test_knowledge_ingest_and_search_api(client: AsyncClient, auth_headers):
    # Test Ingestion Endpoint
    payload = {
        "title": "NEXORA Scaling Standard Operating Procedure",
        "document_type": "PLAYBOOK",
        "content": "Paragraph 1: Executive playbook for pursuit.\n\nParagraph 2: Detailed guidelines for sales teams."
    }
    response = await client.post("/api/v1/knowledge/ingest", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["chunks_created"] == 2

    # Test Search Endpoint
    search_res = await client.get("/api/v1/knowledge/search?q=guidelines", headers=auth_headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data) > 0

    # Test List Documents Endpoint
    docs_res = await client.get("/api/v1/knowledge/documents", headers=auth_headers)
    assert docs_res.status_code == 200
    docs_data = docs_res.json()
    assert len(docs_data) > 0

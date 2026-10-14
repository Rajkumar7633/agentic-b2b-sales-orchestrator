"""
Knowledge API Extended Tests
Covers search query < 2 error, list_documents endpoint.
"""
import pytest

from app.domain.models.models import KnowledgeDocument, Tenant


@pytest.mark.asyncio
async def test_search_knowledge_short_query_error(client, auth_headers):
    res = await client.get("/api/v1/knowledge/search?q=a", headers=auth_headers)
    assert res.status_code == 400
    assert "Query must be at least 2 characters" in res.json()["detail"]


@pytest.mark.asyncio
async def test_list_documents_endpoint(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    doc = KnowledgeDocument(
        tenant_id="tenant_nexora_default",
        title="Engineering Playbook",
        document_type="PLAYBOOK",
        content="Our engineering process."
    )
    db_session.add_all([tenant, doc])
    await db_session.commit()

    res = await client.get("/api/v1/knowledge/documents", headers=auth_headers)
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 1
    assert docs[0]["title"] == "Engineering Playbook"

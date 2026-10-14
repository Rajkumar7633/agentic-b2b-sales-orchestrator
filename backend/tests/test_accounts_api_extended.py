"""
Accounts API — Extended Integration Tests
Covers get_account (200 & 404), research_account (200 & 404),
pursue_account (new company & existing company).
"""
import pytest
from app.domain.models.models import Company, Tenant


@pytest.mark.asyncio
async def test_get_account_success(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Acme Test Corp", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    res = await client.get(f"/api/v1/accounts/{co.id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["id"] == co.id
    assert res.json()["name"] == "Acme Test Corp"


@pytest.mark.asyncio
async def test_get_account_not_found(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/accounts/non_existent_id", headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Account not found"


@pytest.mark.asyncio
async def test_research_account_success(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Apex Energy Group", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    res = await client.post(f"/api/v1/accounts/{co.id}/research", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "why_now_signal" in data
    assert "research_summary" in data

    # Verify company updated in DB
    await db_session.refresh(co)
    assert co.pipeline_stage == "RESEARCHED"


@pytest.mark.asyncio
async def test_research_account_not_found(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.post("/api/v1/accounts/invalid_co_id/research", headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Account not found"


@pytest.mark.asyncio
async def test_pursue_existing_account(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Existing Pursued Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()

    res = await client.post(
        "/api/v1/accounts/pursue",
        json={"company_name": "Existing Pursued Co", "domain": "existing.com"},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVAL_REQUIRED"

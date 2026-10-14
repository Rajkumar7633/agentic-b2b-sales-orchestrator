"""
Additional APIs Integration Tests
Covers Auth API (success & failed login), Leads API (list & 404/detail),
Outreach API (list & draft).
"""
import pytest
from app.core.security import hash_password
from app.domain.models.models import Company, Lead, OutreachMessage, Tenant, User


@pytest.mark.asyncio
async def test_auth_login_success(client, db_session):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    user = User(
        id="usr_login_001",
        tenant_id="tenant_nexora_default",
        email="test_user@nexora.ai",
        full_name="Test Login",
        hashed_password=hash_password("correct_password"),
        role="ADMIN"
    )
    db_session.add_all([tenant, user])
    await db_session.commit()

    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_user@nexora.ai", "password": "correct_password"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["email"] == "test_user@nexora.ai"


@pytest.mark.asyncio
async def test_auth_login_failure(client, db_session):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    user = User(
        id="usr_login_002",
        tenant_id="tenant_nexora_default",
        email="test_fail@nexora.ai",
        full_name="Test Fail",
        hashed_password=hash_password("correct_password"),
        role="ADMIN"
    )
    db_session.add_all([tenant, user])
    await db_session.commit()

    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_fail@nexora.ai", "password": "wrong_password"}
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_leads_api_list_and_get(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Lead Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    lead = Lead(tenant_id="tenant_nexora_default", company_id=co.id, pipeline_stage="TARGET", fit_score=88)
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)

    # List leads
    res = await client.get("/api/v1/leads", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Get lead by id
    res_get = await client.get(f"/api/v1/leads/{lead.id}", headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == lead.id


@pytest.mark.asyncio
async def test_leads_api_not_found(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/leads/invalid_lead_id", headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Lead not found"


@pytest.mark.asyncio
async def test_outreach_api_list_and_draft(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    om = OutreachMessage(
        tenant_id="tenant_nexora_default",
        lead_id="lead_001",
        channel="LINKEDIN",
        body_text="Test Outreach Body",
        approval_status="PENDING"
    )
    db_session.add_all([tenant, om])
    await db_session.commit()

    # List outreach messages
    res = await client.get("/api/v1/outreach", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Create draft via API
    payload = {
        "company_name": "Outreach Draft Co",
        "contact": {"first_name": "Sarah", "title": "VP Procurement"},
        "why_now_signal": "New $50M project"
    }
    res_draft = await client.post("/api/v1/outreach/draft", json=payload, headers=auth_headers)
    assert res_draft.status_code == 200
    assert "body_text" in res_draft.json()

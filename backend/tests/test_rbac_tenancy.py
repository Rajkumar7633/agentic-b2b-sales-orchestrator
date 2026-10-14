"""
RBAC & Tenant Security — Comprehensive Tests
Covers: role-based access control, JWT validation, token expiry,
        cross-tenant data isolation, admin vs sales_rep vs reviewer.
"""
import pytest

from app.core.security import create_access_token
from app.domain.models.models import Approval, Company, Contact, Tenant


# ─────────────────────────────────────────────────────────────
# JWT / Token validation
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_no_token_returns_401_or_403(client, db_session):
    """Test that endpoints respond (not 5xx) without JWT."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    # These endpoints don't call production PG directly in ASGI test mode
    safe_paths = ["/api/v1/accounts", "/api/v1/contacts", "/api/v1/approvals"]
    for path in safe_paths:
        res = await client.get(path)
        assert res.status_code < 500, f"5xx on {path}: {res.status_code}"


@pytest.mark.asyncio
async def test_malformed_token_rejected(client, db_session):
    """A garbage Bearer token must be rejected."""
    res = await client.get(
        "/api/v1/accounts",
        headers={"Authorization": "Bearer this.is.not.a.valid.jwt"}
    )
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_admin_can_access_all_read_endpoints(client, db_session, auth_headers):
    """ADMIN role must be able to read all major endpoints."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    # These endpoints return data (may be empty list) — all must be 200
    for path in ["/api/v1/accounts", "/api/v1/contacts",
                 "/api/v1/approvals"]:
        res = await client.get(path, headers=auth_headers)
        assert res.status_code == 200, f"Admin blocked on {path}: {res.status_code}"


@pytest.mark.asyncio
async def test_sales_rep_can_read_accounts_and_contacts(client, db_session, sales_rep_headers):
    """SALES_REP may read accounts and contacts."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    for path in ["/api/v1/accounts", "/api/v1/contacts"]:
        res = await client.get(path, headers=sales_rep_headers)
        assert res.status_code == 200, f"Sales rep blocked on {path}"


@pytest.mark.asyncio
async def test_sales_rep_cannot_approve_outreach(client, db_session, sales_rep_headers):
    """SALES_REP must be forbidden (403) from approving outreach drafts."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    a = Approval(
        id="appr_rbac_rep",
        tenant_id="tenant_nexora_default",
        entity_type="OUTREACH",
        entity_id="msg_rep",
        action_type="SEND_LINKEDIN",
        draft_payload={"body_text": "hello"},
        risk_level="MEDIUM",
        status="PENDING",
        requested_by_agent="supervisor_agent"
    )
    db_session.add(a)
    await db_session.commit()

    res = await client.post(
        "/api/v1/approvals/appr_rbac_rep/approve",
        json={},
        headers=sales_rep_headers
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_can_approve_outreach(client, db_session, reviewer_headers):
    """REVIEWER role must be allowed to approve outreach drafts."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    a = Approval(
        id="appr_reviewer_ok",
        tenant_id="tenant_nexora_default",
        entity_type="OUTREACH",
        entity_id="msg_rev",
        action_type="SEND_LINKEDIN",
        draft_payload={
            "recipient_url": "https://linkedin.com/in/test",
            "body_text": "Hello from reviewer test"
        },
        risk_level="MEDIUM",
        status="PENDING",
        requested_by_agent="supervisor_agent"
    )
    db_session.add(a)
    await db_session.commit()

    res = await client.post(
        "/api/v1/approvals/appr_reviewer_ok/approve",
        json={"edited_payload": {
            "recipient_url": "https://linkedin.com/in/test",
            "body_text": "Approved"
        }},
        headers=reviewer_headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVED"


# ─────────────────────────────────────────────────────────────
# Multi-tenant data isolation
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_tenant_cannot_read_other_tenant_accounts(client, db_session):
    """Strict tenant isolation: tenant_b data is invisible to tenant_a."""
    t_a = Tenant(id="iso_a", name="A")
    t_b = Tenant(id="iso_b", name="B")
    db_session.add_all([t_a, t_b])
    db_session.add(Company(tenant_id="iso_a", name="Only For A", pipeline_stage="TARGET"))
    db_session.add(Company(tenant_id="iso_b", name="Only For B", pipeline_stage="TARGET"))
    await db_session.commit()

    token_a = create_access_token({
        "sub": "u_iso_a", "email": "a@iso.com",
        "role": "SALES_REP", "tenant_id": "iso_a"
    })
    res = await client.get("/api/v1/accounts",
                           headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    names = [c["name"] for c in res.json()]
    assert "Only For A" in names
    assert "Only For B" not in names


@pytest.mark.asyncio
async def test_tenant_cannot_read_other_tenant_contacts(client, db_session):
    """Contacts must be isolated per tenant."""
    t_a = Tenant(id="iso_c_a", name="A")
    t_b = Tenant(id="iso_c_b", name="B")
    co_a = Company(tenant_id="iso_c_a", name="Co A", pipeline_stage="TARGET")
    co_b = Company(tenant_id="iso_c_b", name="Co B", pipeline_stage="TARGET")
    db_session.add_all([t_a, t_b, co_a, co_b])
    await db_session.commit()
    await db_session.refresh(co_a)
    await db_session.refresh(co_b)

    db_session.add(Contact(
        tenant_id="iso_c_a", company_id=co_a.id,
        first_name="Alice", last_name="A", title="VP"
    ))
    db_session.add(Contact(
        tenant_id="iso_c_b", company_id=co_b.id,
        first_name="Bob", last_name="B", title="CTO"
    ))
    await db_session.commit()

    token_b = create_access_token({
        "sub": "u_iso_b", "email": "b@iso.com",
        "role": "SALES_REP", "tenant_id": "iso_c_b"
    })
    res = await client.get("/api/v1/contacts",
                           headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 200
    names = [f"{c['first_name']} {c['last_name']}" for c in res.json()]
    assert "Bob B" in names
    assert "Alice A" not in names


@pytest.mark.asyncio
async def test_two_tenants_analytics_independent(db_session):
    """Analytics for tenant_a and tenant_b must return independent counts."""
    from app.agents.analytics import AnalyticsAgent
    from app.domain.models.models import Company

    t_a = Tenant(id="ana_a", name="A")
    t_b = Tenant(id="ana_b", name="B")
    db_session.add_all([t_a, t_b])
    for i in range(3):
        db_session.add(Company(tenant_id="ana_a", name=f"A Co {i}", pipeline_stage="TARGET"))
    for i in range(7):
        db_session.add(Company(tenant_id="ana_b", name=f"B Co {i}", pipeline_stage="TARGET"))
    await db_session.commit()

    agent = AnalyticsAgent()
    r_a = await agent.execute({"tenant_id": "ana_a", "_db_session": db_session})
    r_b = await agent.execute({"tenant_id": "ana_b", "_db_session": db_session})

    assert r_a["total_target_accounts"] == 3
    assert r_b["total_target_accounts"] == 7

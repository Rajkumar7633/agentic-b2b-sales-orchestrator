"""
Approvals API Extended Tests
Covers patch-stale-bodies endpoint, value error handling on approve/reject,
and stale approval expiration.
"""
import pytest
from app.domain.models.models import Approval, Tenant


@pytest.mark.asyncio
async def test_patch_stale_approval_bodies(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    appr = Approval(
        id="appr_stale_body_1",
        tenant_id="tenant_nexora_default",
        entity_type="OUTREACH",
        entity_id="msg_stale",
        action_type="SEND_LINKEDIN",
        draft_payload={
            "first_name": "Marcus",
            "company_name": "Acme Construction",
            "body_text": "Hello, reaching out regarding alignment."
        },
        risk_level="MEDIUM",
        status="PENDING",
        requested_by_agent="supervisor_agent"
    )
    db_session.add_all([tenant, appr])
    await db_session.commit()

    res = await client.post("/api/v1/approvals/patch-stale-bodies", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["patched"] >= 1

    await db_session.refresh(appr)
    assert "Congratulations on Acme Construction" in appr.draft_payload["body_text"]


@pytest.mark.asyncio
async def test_approve_non_existent_returns_400(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.post("/api/v1/approvals/invalid_appr_id/approve", json={}, headers=auth_headers)
    assert res.status_code == 400
    assert "not found" in res.json()["detail"]


@pytest.mark.asyncio
async def test_reject_non_existent_returns_400(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.post("/api/v1/approvals/invalid_appr_id/reject", json={"rejection_reason": "No"}, headers=auth_headers)
    assert res.status_code == 400
    assert "not found" in res.json()["detail"]

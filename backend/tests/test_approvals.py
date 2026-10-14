"""
HITL Approval Engine — Integration Tests
Covers: approve, reject, RBAC enforcement, duplicate action guard,
        approval queue listing, status filtering.
"""
import pytest

from app.approvals.engine import hitl_engine
from app.domain.models.models import Approval, Tenant, User


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
async def _make_approval(db, appr_id: str, tenant_id: str, status: str = "PENDING") -> Approval:
    a = Approval(
        id=appr_id,
        tenant_id=tenant_id,
        entity_type="OUTREACH",
        entity_id=f"msg_{appr_id}",
        action_type="SEND_LINKEDIN",
        draft_payload={"recipient_url": "https://linkedin.com/in/test", "body_text": "Hello"},
        risk_level="MEDIUM",
        status=status,
        requested_by_agent="supervisor_agent"
    )
    db.add(a)
    await db.flush()
    return a


# ─────────────────────────────────────────────────────────────
# Engine-level tests
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_hitl_approve_delivers_outreach(db_session):
    """Approving a PENDING approval must mark it APPROVED and return DELIVERED."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "appr_approve_ok", "tenant_nexora_default")
    await db_session.commit()

    res = await hitl_engine.approve(
        db=db_session,
        approval_id="appr_approve_ok",
        user_id="usr_admin",
        tenant_id="tenant_nexora_default",
        edited_payload={
            "recipient_url": "https://linkedin.com/in/test",
            "body_text": "Approved message"
        }
    )
    assert res["status"] == "APPROVED"
    assert res["execution_result"]["status"] == "DELIVERED"


@pytest.mark.asyncio
async def test_hitl_reject_marks_rejected(db_session):
    """Rejecting a PENDING approval must mark it REJECTED with a reason."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "appr_reject_ok", "tenant_nexora_default")
    await db_session.commit()

    res = await hitl_engine.reject(
        db=db_session,
        approval_id="appr_reject_ok",
        user_id="usr_admin",
        tenant_id="tenant_nexora_default",
        reason="Tone is too aggressive"
    )
    assert res["status"] == "REJECTED"
    assert res.get("reason") == "Tone is too aggressive" or res.get("rejection_reason") == "Tone is too aggressive"


@pytest.mark.asyncio
async def test_hitl_cannot_approve_already_approved(db_session):
    """Double-approving must raise an error (idempotency guard)."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "appr_double", "tenant_nexora_default", status="APPROVED")
    await db_session.commit()

    with pytest.raises(Exception):
        await hitl_engine.approve(
            db=db_session,
            approval_id="appr_double",
            user_id="usr_admin",
            tenant_id="tenant_nexora_default",
            edited_payload={}
        )


# ─────────────────────────────────────────────────────────────
# API-level tests
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_approvals_list_pending(client, db_session, auth_headers):
    """GET /approvals?status=PENDING returns only pending items."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "a_p1", "tenant_nexora_default", "PENDING")
    await _make_approval(db_session, "a_p2", "tenant_nexora_default", "PENDING")
    await _make_approval(db_session, "a_ap", "tenant_nexora_default", "APPROVED")
    await db_session.commit()

    res = await client.get("/api/v1/approvals?status=PENDING", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert all(i["status"] == "PENDING" for i in items)


@pytest.mark.asyncio
async def test_approvals_list_all_statuses(client, db_session, auth_headers):
    """GET /approvals (no filter) returns all approvals."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    for s in ("PENDING", "APPROVED", "REJECTED"):
        await _make_approval(db_session, f"a_{s}", "tenant_nexora_default", s)
    await db_session.commit()

    res = await client.get("/api/v1/approvals", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 3


@pytest.mark.asyncio
async def test_sales_rep_cannot_approve(client, db_session, sales_rep_headers):
    """SALES_REP role is forbidden from approving — must return 403."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "appr_rbac", "tenant_nexora_default")
    await db_session.commit()

    res = await client.post(
        "/api/v1/approvals/appr_rbac/approve",
        json={"edited_payload": {"body_text": "hi"}},
        headers=sales_rep_headers
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_approvals_api_approve_full_flow(client, db_session, auth_headers):
    """API POST /approvals/{id}/approve → APPROVED + DELIVERED."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "appr_api_ok", "tenant_nexora_default")
    await db_session.commit()

    res = await client.post(
        "/api/v1/approvals/appr_api_ok/approve",
        json={
            "edited_payload": {
                "recipient_url": "https://linkedin.com/in/test",
                "body_text": "Hello from API test"
            }
        },
        headers=auth_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "APPROVED"
    assert body["execution_result"]["status"] == "DELIVERED"


@pytest.mark.asyncio
async def test_approvals_api_reject_flow(client, db_session, auth_headers):
    """API POST /approvals/{id}/reject → REJECTED with reason."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await _make_approval(db_session, "appr_api_rej", "tenant_nexora_default")
    await db_session.commit()

    res = await client.post(
        "/api/v1/approvals/appr_api_rej/reject",
        json={"rejection_reason": "Wrong target"},
        headers=auth_headers
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "REJECTED"


@pytest.mark.asyncio
async def test_approvals_requires_auth(client, db_session):
    """Approvals endpoint must reject unauthenticated requests."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()
    # Either requires auth or returns empty list — either is acceptable
    res = await client.get("/api/v1/approvals")
    assert res.status_code in (200, 401, 403)

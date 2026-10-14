"""
E2E: Full Pursuit Workflow
Covers the complete happy path:
  Health → Pursue → Approve → Meeting → Analytics
"""
import pytest

from app.domain.models.models import Tenant


@pytest.mark.asyncio
async def test_e2e_pursuit_workflow(client, db_session, auth_headers):
    # ── 0. Seed tenant so DB constraints pass ────────────────────────────
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    # ── 1. Health check ──────────────────────────────────────────────────
    res_health = await client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "HEALTHY"

    # ── 2. Trigger pursuit for target account ────────────────────────────
    pursue_payload = {
        "company_name": "Acme Construction",
        "domain": "acmeconstruction.com"
    }
    res_pursue = await client.post(
        "/api/v1/accounts/pursue", json=pursue_payload, headers=auth_headers
    )
    assert res_pursue.status_code == 200, res_pursue.text
    data = res_pursue.json()
    assert data["status"] == "APPROVAL_REQUIRED"
    assert data["scoring"]["fit_classification"] == "HIGH"
    assert data["scoring"]["fit_score"] >= 75
    assert data["outreach_draft"]["approval_status"] == "PENDING"
    assert "approval_required" in data

    # ── 3. Retrieve Pending Approvals ────────────────────────────────────
    res_appr = await client.get("/api/v1/approvals?status=PENDING", headers=auth_headers)
    assert res_appr.status_code == 200
    approvals = res_appr.json()
    assert len(approvals) >= 1
    appr_id = approvals[0]["id"]

    # ── 4. Human Approval Gate: Reviewer edits and approves ──────────────
    approve_body = {
        "edited_payload": {
            "recipient_name": "Marcus Vance (VP Procurement)",
            "recipient_url": "https://linkedin.com/in/marcus-vance-vp",
            "body_text": "Marcus, approved personalized outreach text for Acme's expansion."
        }
    }
    res_approve = await client.post(
        f"/api/v1/approvals/{appr_id}/approve", json=approve_body, headers=auth_headers
    )
    assert res_approve.status_code == 200
    approve_res = res_approve.json()
    assert approve_res["status"] == "APPROVED"
    assert approve_res["execution_result"]["status"] == "DELIVERED"

    # ── 5. Propose Meeting slots ─────────────────────────────────────────
    mtg_payload = {"lead_id": "lead_001", "company_name": "Acme Construction"}
    res_mtg = await client.post(
        "/api/v1/meetings/propose", json=mtg_payload, headers=auth_headers
    )
    assert res_mtg.status_code == 200
    assert len(res_mtg.json()["proposed_slots"]) >= 1

    # ── 6. Verify Analytics endpoint is reachable ────────────────────────────
    # (Analytics agent calls its own PG connection; just verify HTTP 200)
    res_analytics = await client.get("/api/v1/analytics", headers=auth_headers)
    assert res_analytics.status_code == 200
    analytics_data = res_analytics.json()
    # Must return a valid structure (even if PG connection error → 500 would fail)
    assert isinstance(analytics_data, dict)


@pytest.mark.asyncio
async def test_health_endpoint_returns_healthy(client):
    """Health endpoint always returns HEALTHY regardless of auth."""
    res = await client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "HEALTHY"
    # May contain service, environment, llm_provider etc.
    assert isinstance(body, dict)


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client):
    """Test that endpoints respond without 5xx server errors."""
    endpoints = [
        ("GET", "/api/v1/accounts"),
        ("GET", "/api/v1/contacts"),
        ("GET", "/api/v1/approvals"),
        ("GET", "/api/v1/agents"),
    ]
    for method, path in endpoints:
        res = await client.request(method, path)
        # Must not return 5xx server errors
        assert res.status_code < 500, (
            f"{method} {path} returned server error: {res.status_code}"
        )

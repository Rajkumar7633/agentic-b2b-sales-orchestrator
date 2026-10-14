from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from app.domain.models.models import Approval


@pytest.mark.asyncio
async def test_hitl_approval_expiration(client: AsyncClient, db_session, auth_headers):
    # Insert a stale PENDING approval created 50 hours ago
    stale_created = datetime.now(timezone.utc) - timedelta(hours=50)
    stale_appr = Approval(
        id="appr_stale_test_001",
        tenant_id="tenant_nexora_default",
        entity_type="OUTREACH",
        entity_id="out_stale",
        action_type="SEND_LINKEDIN",
        draft_payload={"body": "Stale outreach message"},
        risk_level="MEDIUM",
        status="PENDING",
        requested_by_agent="supervisor_agent",
        created_at=stale_created
    )
    db_session.add(stale_appr)
    await db_session.commit()

    # Call GET /approvals — should lazily mark stale approval as EXPIRED
    res = await client.get("/api/v1/approvals", headers=auth_headers)
    assert res.status_code == 200
    approvals = res.json()

    stale_item = next((a for a in approvals if a["id"] == "appr_stale_test_001"), None)
    assert stale_item is not None
    assert stale_item["status"] == "EXPIRED"

    # Attempting to approve an EXPIRED record should return 400 Bad Request
    approve_res = await client.post("/api/v1/approvals/appr_stale_test_001/approve", headers=auth_headers)
    assert approve_res.status_code == 400
    assert "final state" in approve_res.json()["detail"]

import json

import pytest

from app.domain.models.models import Tenant


@pytest.mark.asyncio
async def test_stream_pursuit_execution_endpoint(client, db_session, auth_headers):
    """GET /stream/pursuit returns an SSE stream with sequential agent steps."""
    tenant = Tenant(id="tenant_nexora_default", name="Default Org")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get(
        "/api/v1/stream/pursuit?company_name=Acme+Global&speed=0.001",
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert "text/event-stream" in res.headers.get("content-type", "")

    lines = [line.strip() for line in res.text.split("\n") if line.startswith("data: ")]
    assert len(lines) == 6

    # Verify first step (INIT)
    step1 = json.loads(lines[0].replace("data: ", ""))
    assert step1["step"] == 1
    assert step1["phase"] == "INIT"
    assert step1["agent_id"] == "supervisor_agent"
    assert "Acme Global" in step1["company_name"]

    # Verify fourth step (SCORING)
    step4 = json.loads(lines[3].replace("data: ", ""))
    assert step4["step"] == 4
    assert step4["phase"] == "SCORING"
    assert step4["data"]["icp_fit_score"] >= 90

    # Verify final step (GOVERNANCE HITL)
    step6 = json.loads(lines[5].replace("data: ", ""))
    assert step6["step"] == 6
    assert step6["phase"] == "GOVERNANCE"
    assert step6["progress"] == 100
    assert step6["data"]["requires_review"] is True


@pytest.mark.asyncio
async def test_stream_broadcast_endpoint(client, db_session, auth_headers):
    """POST /stream/broadcast broadcasts an event to dashboard listeners."""
    tenant = Tenant(id="tenant_nexora_default", name="Default Org")
    db_session.add(tenant)
    await db_session.commit()

    payload = {
        "event_type": "PIPELINE_STAGE_CHANGED",
        "data": {"company_id": "comp_100", "new_stage": "WON"},
    }
    res = await client.post("/api/v1/stream/broadcast", json=payload, headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "BROADCASTED"
    assert body["event_type"] == "PIPELINE_STAGE_CHANGED"
